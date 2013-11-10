import logging

from .exceptions import DatabaseAlreadyExist, DatabaseSystemError
from .utils import json

__all__ = ("Cursor",)

logger = logging.getLogger(__name__)


class Database(object):
    """
    ArangoDB starting from version 1.4 work with multiple databases.
    This is abstraction to manage multiple databases and work
    within documents.
    """
    DATABASE_PATH = "/_api/database/{0}"
    NO_DATABASE_PATH = "/_api/database"
    ENDPOINT_PATH = "/_db/{0}"

    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def url(self, path):
        return "{0}{1}".format(self.connection.url(db_prefix=False), path)

    def create(self, ignore_exist=True):
        """
        Create new database and return instance
        """

        response = self.connection.client.post(
            self.url(self.NO_DATABASE_PATH), data=json.dumps({
                "name": self.name}))

        # update revision of the document
        if response.status_code == 200:
            return self

        if response.status_code in [400, 403, 409] and ignore_exist is False:
            raise DatabaseAlreadyExist(self.name)
        else:
            return self

        raise DatabaseSystemError(response)

    @property
    def info(self):
        """
        Get info about database
        """
        response = self.connection.get(
            self.DATABASE_PATH.format("current"))

        return response.data.get("result", {})

    def delete(self, ignore_exist=True):
        """
        Delete database
        """
        response = self.connection.client.delete(
            self.url(self.DATABASE_PATH.format(self.name)))

        if response.status_code == 200:
            return True

        if ignore_exist is False:
            raise DatabaseSystemError(response)

        return True

    @property
    def prefix(self):
        """
        Property to return endpoint for this particular database
        """
        # NB: return empty prefix in case no database name provided
        # it's for compatibility with previous versions of ArangoDB
        if self.name is None:
            return ""

        return self.ENDPOINT_PATH.format(self.name)

    def __repr__(self):
        return "<ArangoDB Database: {0}>".format(self.name)
