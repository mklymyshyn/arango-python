import copy
import logging

from .utils import parse_meta
from .mixins import ComparsionMixin
from .document import Document
from .exceptions import EdgeAlreadyCreated, EdgeNotYetCreated, \
    EdgeIncompatibleDataType, \
    DocumentIncompatibleDataType
from .utils import proxied_document_ref, json


logger = logging.getLogger(__name__)


__all__ = ("Edge", "Edges")


class Edges(object):
    """
    Proxy objects between ``Collection`` and ``Edge``.
    Edges in general very related to ``Document``.
    """
    EDGES_PATH = "/_api/edges/{0}"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

    def __call__(self, *args, **kwargs):
        from .core import Resultset

        return Resultset(self, *args, **kwargs)

    def __repr__(self):
        return "<ArangoDB Edges Proxy Object>"

    def __len__(self):
        return self.count()

    def count(self):
        """Get count of edges within current collection"""
        raise NotImplementedError(
            "This functionality not implemented yet."
            "Use ``connection.query`` with custom wrapper")

    def _cursor(self, rs):
        return []

    def iterate(self, rs):
        """
        Execute to iterate results
        """
        raise NotImplementedError(
            "This functionality not implemented yet."
            "Use ``connection.query`` with custom wrapper")

    def create(self, *args, **kwargs):
        """
        Create new Edge
        """
        edge = Edge(collection=self.collection)
        return edge.create(*args, **kwargs)

    def delete(self, ref):
        """
        Delete Edge by reference
        """

        edge = Edge(collection=self.collection, id=ref)
        return edge.delete()

    def update(self, ref, *args, **kwargs):
        """
        Update Edge by reference
        """

        edge = Edge(collection=self.collection, id=ref)
        return edge.update(*args, **kwargs)


