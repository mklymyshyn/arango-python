import logging

from .exceptions import EmptyFields, WrongIndexType

logger = logging.getLogger(__name__)

__all__ = ("Index",)


class Index(object):
    """Interface to work with Indexes"""

    CREATE = "/_api/index/{0}"
    READ = "/_api/index/{0}/{1}"
    DELETE = "/_api/index/{0}/{1}"
    INDEXES = "/_api/index/{0}"

    GEO, HASH, SKIPLIST = ("geo", "hash", "skiplist")
    INDEX_TYPES = (GEO, HASH, SKIPLIST)

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

    def __call__(self):
        """Get list of all available indexes. Returns
        tuple with indentyfiers and original response"""
        response = self.connection.get(
            self.INDEXES.format(self.collection.cid)
        )

        return response.get("identifiers", {}), response

    def create(self, fields, type="hash", unique=False):
        """Create new index. By default type is `hash` and
        `unique=False`"""

        if type not in self.INDEX_TYPES:
            raise WrongIndexType(
                "The type you provided `{0}` is undefined. "\
                "Possible values are: {1}".format(
                    repr(type),
                    ", ".join(self.INDEX_TYPES)
                )
            )

        if len(fields) == 0:
            raise EmptyFields(
                "It's required to provide at least one field to index"
            )

        return self.connection.post(
            self.CREATE.format(self.collection.cid),
            data=dict(
                fields=fields,
                type=type,
                unique=unique
            )
        )

    def delete(self, id):
        """Return tuple of two values:
            - bool success or not deletion
            - original response
        """
        response = self.connection.delete(
            self.DELETE.format(self.collection.cid, id)
        )

        if response.get("code", 500) == 200:
            return True, response

        return False, response

    def get(self, id):
        return self.connection.get(
            self.READ.format(self.collection.cid, id)
        )
