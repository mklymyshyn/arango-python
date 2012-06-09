import logging

from .comparsion import ComparsionMixin
from .exceptions import DocumentAlreadyCreated, \
                        DocumentIncompatibleDataType, \
                        DocumentNotFound


logger = logging.getLogger(__name__)


__all__ = ("Documents", "Document",)


class Documents(object):
    """Proxy object to handle work with
    documents within collection instance
    """

    DOCUMENTS_PATH = "/_api/document?collection={0}"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

    def __call__(self, *args, **kwargs):
        from .core import Resultset

        return Resultset(self)

    def __repr__(self):
        return "<ArangoDB Documents Proxy Object>"

    def __len__(self):
        return self.count()

    def count(self):
        response = self.connection.get(
            self.DOCUMENTS_PATH.format(self.collection.cid)
        )
        return len(response.get("documents", []))

    def prepare_resultset(self, rs, args=None, kwargs=None):
        response = self.connection.get(
            self.DOCUMENTS_PATH.format(self.collection.cid)
        )

        doc_urls = response.get("documents", [])[rs._offset:]

        rs.response = response
        rs.count = len(doc_urls)
        if rs._limit != None:
            doc_urls = doc_urls[:rs._limit]

        rs.data = doc_urls

    def query(self, rs):
        """This method will be called within Resultset so
        it should get list of document"""

        for url in rs.data:
            yield Document(
                collection=self.collection,
                resource_url=url
            )

    def create(self, *args, **kwargs):
        doc = Document(collection=self.collection)
        return doc.create(*args, **kwargs)

    def delete(self, ref):
        """Delete document by reference"""

        doc = Document(collection=self.collection, id=ref)
        return doc.delete()

    def update(self, ref, *args, **kwargs):
        """Update document by reference"""
        doc = Document(collection=self.collection, id=ref)
        return doc.update(*args, **kwargs)


class Document(ComparsionMixin):
    """Particular instance of Document"""

    DOCUMENT_PATH = "/_api/document"
    DELETE_DOCUMENT_PATH = "/_api/document/{0}"
    UPDATE_DOCUMENT_PATH = "/_api/document/{0}"
    READ_DOCUMENT_PATH = "/_api/document/{0}"

    LAZY_LOAD_HANDLERS = ['id', 'rev', 'body', 'get', 'update', 'delete']
    IGNORE_KEYS = set(["_rev", "_id"])

    def __init__(self, collection=None, id=None, resource_url=None):
        """You have to specify collection and you *may* specify either:
         - documents id
         - document resource URL
        """
        self.connection = collection.connection
        self.collection = collection

        self._body = None
        self._id = id
        self._rev = None
        self._resource_url = resource_url

        self._fetch_lazy = id != None or resource_url != None

        self._response = None

    @property
    def id(self):
        return self._id

    @property
    def response(self):
        """Method to get latest response"""
        return self._response

    @property
    def rev(self):
        return self._rev

    def fetch(self):
        # TODO: maybe need to deal with `etag`

        if self._resource_url != None:
            # FIXME: here I have to parse reference from
            # URL which isn't cool

            # NB: This appropriate only for key/value or
            # lists, if document body is object then
            # everything is ok
            chunks = self._resource_url.split("/")
            self._id = "{0}/{1}".format(chunks[-2], chunks[-1])
            self._rev = chunks[-1]

            response = self.connection.get(
                self._resource_url,
                _expect_raw=True)
        else:
            response = self.connection.get(
                self.READ_DOCUMENT_PATH.format(self._id),
                _expect_raw=True
            )

        if response.status != 200:
            raise DocumentNotFound(
                "Sorry, document with handle {0}"\
                "not exist in database".format(self._id)
            )

        self._body = response.data

        self._id = response.data.get("_id", self._id)
        self._rev = response.data.get("_rev", self._rev)

        self._response = response

        return self

    def __getitem__(self, name):
        """Get element by dict-like key"""
        return self.get(name)

    def __setitem__(self, name, value):
        """Get element by dict-like key"""

        self._body[name] = value

    def __getattribute__(self, name):
        """Fetching lazy document"""
        if name in object.__getattribute__(self, "LAZY_LOAD_HANDLERS"):
            object.__getattribute__(self, "_handle_lazy")()

        try:
            return object.__getattribute__(self, name)
        except KeyError:
            raise AttributeError

    def __repr__(self):
        self._handle_lazy()
        return "<ArangoDB Document: Reference {0}, Rev: {1}>".format(
            self._id,
            self._rev
        )

    @property
    def body(self):
        """Return whole document"""
        return self.get()

    def _handle_lazy(self):
        if self._fetch_lazy:
            self.fetch()
            self._fetch_lazy = False

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

    def create(self, body, createCollection=False, **kwargs):
        if self.id is not None:
            raise DocumentAlreadyCreated(
                "This document already created with id {0}".format(self.id)
            )

        params = dict(collection=self.collection.cid)

        if createCollection == True:
            params.update(dict(createCollection=True))

        params.update(kwargs)

        response = self.connection.post(
            self.connection.qs(
                self.DOCUMENT_PATH,
                **params
            ),
            data=body
        )

        # define document ID
        self._response = response

        #import ipdb; ipdb.set_trace()
        if response.status in [200, 201, 202]:
            self._id = response.get("_id")
            self._rev = response.get("_rev")
            self._body = body
            return self

        return None

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
            data=self.body
        )

        self._response = response

        # update revision of the document
        if response.status in [201, 202]:
            self._rev = response.get("_rev")
            return self

        return None

    def delete(self):
        response = self.connection.delete(
            self.DELETE_DOCUMENT_PATH.format(self.id)
        )

        self._response = response

        if response.status == 200:
            self._id = None
            self._rev = None
            self._body = None
            return True

        return False
