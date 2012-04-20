import logging

from .document import Document
from .exceptions import EdgeAlreadyCreated

logger = logging.getLogger(__name__)


__all__ = ("Edge",)


class Edge(object):

    EDGE_PATH = "/edge"

    def __init__(self, collection=None):
        self.connection = collection.connection
        self.collection = collection

        self._body = None
        self._id = None
        self._rev = None
        self._from = None
        self._to = None

    @property
    def id(self):
        return self._id

    @property
    def rev(self):
        return self._rev

    @property
    def from_document(self):
        return self._from

    @property
    def to_document(self):
        return self._to

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

    def get(self, name=None, default=None):
        """Getter for body"""

        if not self._body:
            return default

        if name == None:
            return self._body

        return self._body.get(name, default)

    def parse_edge_response(self, response):
        self._id = response.get("_id", None)
        self._rev = response.get("_rev", None)
        self._from = response.get("_from", None)
        self._to = response.get("_to", None)
        self._body = response

    def create(self, from_doc, to_doc, body):
        if self.id is not None:
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

        # define document ID
        if response.get("code", 500) in [201, 202]:
            self.parse_edge_response(response)

        return self, response
