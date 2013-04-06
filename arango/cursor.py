import logging

from .document import Document
from .exceptions import AqlQueryError

__all__ = ("Cursor",)

logger = logging.getLogger(__name__)


class Cursor(object):
    """
    Work with **Cursors** in ArangoDB.
    At the moment, it's
    common routine to work with **AQL** from this driver.

    .. note:: the server will also destroy abandoned
              cursors automatically after a certain
              server-controlled timeout to
              avoid resource leakage.

    - ``query`` - contains the query string to be executed (mandatory)
    - ``count`` - boolean flag that indicates whether the
            number of documents found should be
            returned as "count" attribute in the
            result set (optional). Calculating the
            "count" attribute might have a performance
            penalty for some queries so this option
            is turned off by default.

    - ``batchSize`` - maximum number of result documents to be
                transferred from the server to the client in
                one roundtrip (optional).
                If this attribute is not set, a server-controlled
                default value will be used.
    - ``bindVars`` - key/value list of bind parameters (optional).
    - ``wrapper`` - by default it's ``Document.load``
              class, wrap result into
    """
    CREATE_CURSOR_PATH = "/_api/cursor"
    DELETE_CURSOR_PATH = "/_api/cursor/{0}"
    READ_NEXT_BATCH_PATH = "/_api/cursor/{0}"

    def __init__(self, connection, query,
                 count=True, batchSize=None, bindVars=None,
                 wrapper=Document.load):
        self.connection = connection
        self.query = query

        # boolean flag: show count in results or not
        self.count = count
        self.wrapper = wrapper
        self.batchSize = batchSize
        self.bindVars = bindVars if \
            isinstance(bindVars, dict) else {}

        # current position in dataset
        self._position = 0

        # ID of Cursor object within databse
        self._cursor_id = None

        # has more batch or not. By default it's true
        # to fetch at least first dataset/response
        self._has_more = True

        # data from current batch
        self._dataset = []

        # total count of results, extracted from Database
        self._count = 0

    def bind(self, bind_vars):
        """
        Bind variables to the cursor
        """
        self.bindVars = bind_vars
        return self

    def __iter__(self):
        return self

    @property
    def first(self):
        """
        Get first element from resultset
        """
        if not self._dataset:
            self.bulk()

        try:
            return self.wrapper(self.connection, self._dataset[0])
        except IndexError:
            return None

    @property
    def last(self):
        """
        Return last element from ``current bulk``. It's
        **NOT** last result in *entire dataset*.
        """
        if not self._dataset:
            self.bulk()

        try:
            return self.wrapper(self.connection, self._dataset[-1])
        except IndexError:
            return None

    def next(self):
        """
        Iterator though resultset (lazy)
        """

        self._position += 1

        try:
            item = self._dataset.pop(0)
            return self.wrapper(self.connection, item)
        except IndexError:
            if self._has_more:
                self.bulk()
                return self.next()

        raise StopIteration

    __next__ = next

    def bulk(self):
        """
        Getting initial or next bulk of results from Database
        """

        if not self._cursor_id:
            response = self.connection.post(self.CREATE_CURSOR_PATH, data={
                "query": self.query,
                "count": self.count,
                "batchSize": self.batchSize,
                "bindVars": self.bindVars})

            self._cursor_id = response.get("id", None)
        else:
            response = self.connection.put(
                self.READ_NEXT_BATCH_PATH.format(self._cursor_id))

        if response.status not in [200, 201]:
            raise AqlQueryError(
                response.data.get("errorMessage", "Unknown error"),
                num=response.data.get("errorNum", -1),
                code=response.status)

        self._has_more = response.get("hasMore", False)
        self._count = int(response.get("count", 0))
        self._dataset = response["result"] if "result" in response else []

    def __len__(self):
        if not self._cursor_id:
            self.bulk()

        return self._count

    def __repr__(self):
        return "<ArangoDB Cursor Object: {0}>".format(self.query)
