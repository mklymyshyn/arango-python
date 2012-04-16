
__all__ = ("InvalidCollectionId", "CollectionIdAlreadyExist",
           "InvalidCollection", "DocumentAlreadyCreated",
           "DocumentIncompatibleDataType", "WrongIndexType",
           "EmptyFields")


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


class DocumentIncompatibleDataType(Exception):
    """Raises in case you trying to update document
    with non-dict or non-list data"""


class WrongIndexType(Exception):
    """Raises in case index type is undefined"""


class EmptyFields(Exception):
    """Raises in case no fields for index provied"""
