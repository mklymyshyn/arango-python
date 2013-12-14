import logging

from nose.tools import assert_equal, assert_false, assert_true, \
    assert_not_equal

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
        c.collection.test.delete()
        created = c.collection.test.create()
        self.wait()
        assert_true(created.cid is not None)

        logger.info("Deleting collection 'test'")

        assert_true(created.cid in c.collection())
        c.collection.test.delete()

        self.wait()
        assert_false(created.cid in c.collection())

        logger.info("Deleting collection 'test' with waitForSync=True")
        created = c.collection.test.create(waitForSync=True)
        assert_true(created.cid in c.collection())

    def test_edges_collection_creation(self):
        c = self.conn
        logger.info("Creating edges collection 'test'")

        created = c.collection.test_edges.create_edges()
        self.wait()

        assert_true(created.cid in c.collection())
        c.collection.test_edges.delete()

        self.wait()
        assert_false(created.cid in c.collection())

    def test_colletion_deletion(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Deleting collection 'test'")
        deleted = c.collection.test.delete()
        assert_true(deleted)

    def test_collection_rename(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Renaming collection to 'test_sample'")
        renamed = c.collection.test.rename(name="test_sample")
        assert_true(renamed)

        response = c.collection.test_sample.load()
        assert_equal(response.get("code"), 200)
        assert_false(response.get("error"), False)

        logger.info("Removign collection 'test_sample'")
        c.collection.test_sample.delete()

    def test_collection_rename_to_exist_name(self):
        c = self.conn.collection
        logger.info("Creating collection 'test' and 'test11")

        c.test.create()
        c.test1.create()

        assert_false(c.test1.rename("test"))

        c.test1.delete()

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

    def test_details_and_properties(self):
        c = self.conn
        c.collection.test.create(waitForSync=True)

        info = c.collection.test.info()
        assert_equal(info.get("code"), 200)

        properties = c.collection.test.properties()
        assert_true(properties.get("waitForSync", True))

        c.collection.test.properties(waitForSync=False)
        self.wait()

        # XXX: Expected behavior: ``waitForSync`` should equal False:
        #      doublecheck API for collection properties
        c.collection.test.properties()

    def test_collection_truncate(self):
        c = self.conn.collection
        c.test.create()

        c.test.docs.create({"doc": 1})
        c.test.docs.create({"doc": 2})

        assert_equal(len(c.test), 2)

        c.test.truncate()

        assert_equal(len(c.test), 0)

    def test_proxy_repr(self):
        self.conn.collection.test.create()
        assert_equal(
            repr(self.conn.collection.test.documents),
            "<ArangoDB Documents Proxy Object>"
        )

    def test_limit_documents(self):
        c = self.conn.collection
        c.test.create()

        c.test.docs.create({"doc": 1})
        c.test.docs.create({"doc": 2})

        assert_not_equal(
            self.conn.collection.test.documents().count,
            1
        )

        assert_equal(
            len(self.conn.collection.test.documents()),
            self.conn.collection.test.documents().count
        )

        assert_equal(
            len(self.conn.collection.test.documents().limit(1)),
            1
        )

        assert_equal(
            len(self.conn.collection.test
                .documents()
                .offset(2)
                .limit(1)),
            0)
