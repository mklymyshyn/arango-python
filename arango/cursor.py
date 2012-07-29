import logging

__all__ = ("Cursor",)

logger = logging.getLogger(__name__)


class Cursor(object):
    """API to work with Cursors in ArangoDB.
    I don't see a reason why it shouldn't be a
    common routine to work with AQL.

    Quote from ArangoDB Wiki:
        Note: the server will also destroy abandoned
              cursors automatically after a certain
              server-controlled timeout to
              avoid resource leakage.

    https://github.com/triAGENS/ArangoDB/wiki/HttpCursor
    """
    CREATE_CURSOR_PATH = "/_api/cursor"
    DELETE_CURSOR_PATH = "/_api/cursor/{0}"
    READ_NEXT_BATCH_PATH = "/_api/cursor/{0}"

    def __init__(self, connection, query,
                 count=True, batchSize=None, bindVars=None):
        """
            ``query`` - contains the query string to be executed (mandatory)
            ``count`` - boolean flag that indicates whether the
                        number of documents found should be
                        returned as "count" attribute in the
                        result set (optional). Calculating the
                        "count" attribute might have a performance
                        penalty for some queries so this option
                        is turned off by default.

            ``batchSize`` - maximum number of result documents to be
                            transferred from the server to the client in
                            one roundtrip (optional).
                            If this attribute is not set, a server-controlled
                            default value will be used.
            ``bindVars`` - key/value list of bind parameters (optional).
        """
        self.connection = connection
        self.query = query

        # boolean flag: show count in results or not
        self.count = count

        self.batchSize = batchSize
        self.bindVars = bindVars if \
            isinstance(bindVars, dict) else {}

        # current position in dataset
        self._position = 0

        # ID of Cursor object within databse
        self._cursor_id = None

        # has more batch or not. By default it's true
        # to fetch at least first dataset/response
        self._hasMore = True

        # data from current batch
        self._dataset = []

        # total count of results, extracted from Database
        self._count = None

    def __iter__(self):
        return self

    def next(self):
        """
        Iterator though resultset (lazy)
        """

        self._position += 1

        try:
            return self._dataset.pop(0)
        except IndexError:
            if self._hasMore:
                self.bulk()
                return self.next()

        raise StopIteration

    def bulk(self):
        """
        Getting initial or next bulk of results from Database
        """

        if not self._cursor_id:
            response = self.connection.post(self.CREATE_CURSOR_PATH, data={
                "query": self.query,
                "count": self.count,
                "batchSize": self.batchSize,
                "bindVars": self.bindVars
            })

            self._cursor_id = response.get("id", None)
        else:
            response = self.connection.put(
                self.READ_NEXT_BATCH_PATH.format(self._cursor_id)
            )

        # TODO: handle errors
        self._hasMore = response.get("hasMore", False)
        self._count = response.get("count", None)
        self._dataset = response["result"] if "result" in response else []

    def __repr__(self):
        return "<ArangoDB Cursor Object: %s>" % self.query
