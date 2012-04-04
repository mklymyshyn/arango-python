import logging

logger = logging.getLogger(__name__)


class Document(object):

    waitForSync = True
    path = "/document"

    def __init__(self, collection=None, handle=None, waitForSync=False):
        self._handle = handle
        self.connection = collection.connection
        self.collection = collection
        self.waitForSync = waitForSync

    @property
    def handle(self):
        return self._handle

    def create(self, handle=None, waitForSync=None, **kwargs):
        params = {
            "collection": self.collection.handle or self.collection.name,
            "waitForSync": waitForSync or self.waitForSync,
            "createCollection": self.collection.createCollection
        }

        self.connection.post(
            self.path,
            params
        )

    def update(self, handle=None):
        self.connection.put(
            self.path
        )

    def delete(self, handle=None):
        self.connection.delete(
            self.path
        )
