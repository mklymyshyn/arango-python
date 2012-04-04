import unittest
import logging

from nose.tools import assert_equal, assert_false, assert_true

from avocado.core import Connection

logger = logging.getLogger(__name__)


class TestsCollection(unittest.TestCase):
    """
    This suite shoudl work with real AvocadoDB instance
    so make sure that db is running and available
    on http://localhost:8529
    """

    def setUp(self):
        self.conn = Connection()

    def tearDown(self):
        c = self.conn

        logger.info("Deleting/Cleaning up collection 'test'")
        c.collection.test.delete()

    def test_collection_creation(self):
        c = self.conn

        logger.info("Creationg new collection 'test'")

        response = c.collection.test.create()
        assert_equal(response.get("status"), 3)
        assert_equal(response.get("code"), 200)

        assert_false(response.get("waitForSync"))
        assert_false(response.get("error"))

        logger.info("Deleting collection 'test'")
        c.collection.test.delete()

        logger.info("Deleting collection 'test' with waitForSync=True")
        response = c.collection.test.create(waitForSync=True)

        assert_equal(response.get("code"), 200)
        assert_true(response.get("waitForSync"))

    def test_colletion_deletion(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Deleting collection 'test'")
        response = c.collection.test.delete()

        assert_equal(response.get("code"), 200)
        assert_false(response.get("error"))
