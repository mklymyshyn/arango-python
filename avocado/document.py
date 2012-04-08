import logging

from .exceptions import DocumentAlreadyCreated, \
                        DocumentIncompatibleDataType

logger = logging.getLogger(__name__)


class Document(object):

    DOCUMENT_PATH = "/document"
    DELETE_DOCUMENT_PATH = "/document/{0}"
    UPDATE_DOCUMENT_PATH = "/document/{0}"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

        self._body = None
        self._id = None
        self._rev = None

    @property
    def id(self):
        return self._id

    @property
    def rev(self):
        return self._rev

    def __getitem__(self, name):
        """Get element by dict-like key"""
        return self.get(name)

    def __setitem__(self, name, value):
        """Get element by dict-like key"""

        self._body[name] = value

    @property
    def doc(self):
        """Return whole document"""
        return self.get()

    def get(self, name=None, default=None):
        """Getter for body"""

        if not self._body:
            return default

        if isinstance(self._body, (list, tuple)) and \
            isinstance(name, int):
            return self._body[name]

        if isinstance(self._body, (list, tuple)) or name == None:
            return self._body

        return self._body.get(name, default)

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
                self.DOCUMENT_PATH,
                **params
            ),
            data=body
        )

        # define document ID
        if response.get("code", 500) in [201, 202]:
            self._id = response.get("_id")
            self._rev = response.get("_rev")
            self._body = body

        return self, response

    def update(self, newData, save=True, **kwargs):
        if issubclass(type(self._body), dict) and \
                issubclass(type(newData), dict):
            self._body.update(newData)
        elif issubclass(type(self._body), list) and \
                issubclass(type(newData), list):
            self._body.extend(newData)
        else:
            raise DocumentIncompatibleDataType(
                "You trying to update document `{0}` with "\
                "incompatible datat type {1}".format(
                    self.id,
                    repr(newData)
                )
            )

        if save == True:
            return self.save(**kwargs)

        return True

    def save(self):
        response = self.connection.put(
            self.UPDATE_DOCUMENT_PATH.format(self.id),
            data=self.doc
        )

        # update revision of the document
        if response.get("code", 500) in [201, 202]:
            self._rev = response.get("_rev")

        return response

    def delete(self):
        response = self.connection.delete(
            self.DELETE_DOCUMENT_PATH.format(self.id)
        )

        if response.get("code", 500) == 204:
            self._id = None
            self._rev = None
            self._body = None

        return response
