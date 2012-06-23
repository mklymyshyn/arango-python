import logging

from .mixins import ComparsionMixin, LazyLoadMixin
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
        return self.count

    @property
    def count(self):
        """
        Get count of all documents in :ref:`collection`
        """
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
        logger.error("XXX: %r" % doc_urls)
        if rs._limit != None:
            doc_urls = doc_urls[:rs._limit]

        rs.data = doc_urls

    def iterate(self, rs):
        """This method will be called within Resultset so
        it should get list of document"""

        #import ipdb; ipdb.set_trace()
        for url in rs.data or []:
            yield Document(
                collection=self.collection,
                resource_url=url
            )

    def create(self, *args, **kwargs):
        """
        Shortcut for new documents creation
        """
        doc = Document(collection=self.collection)
        return doc.create(*args, **kwargs)

    def _reach_reference(self, ref_or_document):
        """
        Reach reference by type
        """
        if issubclass(type(ref_or_document), Document):
            ref = ref_or_document.id
        else:
            ref = ref_or_document

        return ref

    def delete(self, ref_or_document):
        """
        Delete document shorcut

        ``ref_or_document`` may be either plai reference or
        Document instance

        """

        doc = Document(
            collection=self.collection,
            id=self._reach_reference(ref_or_document)
        )
        return doc.delete()

    def update(self, ref_or_document, *args, **kwargs):
        """
        Update document

        ``ref_or_document`` may be either plai reference or
        Document instance
        """
        doc = Document(
            collection=self.collection,
            id=self._reach_reference(ref_or_document)
        )
        return doc.update(*args, **kwargs)


class Document(ComparsionMixin, LazyLoadMixin):
    """Particular instance of Document"""

    DOCUMENT_PATH = "/_api/document"
    DELETE_DOCUMENT_PATH = "/_api/document/{0}"
    UPDATE_DOCUMENT_PATH = "/_api/document/{0}"
    READ_DOCUMENT_PATH = "/_api/document/{0}"

    LAZY_LOAD_HANDLERS = ["id", "rev", "body", "get", "update", "delete"]
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

        self._lazy_loaded = True

        if id != None or resource_url != None:
            self._lazy_loaded = False

        self._response = None

    @property
    def id(self):
        """
        Id of the :ref:`Document` instance
        """
        return self._id

    @property
    def rev(self):
        """
        Revision of the :ref:`Document` instance
        """
        if not self._rev and self._id != None:
            self._rev = self._id.split("/")[1]

        return self._rev

    @property
    def response(self):
        """Method to get latest response"""
        return self._response

    def lazy_loader(self):
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
                "Sorry, document with handle `{0}` "\
                "not exist in database".format(self._id)
            )

        self._body = response.data

        if isinstance(response.data, dict):
            self._id = response.data.get("_id", self._id)
            self._rev = response.data.get("_rev", self._rev)

        self._response = response

        return self

    def __getitem__(self, name):
        """Get element by dict-like key"""
        return self.get(name)

    def __setitem__(self, name, value):
        """Set element by dict-like key"""

        self._body[name] = value

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

    @body.setter
    def body(self, value):
        """
        Setter for document body
        """
        self._body = value

    def get(self, name=None, default=None):
        """
        This method very similar to ``dict``'s ``get`` method.
        The difference is that *default* value should be specified
        explicitly.

        To get specific value for specific key in body use and default
        *(fallback)* value ``0``::

            document.get(name="sample_key", default=0)
        """

        if not self._body:
            return default

        if isinstance(self._body, (list, tuple)) and \
            isinstance(name, int):
            return self._body[name]

        if isinstance(self._body, (list, tuple)) or name == None:
            return self._body

        return self._body.get(name, default)

    def create(self, body, createCollection=False, **kwargs):
        """
        Method to create new document.

        Possible arguments: :term:`waitForSync`

        Read more about additional arguments  :term:`Documents REST Api`

        This method may raise :term:`DocumentAlreadyCreated` exception in
        case document already created.

        Return document instance (``self``) or ``None``
        """

        if self._id != None:
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

        if response.status in [200, 201, 202]:
            self._id = response.get("_id")
            self._rev = response.get("_rev")
            self._body = body
            return self

        return None

    def update(self, newData, save=True, **kwargs):
        """
        Method to update document.

        This method is **NOT** for overwriting document body.
        In case document is ``list`` it will **extend** current
        document body. In case it's ``dict`` - **update** document body
        with new data.

        To overwrite document body use ``body`` setter.

        In case ``save`` argument set to ``False`` document will not be
        updated until ``save()`` method will be called.

        This method may raise :term:`EdgeNotYetCreated` exception
        in case you trying to update edge which is not saved yet.

        Exception :term:`DocumentIncompatibleDataType` will be raised
        in case body of the document isn't either ``dict`` or ``list``.
        """

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

    def save(self, **kwargs):
        """
        Method to force save of the document.

        ``kwargs`` will be passed directly to ``requests``
        arguments.
        """

        response = self.connection.put(
            self.UPDATE_DOCUMENT_PATH.format(self.id),
            data=self.body,
            **kwargs
        )

        self._response = response

        # update revision of the document
        if response.status in [201, 202]:
            self._rev = response.get("_rev")
            return self

        return None

    def delete(self):
        """
        Delete current document.

        Return ``True`` if success and ``False`` if not
        """
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
