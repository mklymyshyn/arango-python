import logging

from .document import Documents
from .edge import Edges
from .index import Index
from .exceptions import InvalidCollectionId, CollectionIdAlreadyExist, \
    InvalidCollection
from .aql import AQLQuery

logger = logging.getLogger(__name__)

__all__ = ("Collection", "Collections")


class Collections(object):
    """connection) for Collections"""
    COLLECTION_DOCUMENTS, COLLECTION_EDGES = 2, 3
    COLLECTIONS_LIST_URL = "/_api/collection"

    def __init__(self, connection):
        self.connection = connection
        self.collections = {}

    def __call__(self, *args, **kwargs):
        """Return list of collections within current database"""
        response = self.connection.get(self.COLLECTIONS_LIST_URL)

        names = [c.get("name") for c in response.get("collections", [])]

        return names

    def __getattr__(self, name):
        """
        Accessible as property by default.
        """
        return self._collection(name)

    def __getitem__(self, name):
        """
        In case property used internally by ``Collections``
        it's possible to use dict-like interface, for example
        ``.database`` used internally as link to database instance
        but feel free to use dict-like interface to
        create collection with name ``database``: ``voca["database"]``
        """
        return self._collection(name)

    def _collection(self, name):
        """Lazy init of collection"""

        if name in self.collections:
            return self.collections.get(name)

        self.collections[name] = self.collections.get(
            name,
            Collection(connection=self.connection, name=name))

        return self.collections.get(name)

    @property
    def database(self):
        return self.connection.database

    def rename_collection(self, collection, new_name):
        """
        Private method which should be used by ``Collection``
        instance itself.
        """
        if collection is None or \
                not issubclass(collection.__class__, Collection):
            raise InvalidCollection(
                "Object '{0}' is not subclass of "
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

    TYPE_DOCUMENT, TYPE_EDGE = 2, 3

    COLLECTION_DETAILS_PATH = "/_api/collection/{0}/{1}"
    CREATE_COLLECTION_PATH = "/_api/collection"
    DELETE_COLLECTION_PATH = "/_api/collection/{0}"
    LOAD_COLLECTION_PATH = "/_api/collection/{0}/load"
    UNLOAD_COLLECTION_PATH = "/_api/collection/{0}/unload"
    TRUNCATE_COLLECTION_PATH = "/_api/collection/{0}/truncate"
    PROPERTIES_COLLECTION_PATH = "/_api/collection/{0}/properties"
    RENAME_COLLECTION_PATH = "/_api/collection/{0}/rename"

    INFO_ALLOWED_RESOURCES = ["count", "figures"]

    def __init__(self, connection=None, name=None, id=None,
                 createCollection=True, response=None):
        self.connection = connection
        self.name = name
        self.id = id
        self.response = response

        self.createCollection = createCollection
        self.state_fields = ("connection", "name", "id", "createCollector")

        self._documents = None
        self._edges = None
        self._index = None

    def __repr__(self):
        return "<Collection '{0}' for {1}>".format(self.name, self.connection)

    def __eq__(self, obj):
        return obj.name == obj.name

    @property
    def cid(self):
        """
        Get collection name
        """
        return self.name

    @property
    def query(self):
        """
        .. :py:attr::

        Create Query Builder for current collection.

        .. testcode::

                c.test.create()
                c.test.docs.create({"name": "sample"})

                assert len(c.test.query.execute()), 1

        """
        return AQLQuery(
            connection=self.connection,
            collection=self.cid)

    @property
    def index(self):
        """
        Get **Indexes** related to Collection
        """
        if not self._index:
            self._index = Index(self)

        return self._index

    @property
    def documents(self):
        """
        Get :ref:`documents` related to Collection.

        Technically return instance of :ref:`documents proxy` object
        """
        if self._documents is None:
            self._documents = Documents(collection=self)

        return self._documents

    @property
    def edges(self):
        """
        Get :ref:`edges` related to Collection.

        Technically return instance of :ref:`edges proxy` object

        If this method used to query edges (or called with no arguments)
        it may generated exceptions:

            * ``DocumentIncompatibleDataType``

              In case you're not provided ``VERTEX`` of the Edge
              which should be instance or subclass od :ref:`document`

              More about :term:`DocumentIncompatibleDataType`

        """
        if self._edges is None:
            self._edges = Edges(collection=self)

        return self._edges

    @property
    def docs(self):
        """
        Shortcut for `documents` property
        """
        return self.documents

    def info(self, resource=""):
        """
        Get information about collection.
        Information returns **AS IS** as
        raw ``Response`` data
        """
        if resource not in self.INFO_ALLOWED_RESOURCES:
            resource = ""

        return self.connection.get(
            self.COLLECTION_DETAILS_PATH.format(self.name, resource)
        ).data

    def create_edges(self, *args, **kwargs):
        """
        Create new **Edges Collection** - sepcial
        kind of collections to keep information about edges.
        """
        kwargs.update({"type": Collections.COLLECTION_EDGES})
        return self.create(*args, **kwargs)

    def create(self, waitForSync=False,
               type=Collections.COLLECTION_DOCUMENTS, **kwargs):
        """
        Create new **Collection**. You can specify
        ``waitForSync`` argument (boolean) to wait until
        collection will be synced to disk
        """
        params = {"waitForSync": waitForSync,
                  "name": self.name,
                  "type": type}
        params.update(kwargs)

        response = self.connection.post(
            self.CREATE_COLLECTION_PATH,
            data=params)

        if response.status == 200:
            # TODO: update ID/revision for this collection
            return self

        return None

    def count(self):
        """
        Get count of all documents in collection
        """
        response = self.info(resource="count")
        return response.get("count", 0)

    def __len__(self):
        """
        Exactly the same as ``count`` but it's possible
        to use in more convenient way

        .. testcode::

                c.test.create()

                assert c.test.count() == len(c.test)

        """
        return self.count()

    def load(self):
        """
        Load collection into memory
        """
        return self.connection.put(
            self.LOAD_COLLECTION_PATH.format(self.name)
        )

    def unload(self):
        """
        Unload collection from memory
        """
        return self.connection.put(
            self.UNLOAD_COLLECTION_PATH.format(self.name)
        )

    def delete(self):
        """
        Delete collection
        """
        response = self.connection.delete(
            self.DELETE_COLLECTION_PATH.format(self.name)
        )

        if response.status == 200:
            return True

        return False

    def rename(self, name=None):
        """
        Change name of Collection to ``name``.

        Return value is ``bool`` if success or
        error respectively.

        This method may raise exceptions:

            * ``InvalidCollection``

              This one may be generated only in case
              very low-level instantiation of Collection
              and if base collection proxy isn't provided
              More about :term:`InvalidCollection`

            * ``CollectionIdAlreadyExist``

              If Collection with new name already exist
              this exception will be generated.
              More about :term:`CollectionIdAlreadyExist`

            * ``InvalidCollectionId``

              If Collection instantiated but name
              is not defined or not set.
              More about :term:`InvalidCollectionId`

        Sample usage:

        .. testcode::

                c.test.create()

                c.test.rename("test2")
                assert "test2" in c()
        """
        if name is None or name == "":
            raise InvalidCollectionId(
                "Please, provide correct collection name")

        response = self.connection.post(
            self.RENAME_COLLECTION_PATH.format(self.name),
            data={"name": name})

        if not response.is_error:
            # pass new name to connection
            # change current id of the collection
            self.connection.collection.rename_collection(self, name)
            return True

        return False

    def properties(self, **props):
        """
        Set or get collection properties.

        If ``**props`` are empty eq no keyed arguments
        specified then this method return properties for
        current **Collection**.

        Otherwise method will set or update properties
        using values from ``**props``
        """
        url = self.PROPERTIES_COLLECTION_PATH.format(self.name)

        if not props:
            return self.connection.get(url).data

        # update fields which should be updated,
        # keep old fields as is
        origin = self.properties()

        if isinstance(origin, dict):
            origin.update(props)

        return self.connection.put(url, data=origin).data

    def truncate(self):
        """
        Truncate current **Collection**
        """
        return self.connection.put(
            self.TRUNCATE_COLLECTION_PATH.format(self.name))
