from .tests_base import TestsBase

from nose.tools import assert_equal, assert_true, raises

from arango.db import Database
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

    def test_database_property(self):
        assert_equal(self.conn.collection.database.__class__, Database)

    def test_repr(self):
        assert_equal(
            str(self.conn.collection),
            "<Collections proxy for {0}>".format(self.conn)
        )

    def test_collections_list(self):
        collection = self.conn.collection()

        assert_equal(collection, [])

    def test_collections_dict_iface(self):
        assert_equal(self.conn.collection["test"].__class__, Collection)


class TestCollection(TestsBase):
    def setUp(self):
        super(TestCollection, self).setUp()
        self.c = self.conn.collection.test
        self.c_e = self.conn.collection.test_edges

    def test_cid(self):
        assert_equal(self.c.cid, "test")

    def test_create(self):
        self.c.create()

        test_data = {
            "name": "test", "waitForSync": False,
            "type": Collections.COLLECTION_DOCUMENTS}
        test_args = {"data": json.dumps(test_data)}

        assert_true(Client.post.called)
        assert_equal(Client.post.call_args[1], test_args)

    def test_create_edges(self):
        self.c_e.create_edges()

        test_data = {
            "name": "test_edges", "waitForSync": False,
            "type": Collections.COLLECTION_EDGES}
        test_args = {"data": json.dumps(test_data)}

        assert_true(Client.post.called)
        assert_equal(Client.post.call_args[1], test_args)

    def test_info(self):
        assert_equal(
            self.c.info(resource="wrong"),
            self.c.info())

    def test_properties(self):
        self.c.properties(waitForSync=True)

        test_data = {"waitForSync": True}
        test_args = {"data": json.dumps(test_data)}

        self.c.properties(waitForSync=True)
        assert_equal(Client.put.call_args[1], test_args)

        self.c.properties()
        assert_equal(Client.get.call_args[1], {})

    def test_rename(self):
        test_data = {"name": "test1"}
        test_args = {"data": json.dumps(test_data)}

        self.c.rename(name="test1")

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
