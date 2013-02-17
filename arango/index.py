import logging

from .exceptions import EmptyFields, WrongIndexType

logger = logging.getLogger(__name__)

__all__ = ("Index",)


class Index(object):
    """Interface to work with Indexes"""

    CREATE = "/_api/index/?collection={0}"
    READ = "/_api/index/{1}?collection={0}"
    DELETE = "/_api/index/{1}?collection={0}"
    INDEXES = "/_api/index/?collection={0}"

    GEO, HASH, SKIPLIST = ("geo", "hash", "skiplist")
    INDEX_TYPES = (GEO, HASH, SKIPLIST)

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection
        self.indexes = {}

    def __call__(self):
        """
        Get list of all available indexes. Returns
        tuple with indentyfiers and original response

        .. code::

            ...
            c.test.index()

        """
        response = self.connection.get(
            self.INDEXES.format(self.collection.cid))

        return response.get("identifiers", {})

    def create(self, fields, index_type="hash", unique=False):
        """
        Create new index. By default type is `hash` and
        `unique=False`


        ``fields`` may be either ``str``, ``list`` or ``tuple``.

        This method may generate :term:`WrongIndexType` exception
        in case ``index_type`` isn't allowed for Arango DB
        """

        if not isinstance(fields, (list, tuple)):
            fields = [fields]

        if index_type not in self.INDEX_TYPES:
            raise WrongIndexType(
                "The type you provided `{0}` is undefined. "
                "Possible values are: {1}".format(
                    repr(type),
                    ", ".join(self.INDEX_TYPES)
                )
            )

        if len(fields) == 0:
            raise EmptyFields(
                "It's required to provide at least one field to index"
            )

        response = self.connection.post(
            self.CREATE.format(self.collection.cid),
            data={
                "fields": fields,
                "type": index_type,
                "unique": unique})

        if response.status in [200, 201]:
            self.indexes[response.data["id"]] = response.data
            return self

        return None

    def delete(self, field_id):
        """Return tuple of two values:
            - bool success or not deletion
            - original response
        """
        response = self.connection.delete(
            self.DELETE.format(self.collection.cid, field_id))

        if response.get("code", 500) == 200:
            return True

        return False

    def get(self, field_id, force_read=False):
        """
        Get index by ``id``
        """
        if force_read is False and field_id in self.indexes:
            return self.indexes[field_id]

        response = self.connection.get(
            self.READ.format(self.collection.cid, field_id))

        self.indexes[field_id] = response.data

        return self.indexes[field_id]
