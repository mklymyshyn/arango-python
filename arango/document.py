import logging

from .mixins import ComparsionMixin, LazyLoadMixin
from .exceptions import DocumentAlreadyCreated, \
    DocumentIncompatibleDataType, DocumentNotFound, \
    DocuemntUpdateError
from .utils import proxied_document_ref, parse_meta
from .utils import json

__all__ = ("Documents", "Document",)

logger = logging.getLogger(__name__)


class Documents(object):
    """Proxy object to handle work with
    documents within collection instance
    """

    DOCUMENTS_PATH = "/_api/document?collection={0}"
    BULK_INSERT_PATH = "/_api/import"

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

        cursor = self.connection.query(
            "FOR d IN {} RETURN d".format(
                self.collection.cid),
            count=True)
        return len(cursor)

    def _cursor(self, rs):
        return self.connection.query(
            "FOR d IN {} {} RETURN d".format(
                self.collection.cid, self._limits(rs)),
            count=True)

    def _limits(self, rs):
        limit = ""

        if rs._limit:
            limit = "LIMIT {}".format(rs._limit)

            if rs._offset:
                limit = "LIMIT {}, {}".format(
                    rs._offset, rs._limit)

        return limit

    def iterate(self, rs):
        """This method will be called within Resultset so
        it should get list of document"""

        for doc in self._cursor(rs):
            yield doc

    def create(self, *args, **kwargs):
        """
        Shortcut for new documents creation
        """
        doc = Document(
            collection=self.collection,
            connection=self.connection)
        return doc.create(*args, **kwargs)

    def create_bulk(self, docs, batch=100):
        """
        Insert bulk of documents using **HTTP Interface for bulk imports**.

        .. testcode::

            docs = [
                {"name": "doc1"},
                {"name": "doc2"},
                {"name": "doc3"}]
            response = c.test.documents.create_bulk(docs)

            assert response == {
                u'created': 3, u'errors': 0,
                u'empty': 0, u'error': False}, "Docs are not created"

        Actually, it's possible to use **Headers and values import**
        in this call (and first element in ``docs`` have
        to be attribute names and every element in ``docs`` array
        have to be list). In this case you don't need to pass
        key/value pair for every document.

        .. testcode::

            docs = [
                ["name"],
                ["doc1"],
                ["doc2"],
                ["doc3"]]
            response = c.test.documents.create_bulk(docs)

            assert response == {
                u'created': 3, u'errors': 0,
                u'empty': 0, u'error': False}, "Docs are not created"

        """

        # if no documents provided
        if not docs:
            return False

        qs_args = {
            "createCollection": "true",
            "collection": self.collection.cid}

        # if there's no headers/values import
        if not isinstance(docs[0], (list, tuple)):
            qs_args["type"] = "documents"  # we do not want to use array here!

        response = self.connection.post(
            self.connection.qs(self.BULK_INSERT_PATH, **qs_args),
            data=u"\n".join(json.dumps(doc) for doc in docs),
            ignore_request_args=True)

        # update revision of the document
        if response.status == 201:
            return response.data

        return False

    def delete(self, ref_or_document):
        """
        Delete document shorcut

        ``ref_or_document`` may be either plai reference or
        Document instance

        """

        doc = Document(
            collection=self.collection,
            connection=self.connection,
            id=proxied_document_ref(ref_or_document)
        )
        return doc.delete()

    def update(self, ref_or_document, *args, **kwargs):
        """
        Update document

        ``ref_or_document`` may be either plain reference or
        Document instance
        """
        if not issubclass(type(ref_or_document), Document):
            doc = Document.load(self.connection, id=ref_or_document)
        else:
            doc = ref_or_document

        return doc.update(*args, **kwargs)

    def load(self, doc_id):
        """
        Load particular document by id ``doc_id``.

        **Example:**

        .. testcode::

            doc_id = c.test.documents.create({"x": 2}).id
            doc = c.test.documents.load(doc_id)

            assert doc.body["x"] == 2

        """
        return Document.load(self.connection, id=doc_id)


