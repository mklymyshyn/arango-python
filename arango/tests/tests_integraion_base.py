import os
import logging
import unittest
import time

from arango.core import Connection

logger = logging.getLogger(__name__)


__all__ = ("TestsIntegration",)

# timeout which we wait for async actions from ArangoDB
DEFAULT_TIMEOUT = 0.2


class TestsIntegration(unittest.TestCase):
    """
    This suite shoudl work with real ArangoDB instance
    so make sure that db is running and available
    on http://localhost:8529
    """

    def setUp(self):
        self.conn = Connection()

        # enable verbose output for tests
        if "DEBUG_HTTP" in os.environ:
            self.conn.client.DEBUG = True

    def tearDown(self):
        c = self.conn

        logger.info("Deleting/Cleaning up collection 'test'")
        c.collection.test.delete()

    def wait(self, times=1):
        """
        Waiting for async actions ``times`` times
        """
        for c in range(times):
            time.sleep(DEFAULT_TIMEOUT)
