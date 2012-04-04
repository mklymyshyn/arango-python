import logging

from .document import Document
from .exceptions import InvalidCollectionId

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
        return self.connection.get(
            self.COLLECTIONS_LIST_URL
        )

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

    def __repr__(self):
        return "<Collections proxy for {0}>".format(self.connection)


class Collection(object):
    """Represent single collection with certain name"""
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

    def create(self, waitForSync=False):
        # TODO: create collection and provide status
        pass

    def load(self):
        # TODO: send request to load collection in memory
        pass

    def unload(self, name=None):
        pass

    def delete(self):
        pass

    def rename(self, name=None):
        if not name or name == "":
            raise InvalidCollectionId(
                "Please, provide correct collection name"
            )

    def param(self, **params):
        pass

    def truncate(self):
        pass
