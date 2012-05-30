import unittest
import logging

from arango.core import Connection

logger = logging.getLogger(__name__)


__all__ = ("TestsIntegration",)


class TestsIntegration(unittest.TestCase):
    """
    This suite shoudl work with real ArangoDB instance
    so make sure that db is running and available
    on http://localhost:8529
    """

    def setUp(self):
        self.conn = Connection()

    def tearDown(self):
        c = self.conn

        logger.info("Deleting/Cleaning up collection 'test'")
        c.collection.test.delete()
