import logging

from .document import Document
from .exceptions import InvalidCollectionId, CollectionIdAlreadyExist, \
                        InvalidCollection


logger = logging.getLogger(__name__)

__all__ = ("Collection", "Collections")


class Collections(object):
    """connection) for Collections"""

    COLLECTIONS_LIST_URL = "/_api/collection"

    def __init__(self, connection):
        self.connection = connection
        self.collections = {}

    def __call__(self, *args, **kwargs):
        """Return list of collections within current database"""
        response = self.connection.get(
            self.COLLECTIONS_LIST_URL
        )

        names = [c.get("name") for c in response.get("collections", [])]
        return names, response

    def __getattr__(self, name):
        """Lazy init of collection"""

        if name in self.collections:
            return self.collections.get(name)

        self.collections.update({
            name: self.collections.get(
                name,
                Collection(
                    connection=self.connection,
                    name=name
                )
            )
        })

        return self.collections.get(name)

    def rename_collection(self, collection, new_name):
        if collection is None or \
                not issubclass(collection.__class__, Collection):
            raise InvalidCollection(
                "Object '{0}' is not subclass of "\
                "Collection or is None".format(repr(collection))
            )

        if new_name in self.collections:
            raise CollectionIdAlreadyExist(
                "Collection with name '{0}' already exist".format(new_name)
            )

        if not collection.cid in self.collections:
            self.collections[collection.cid] = collection

        old_name = collection.cid
        collection.name = new_name
        self.collections[new_name] = collection
        del self.collections[old_name]

    def __repr__(self):
        return "<Collections proxy for {0}>".format(self.connection)


class Collection(object):
    """Represent single collection with certain name"""

    COLLECTION_DETAILS_PATH = "/_api/collection/{0}/{1}"
    CREATE_COLLECTION_PATH = "/_api/collection"
    DELETE_COLLECTION_PATH = "/_api/collection/{0}"
    LOAD_COLLECTION_PATH = "/_api/collection/{0}/load"
    UNLOAD_COLLECTION_PATH = "/_api/collection/{0}/unload"
    TRUNCATE_COLLECTION_PATH = "/_api/collection/{0}/truncate"
    PARAM_COLLECTION_PATH = "/_api/collection/{0}/parameter"
    RENAME_COLLECTION_PATH = "/_api/collection/{0}/rename"

    INFO_ALLOWED_RESOURCES = ["count", "figures"]

    def __init__(self, connection=None, name=None, id=None,
            createCollection=True):
        self.connection = connection
        self.name = name
        self._id = id
        self.createCollection = createCollection

    def __repr__(self):
        return "<Collection '{0}' for {1}>".format(self.name, self.connection)

    @property
    def cid(self):
        return self.name

    @property
    def document(self):
        return Document(collection=self)

    @property
    def d(self):
        return self.document

    def info(self, resource=""):
        if resource not in self.INFO_ALLOWED_RESOURCES:
            resource = ""

        return self.connection.get(
            self.COLLECTION_DETAILS_PATH.format(self.name, resource)
        )

    def create(self, waitForSync=False):
        return self.connection.post(
            self.CREATE_COLLECTION_PATH,
            data=dict(
                waitForSync=waitForSync,
                name=self.name
            )
        )

    def count(self):
        response = self.info(resource="count")
        return response.get("count", 0)

    def __len__(self):
        return self.count()

    def load(self):
        return self.connection.put(
            self.LOAD_COLLECTION_PATH.format(self.name)
        )

    def unload(self, name=None):
        return self.connection.put(
            self.UNLOAD_COLLECTION_PATH.format(self.name)
        )

    def delete(self):
        return self.connection.delete(
            self.DELETE_COLLECTION_PATH.format(self.name)
        )

    def rename(self, name=None):
        if name is None or name == "":
            raise InvalidCollectionId(
                "Please, provide correct collection name"
            )

        response = self.connection.put(
            self.RENAME_COLLECTION_PATH.format(self.name),
            data=dict(name=name)
        )

        if not response.is_error:
            # pass new name to connection
            # change current id of the collection
            self.connection.collection.rename_collection(self, name)

        return response

    def param(self, **params):
        action = "get" if params == {} else "put"

        return getattr(self.connection, action)(
            self.PARAM_COLLECTION_PATH.format(self.name),
            data=params
        )

    def truncate(self):
        return self.connection.put(
            self.TRUNCATE_COLLECTION_PATH.format(self.name)
        )