class Document(ComparsionMixin, LazyLoadMixin):
    """Particular instance of Document"""

    DOCUMENT_PATH = "/_api/document"
    DELETE_DOCUMENT_PATH = "/_api/document/{0}"
    UPDATE_DOCUMENT_PATH = "/_api/document/{0}"
    READ_DOCUMENT_PATH = "/_api/document/{0}"

    LAZY_LOAD_HANDLERS = ["id", "rev", "body", "get", "update", "delete"]
    IGNORE_KEYS = set(["_rev", "_id", "_key"])

    def __init__(self, collection=None,
                 id=None, rev=None,
                 resource_url=None, connection=None):
        """You have to specify collection and you *may* specify either:
         - documents id
         - document resource URL
        """
        self.connection = connection
        self.collection = collection

        self._body = None
        self._id = id
        self._rev = rev or None
        self._resource_url = resource_url

        self._lazy_loaded = True

        if id is not None or resource_url is not None:
            self._lazy_loaded = False

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
        return self._rev

    @classmethod
    def wrap(cls, connection, item):
        doc = cls(connection=connection,
                  id=item.get("_id"),
                  rev=item.get("_rev"))
        doc._body = item
        doc._lazy_loaded = True
        return doc

    @classmethod
    def load(cls, connection, meta=None, id=None):
        """
        Method to load particular document from database
        by using meta information (which passed by ``Cursor``)
        or by specified document ``id``

        .. testcode::

            doc = c.test.documents.create({"x": 2})

            same_doc = Document.load(c.connection, id=doc.id)
            assert doc.body["x"] == same_doc.body["x"]

        """
        if isinstance(meta, dict) and "_id" in meta:
            id = meta.get("_id")

        if id is None:
            raise DocumentNotFound("id equal to None, can't load")

        response = connection.get(
            cls.READ_DOCUMENT_PATH.format(id),
            _expect_raw=True)

        if response.status != 200:
            raise DocumentNotFound(
                "Sorry, document with handle `{0}` "
                "not exist in database".format(id))

        return cls.wrap(connection, response.data)

    def lazy_loader(self):
        return Document.load(self.connection, id=self._id)

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
        """
        Return whole document.

        This property setter also should be used if
        overwriting of whole document is required.

        .. testcode::

            doc_id = c.test.documents.create({"x": 2}).id

            doc = c.test.documents.load(doc_id)
            assert doc.body["x"] == 2

            doc.body = {"x": 1}
            doc.save()

            assert c.test.documents.load(doc_id).body["x"] == 1
        """
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
        *(fallback)* value ``0``

        .. testcode::


            c.test.documents().first.get(name="sample_key", default=0)
        """

        if not self._body:
            return default

        if isinstance(self._body, (list, tuple)) and \
                isinstance(name, int):
            return self._body[name]

        if isinstance(self._body, (list, tuple)) or name is None:
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

        if self._id is not None:
            raise DocumentAlreadyCreated(
                "This document already created with id {0}".format(self.id)
            )

        params = {"collection": self.collection.cid}

        if createCollection is True:
            params.update({"createCollection": True})

        params.update(kwargs)

        response = self.connection.post(
            self.connection.qs(
                self.DOCUMENT_PATH,
                **params
            ),
            data=body)

        if response.status in [200, 201, 202]:
            self._body = body
            parse_meta(self, response)

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
                "You trying to update document `{0}` with "
                "incompatible datat type {1}".format(
                    self.id,
                    repr(newData)
                )
            )

        if save is True:
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
            **kwargs)

        # update revision of the document
        if response.status in [200, 201, 202]:
            self._rev = response.data.get("_rev")
            return self

        raise DocuemntUpdateError(
            response.get("errorMessage", "Unknown error"))

    def delete(self):
        """
        Delete current document.

        Return ``True`` if success and ``False`` if not
        """
        response = self.connection.delete(
            self.DELETE_DOCUMENT_PATH.format(self.id)
        )

        if response.status == 202:
            self._id = None
            self._rev = None
            self._body = None
            return True

        return False
