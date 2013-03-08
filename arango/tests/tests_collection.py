from .tests_base import TestsBase

from nose.tools import assert_equal, assert_true, raises

from arango.clients import Client
from arango.collection import Collection, Collections
from arango.utils import json
from arango.exceptions import CollectionIdAlreadyExist, InvalidCollectionId, \
    InvalidCollection


class TestCollectionProxy(TestsBase):
    def test_proxy(self):

        assert_equal(
            self.conn.collection.__class__,
            Collections
        )

        assert_equal(
            self.conn.collection.test.__class__,
            Collection
        )

        assert_equal(
            self.conn.collection.test.cid,
            Collection(
                connection=self.conn,
                name="test"
            ).cid
        )

    def test_repr(self):
        assert_equal(
            str(self.conn.collection),
            "<Collections proxy for {0}>".format(self.conn)
        )

    def test_collections_list(self):
        collection = self.conn.collection()

        assert_equal(
            collection,
            []
        )


class TestCollection(TestsBase):
    def setUp(self):
        super(TestCollection, self).setUp()
        self.c = self.conn.collection.test

    def test_cid(self):
        assert_equal(self.c.cid, "test")

    def test_create(self):
        self.c.create()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.CREATE_COLLECTION_PATH)

        test_data = {"name": "test", "waitForSync": False}
        test_args = {"data": json.dumps(test_data)}

        assert_true(Client.post.called)
        assert_equal(Client.post.call_args[0][0], url)
        assert_equal(Client.post.call_args[1], test_args)

    def test_load(self):
        self.c.load()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.LOAD_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(Client.put.call_args[0][0], url)

    def test_unload(self):
        self.c.unload()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.UNLOAD_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(Client.put.call_args[0][0], url)

    def test_delete(self):
        self.c.delete()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.DELETE_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(Client.delete.call_args[0][0], url)

    def test_truncate(self):
        self.c.truncate()

        url = "{0}{1}".format(
            self.conn.url,
            self.c.TRUNCATE_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(Client.put.call_args[0][0], url)

    def test_info(self):
        assert_equal(
            self.c.info(resource="wrong"),
            self.c.info())

    def test_properties(self):
        self.c.properties(waitForSync=True)

        url = "{0}{1}".format(
            self.conn.url,
            self.c.PROPERTIES_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(Client.put.call_args[0][0], url)

        test_data = {"waitForSync": True}
        test_args = {"data": json.dumps(test_data)}

        self.c.properties(waitForSync=True)
        assert_equal(Client.put.call_args[0][0], url)
        assert_equal(Client.put.call_args[1], test_args)

        self.c.properties()
        assert_equal(Client.get.call_args[1], {})

    def test_rename(self):
        test_data = {"name": "test1"}
        test_args = {"data": json.dumps(test_data)}

        url = "{0}{1}".format(
            self.conn.url,
            self.c.RENAME_COLLECTION_PATH.format(self.c.name))

        self.c.rename(name="test1")

        assert_equal(Client.post.call_args[0][0], url)
        assert_equal(Client.post.call_args[1], test_args)

    def test_rename_manual_collection(self):
        c = Collection(connection=self.c.connection, name="manual")
        self.conn.collection.rename_collection(c, "sample")

        assert_true("sample" in self.conn.collection.collections)

    @raises(CollectionIdAlreadyExist)
    def test_rename_collection_with_exist_name(self):
        self.conn.collection.rename_collection(self.c, "test")

    @raises(InvalidCollection)
    def test_rename_wrong_collection(self):
        self.conn.collection.rename_collection(object(), "test")

    @raises(InvalidCollectionId)
    def test_rename_empty_collection(self):
        self.conn.collection.test.rename("")

    def test_count(self):
        assert_equal(self.c.count(), 0)
        assert_equal(self.c.count(), len(self.c))

    def test_repr(self):
        exp_repr = "<Collection '{0}' for {1}>".format("test", self.conn)
        assert_equal(repr(self.c), exp_repr)