class Edge(ComparsionMixin):
    """
    Edge instance object
    """

    EDGE_PATH = "/_api/edge"
    READ_EDGE_PATH = "/_api/edge/{0}"
    DELETE_EDGE_PATH = "/_api/edge/{0}"
    UPDATE_EDGE_PATH = "/_api/edge/{0}"

    IGNORE_KEYS = set(["_rev", "_id", "_from", "_to", "_key"])
    LAZY_LOAD_HANDLERS = [
        "id", "rev", "body", "get", "update", "delete",
        "from_document", "to_document"
    ]

    def __init__(self, collection=None,
                 _id=None, _rev=None,
                 _from=None, _to=None, **kwargs):
        self.connection = collection.connection
        self.collection = collection

        self._body = None
        self._id = _id
        self._rev = _rev
        self._from = _from
        self._to = _to

        self._from_document = None
        self._to_document = None

        if _id is not None:
            self._body = kwargs

    @property
    def id(self):
        """
        Id of the :ref:`Edge` instance
        """
        return self._id

    @property
    def rev(self):
        """
        Revision of the :ref:`Edge` instance
        """
        return self._rev

    @property
    def from_document(self):
        """
        From vertex, return instance of ``Document`` or ``None``
        """
        if not self._from:
            return None

        if not self._from_document:
            self._from_document = Document(
                collection=self.collection,
                connection=self.connection,
                id=self._from
            )

        return self._from_document

    @property
    def to_document(self):
        """
        To vertex, return instance of ``Document`` or ``None``
        """

        if not self._to:
            return None

        if not self._to_document:
            self._to_document = Document(
                collection=self.collection,
                connection=self.connection,
                id=self._to
            )

        return self._to_document

    def __eq__(self, other):
        """
        Compare two Edges in same way as Document and
        additionally compare FROM and TO documents
        """

        if super(Edge, self).__eq__(other) is False:
            return False

        if (self._from == other._from and
                self._to == other._to):
            return True

        return False

    def __repr__(self):
        return "<ArangoDB Edge: Id {0}/{1}, From {2} to {3}>".format(
            self._id,
            self._rev,
            self._from,
            self._to
        )

    def __getitem__(self, name):
        """Get element by dict-like key"""
        return self.get(name)

    def __setitem__(self, name, value):
        """Set element by dict-like key"""

        self._body[name] = value

    @property
    def body(self):
        """This property return Edge content"""
        return self.get()

    def get(self, name=None, default=None):
        """
        This method very similar to ``dict``'s ``get`` method.
        The difference is that *default* value should be specified
        explicitly.

        To get specific value for specific key in body use and default
        *(fallback)* value ``0``::

            edge.get(name="sample_key", default=0)

        """

        if not self._body:
            return default

        if name is None:
            return self._body

        return self._body.get(name, default)

    def parse(self, response):
        """
        Parse Edge details
        """

        self._from = response.get("_from", None)
        self._to = response.get("_to", None)
        self._body = response.data

        return response

    def create(self, from_doc, to_doc, body=None, **kwargs):
        """
        Method to create new edge.
        ``from_doc`` and ``to_doc`` may be both
        **document-handle** or instances of ``Document`` object.

        Possible arguments: :term:`waitForSync`

        Read more about additional arguments  :term:`Edges REST Api`

        This method may raise :term:`EdgeAlreadyCreated` exception in
        case edge already created.

        Return edge instance (``self``) or ``None``
        """

        if self.id is not None:
            raise EdgeAlreadyCreated(
                "This edge already created with id {0}".format(self.id)
            )

        from_doc_id = proxied_document_ref(from_doc)
        to_doc_id = proxied_document_ref(to_doc)

        params = {
            "collection": self.collection.cid,
            "from": from_doc_id,
            "to": to_doc_id}

        params.update(kwargs)

        data = copy.copy(self.body) if self.body else {}
        data.update({
            "_from": from_doc_id,
            "_to": to_doc_id
        })

        response = self.connection.post(
            self.connection.qs(
                self.EDGE_PATH,
                **params
            ),
            data=json.dumps(body or {}))

        # define document ID
        if response.status in [200, 201, 202]:
            self.parse(parse_meta(self, response))
            return self

        return None

    def delete(self):
        """
        Method to delete current edge. If edge deleted
        this method return ``True`` and in other case ``False``
        """
        response = self.connection.delete(
            self.DELETE_EDGE_PATH.format(self.id))

        if response.get("code", 500) == 204:
            self.parse(parse_meta(self, response))
            self._from, self._to = None, None
            self._id, self._rev, self._body = None, None, None
            return True

        return False

    def update(self, body, from_doc=None, to_doc=None, save=True, **kwargs):
        """
        Method to update edge. In case **from_doc** or **do_doc**
        not specified or equal to ``None`` then current
        ``from_document`` and ``to_document`` will be used.

        In case ``save`` argument set to ``False`` edge will not be
        updated until ``save()`` method will be called.

        This method may raise :term:`EdgeNotYetCreated` exception
        in case you trying to update edge which is not saved yet.

        Exception :term:`EdgeIncompatibleDataType` will be raised
        in case body of the edge isn't ``dict``.
        """
        if not self._id or not self._from or not self._to:
            raise EdgeNotYetCreated(
                "Sorry, you try to update Edge which is not yet created"
            )

        from_doc_id = proxied_document_ref(from_doc) or self._from
        to_doc_id = proxied_document_ref(to_doc) or self._to

        self._from = from_doc_id
        self._to = to_doc_id

        if not issubclass(type(body), dict) and body is not None:
            raise EdgeIncompatibleDataType(
                "Body should be None (empty) or instance or "
                "subclass of `dict` data type")

        if body is not None:
            self.body.update(body)

            return self.save(**kwargs)

        return True

    def save(self, **kwargs):
        """
        Method to save Edge. This is useful when
        edge udpated several times via ``update``

        Possible arguments: :term:`waitForSync`

        Read more about additional arguments  :term:`Edges REST Api`
        """
        # TODO: research it's possible to change
        # from/to edge properties within this method

        data = copy.copy(self.body or {})

        data.update({
            "_from": self._from,
            "_to": self._to
        })

        response = self.connection.put(
            self.UPDATE_EDGE_PATH.format(self.id),
            data=data,
            **kwargs)

        self._response = response

        # update revision of the edge
        if response.get("code", 500) in [201, 202]:
            parse_meta(self, response)
            return self

        return None
