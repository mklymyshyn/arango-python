import logging

from .document import Documents
from .edge import Edges
from .index import Index
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

        return names

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
        """
        Private method which should be used by ``Collection``
        instance itself.
        """
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
    PARAM_COLLECTION_PATH = "/_api/collection/{0}/properties"
    RENAME_COLLECTION_PATH = "/_api/collection/{0}/rename"

    INFO_ALLOWED_RESOURCES = ["count", "figures"]

    def __init__(self, connection=None, name=None, id=None,
            createCollection=True):
        self.connection = connection
        self.name = name
        self._id = id

        self.createCollection = createCollection

        self._documents = None
        self._edges = None
        self._index = None
        self._response = None

    def __repr__(self):
        return "<Collection '{0}' for {1}>".format(self.name, self.connection)

    @property
    def cid(self):
        return self.name

    @property
    def index(self):
        if not self._index:
            self._index = Index(self)

        return self._index

    @property
    def documents(self):
        if not self._documents:
            self._documents = Documents(collection=self)

        return self._documents

    @property
    def edges(self):
        if self._edges == None:
            self._edges = Edges(collection=self)

        return self._edges

    @property
    def response(self):
        return self._response

    @property
    def docs(self):
        return self.documents

    def info(self, resource=""):
        if resource not in self.INFO_ALLOWED_RESOURCES:
            resource = ""

        return self.connection.get(
            self.COLLECTION_DETAILS_PATH.format(self.name, resource)
        )

    def create(self, waitForSync=False):
        response = self.connection.post(
            self.CREATE_COLLECTION_PATH,
            data=dict(
                waitForSync=waitForSync,
                name=self.name
            )
        )

        self._response = response

        if response.status == 200:
            return self

        return None

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
        response = self.connection.delete(
            self.DELETE_COLLECTION_PATH.format(self.name)
        )

        self._response = response

        if response.status == 200:
            return True

        return False

    def rename(self, name=None):
        """
        Change name of Collection to ``name``

        .. code::

                from arango import create
                c = create()

                c.test.create()

                c.test.rename("test2")
                assert "test2" in c()
        """
        if name is None or name == "":
            raise InvalidCollectionId(
                "Please, provide correct collection name"
            )

        response = self.connection.put(
            self.RENAME_COLLECTION_PATH.format(self.name),
            data=dict(name=name)
        )

        self._response = response

        if not response.is_error:
            # pass new name to connection
            # change current id of the collection
            self.connection.collection.rename_collection(self, name)
            return True

        return False

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
