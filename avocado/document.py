import logging

from .exceptions import DocumentAlreadyCreated

logger = logging.getLogger(__name__)


class Document(object):

    CREATE_DOCUMENT_PATH = "/document"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

        self._body = None
        self._id = None

    @property
    def id(self):
        return self._id

    def get(self, _id, default=None):
        """Getter for body"""
        if isinstance(self._body, (list, tuple)):
            return self._body

        return self._body.get(_id, default)

    def create(self, body, createCollection=False):
        if self.id is not None:
            raise DocumentAlreadyCreated(
                "This document already created with id {0}".format(self.id)
            )

        params = dict(collection=self.collection.cid)

        if createCollection == True:
            params.update(dict(createCollection=True))

        response = self.connection.post(
            self.connection.qs(
                self.CREATE_DOCUMENT_PATH,
                **params
            ),
            data=body
        )

        # define document ID
        if response.get("code", 500) in [201, 202]:
            self._id = response.get("_id")

        return self, response

    def update(self, handle=None):
        self.connection.put(
            self.path
        )

    def delete(self, handle=None):
        self.connection.delete(
            self.path
        )
