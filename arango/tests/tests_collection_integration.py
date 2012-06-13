import logging
import os

from nose.tools import assert_equal, assert_false, assert_true

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


class TestsCollection(TestsIntegration):
    def purge(self):
        c = self.conn

        logger.info("Deleting/Cleaning up collection 'test'")

        c.collection.test_sample.delete()
        c.collection.sample1.delete()
        c.collection.sample2.delete()
        c.collection.sample3.delete()

    def tearDown(self):
        super(TestsCollection, self).tearDown()
        self.purge()

    def test_collection_creation(self):
        c = self.conn

        logger.info("Creationg new collection 'test'")

        c.collection.test.create()
        assert_equal(c.collection.test.response.get("status"), 3)
        assert_equal(c.collection.test.response.status, 200)

        assert_false(c.collection.test.response.get("waitForSync"))
        assert_false(c.collection.test.response.get("error"))

        logger.info("Deleting collection 'test'")
        c.collection.test.delete()

        logger.info("Deleting collection 'test' with waitForSync=True")
        c.collection.test.create(waitForSync=True)

        assert_equal(c.collection.test.response.get("code"), 200)
        assert_true(c.collection.test.response.get("waitForSync"))

    def test_colletion_deletion(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Deleting collection 'test'")
        assert_true(c.collection.test.delete())

        assert_equal(c.collection.test.response.get("code"), 200)
        assert_false(c.collection.test.response.get("error"))

    def test_collection_rename(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Renaming collection to 'test_sample'")
        assert_true(
                c.collection.test.rename(name="test_sample")
        )

        assert_equal(c.collection.test_sample.response.get("code"), 200)
        assert_false(c.collection.test_sample.response.get("error"))

        response = c.collection.test_sample.load()
        assert_equal(response.get("code"), 200)
        assert_false(response.get("error"), False)

        logger.info("Removign collection 'test_sample'")
        c.collection.test_sample.delete()

    def test_load_unload(self):
        c = self.conn

        c.collection.test.create()
        response = c.collection.test.load()

        assert_equal(response.get("code"), 200)
        assert_equal(response.get("count"), 0)
        assert_equal(response.get("name"), "test")

        response = c.collection.test.unload()

        assert_equal(response.get("code"), 200)
        assert_false(response.get("error"))

    def test_collectios_list(self):
        c = self.conn

        logger.info("Creationg three collections sample[1..3]")
        c.collection.sample1.create()
        c.collection.sample2.create()
        c.collection.sample3.create()

        logger.info("Getting list of collections")
        names = c.collection()

        for n in ["sample1", "sample2", "sample3"]:
            assert_true(n in names)

        logger.info("Deleting two of three collections")
        c.collection.sample1.delete()
        c.collection.sample3.delete()

        names = c.collection()

        for n in ["sample1", "sample3"]:
            assert_false(n in names)

        assert_true("sample2" in names)

        logger.info("Removing last collection")
        c.collection.sample2.delete()

    def test_details_and_param(self):
        c = self.conn
        c.collection.test.create()

        response = c.collection.test.info()
        assert_equal(response.get("code"), 200)
        assert_false(response.get("waitForSync", False))

        c.collection.test.param(waitForSync=True)

        # renew
        response = c.collection.test.param()
        assert_true(response.get("waitForSync", True))

        c.collection.test.param(waitForSync=False)

        response = c.collection.test.param()
        assert_false(response.get("waitForSync", False))

    def test_collection_truncate(self):
        c = self.conn.collection
        c.test.create()

        c.test.docs.create({"doc": 1})
        c.test.docs.create({"doc": 2})

        assert_equal(len(c.test), 2)

        c.test.truncate()

        assert_equal(len(c.test), 0)


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsCollection = None
