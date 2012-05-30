import logging

from .document import Document
from .exceptions import EdgeAlreadyCreated, EdgeNotYetCreated, \
                        EdgeIncompatibleDataType

logger = logging.getLogger(__name__)


__all__ = ("Edge", "Edges")


class Edges(object):

    EDGES_PATH = "/_api/edge"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

    def __call__(self, *args, **kwargs):
        from .core import Resultset

        return Resultset(self)

    def __repr__(self):
        return "<ArangoDB Edges Proxy Object>"

    def __len__(self):
        return self.count()

    def count(self):
        """Get count of edges"""
        response = self.connection.get(
            self.EDGES_PATH.format(self.collection.cid)
        )
        return len(response.get("edges", []))

    def query(self, rs):
        """This method will be called within Resultset so
        it should get list of document"""
        response = self.connection.get(
            self.EDGES_PATH.format(self.collection.cid)
        )

        edges = response.get("edges", [])[rs._offset:]

        if rs._limit != None:
            edges = edges[:rs._limit]

        for edge in edges:
            yield Edge(
                collection=self.collection,
                **edge
            )

    def create(self, *args, **kwargs):
        edge = Edge(collection=self.collection)
        return edge.create(*args, **kwargs)

    def delete(self, ref):
        """Delete Edge by reference"""

        edge = Edge(collection=self.collection, id=ref)
        return edge.delete()

    def update(self, ref, *args, **kwargs):
        """Update Edge by reference"""

        edge = Edge(collection=self.collection, id=ref)
        return edge.update(*args, **kwargs)


class Edge(object):

    EDGE_PATH = "/_api/edge"
    DELETE_EDGE_PATH = "/_api/edge/{0}"
    UPDATE_EDGE_PATH = "/_api/edge/{0}"

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

    @property
    def id(self):
        return self._id

    @property
    def rev(self):
        return self._rev

    @property
    def from_document(self):
        if not self._from:
            return None

        if not self._from_instance:
            self._from_instance = Document(
                collection=self.collection,
                id=self._from
            )

        return self._from_instance

    @property
    def to_document(self):
        if not self._to:
            return None

        if not self._to_instance:
            self._to_instance = Document(
                collection=self.collection,
                id=self._to
            )

        return self._to_instance

    def __getitem__(self, name):
        """Get element by dict-like key"""
        return self.get(name)

    def __setitem__(self, name, value):
        """Get element by dict-like key"""

        self._body[name] = value

    @property
    def edge(self):
        """Return whole document"""
        return self.get()

    @property
    def response(self):
        """Method to get latest response"""
        return self._response

    def get(self, name=None, default=None):
        """Getter for body"""

        if not self._body:
            return default

        if name == None:
            return self._body

        return self._body.get(name, default)

    def parse_edge_response(self, response):
        """
        Parse Edge details
        """
        self._id = response.get("_id", None)
        self._rev = response.get("_rev", None)
        self._from = response.get("_from", None)
        self._to = response.get("_to", None)
        self._body = response

    def create(self, from_doc, to_doc, body):
        if self.id != None:
            raise EdgeAlreadyCreated(
                "This edge already created with id {0}".format(self.id)
            )

        from_doc_id = from_doc
        to_doc_id = to_doc

        if issubclass(type(from_doc), Document):
            from_doc_id = from_doc.id

        if issubclass(type(to_doc), Document):
            to_doc_id = to_doc.id

        params = {
            "collection": self.collection.cid,
            "from": from_doc_id,
            "to": to_doc_id
        }

        response = self.connection.post(
            self.connection.qs(
                self.EDGE_PATH,
                **params
            ),
            data=body
        )

        self._response = response

        # define document ID
        if response.get("code", 500) in [201, 202]:
            self.parse_edge_response(response)

        return self

    def delete(self):
        response = self.connection.delete(
            self.DELETE_EDGE_PATH.format(self.id)
        )

        self._response = response

        if response.get("code", 500) == 204:
            self.parse_edge_response({})
            self._body = None
            return True

        return False

    def update(self, body, from_doc=None, to_doc=None, save=True, **kwargs):

        if not self._id or not self._from or not self._to:
            raise EdgeNotYetCreated(
                "Sorry, you try to update Edge which is not yet created"
            )

        from_doc_id = from_doc or self._from
        to_doc_id = to_doc or self._to

        if issubclass(type(from_doc), Document):
            from_doc_id = from_doc.id

        if issubclass(type(to_doc), Document):
            to_doc_id = to_doc.id

        self._from = from_doc_id
        self._to = to_doc_id

        if not issubclass(type(body), dict) and body != None:
            raise EdgeIncompatibleDataType(
                "Body should be None (empty) or instance or "\
                "subclass of `dict` data type"
            )

        if body != None:
            self.body.update(body)

        if save == True:
            return self.save(**kwargs)

        return True

    def save(self, **kwargs):
        # TODO: research it's possible to change
        # from/to edge properties within this method
        response = self.connection.put(
            self.UPDATE_EDGE_PATH.format(self.id),
            data=self.edge
        )

        self._response = response

        # update revision of the edge
        if response.get("code", 500) in [201, 202]:
            self._rev = response.get("_rev")
            return self

        return None
