import logging

from .document import Document

logger = logging.getLogger(__name__)

__all__ = ("Collection", "Collections")


class Collections(object):
    """connection) for Collections"""

    def __init__(self, connection):
        self.connection = connection
        self.collections = {}
        connection.collections = self

    def __getattr__(self, name):
        """Lazy init of collection"""
        return self.collections.get(
            name,
            Collection(
                connection=self.connection,
                name=name
            )
        )


class Collection(object):
    """Method which should be passed to
    document instance"""
    _doc_methods = (
        "create",
        "update",
        "delete",
    )

    def __init__(self, connection=None, name=None, handle=None,
            createCollection=True):
        self.connection = connection
        self.name = name
        self._handle = handle
        self.createCollection = createCollection

    def __getattr__(self, name):
        """Pass methods to new Document instance
        """
        if name in self._doc_methods:
            return getattr(Document(collection=self), name)
