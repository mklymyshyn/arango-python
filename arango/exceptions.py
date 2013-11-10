
__all__ = ("InvalidCollectionId", "CollectionIdAlreadyExist",
           "InvalidCollection", "DocumentAlreadyCreated",
           "DocumentIncompatibleDataType", "WrongIndexType",
           "EmptyFields", "EdgeAlreadyCreated",
           "DocumentNotFound", "EdgeNotYetCreated",
           "EdgeIncompatibleDataType", "EdgeNotFound",
           "DocuemntUpdateError", "AqlQueryError", "DatabaseAlreadyExist",
           "DatabaseSystemError")


class DatabaseSystemError(Exception):
    """Raises in case something went completely wrong"""


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


class DocumentNotFound(Exception):
    """Raises in case Document not exist in database"""


class DocuemntUpdateError(Exception):
    """In case can't save document"""


class WrongIndexType(Exception):
    """Raises in case index type is undefined"""


class EmptyFields(Exception):
    """Raises in case no fields for index provied"""


class EdgeAlreadyCreated(Exception):
    """Raises in case Edge have identifier and already created"""


class EdgeNotYetCreated(Exception):
    """Raises in case you try to update Edge which is not created"""


class EdgeIncompatibleDataType(Exception):
    """Raises when you provide new body not None or not dict"""


class EdgeNotFound(Exception):
    """Raised in case Edge not found"""


class AqlQueryError(Exception):
    """In case AQL query cannot be executed"""

    def __init__(self, message, num=0, code=0):
        self.num = num
        self.code = code
        self.message = message

        super(AqlQueryError, self).__init__(message)


class DatabaseAlreadyExist(Exception):
    """Raises in case database already exists"""
