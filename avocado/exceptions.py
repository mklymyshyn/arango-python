
__all__ = ("InvalidCollectionId", "CollectionIdAlreadyExist",
           "InvalidCollection", "DocumentAlreadyCreated")


class InvalidCollection(Exception):
    """Collection should exist and be subclass of Collection object"""


class InvalidCollectionId(Exception):
    """Invalid name of the collection provided"""


class CollectionIdAlreadyExist(Exception):
    """Raise in case you try to rename collection and new name already
    available"""


class DocumentAlreadyCreated(Exception):
    """Raise in case document already exist and you try to
    call `create` method"""
