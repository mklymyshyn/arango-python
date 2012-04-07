import logging

logger = logging.getLogger(__name__)


class Document(object):

    CREATE_DOCUMENT_PATH = "/document"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

        self._handle = None

    @property
    def handle(self):
        return self._handle

    def create(self, body, createCollection=False):
        params = dict(collection=self.collection.cid)

        if createCollection == True:
            params.update(dict(createCollection=True))

        return self.connection.post(
            self.connection.qs(
                self.CREATE_DOCUMENT_PATH,
                **params
            ),
            data=body
        )

    def update(self, handle=None):
        self.connection.put(
            self.path
        )

    def delete(self, handle=None):
        self.connection.delete(
            self.path
        )
