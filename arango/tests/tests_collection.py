
from tests_base import TestsBase

from nose.tools import assert_equal, assert_false, assert_true, raises
from mock import Mock

from arango.core import Response
from arango.collection import Collection, Collections
from arango.document import Documents
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
            self.c.CREATE_COLLECTION_PATH
        )

        test_data = {"name": "test", "waitForSync": False}
        test_args = {"data": json.dumps(test_data)}

        assert_equal(self.c.response.url, url)
        assert_equal(self.c.response.args, test_args)

    def test_load(self):
        response = self.c.load()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.LOAD_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

    def test_unload(self):
        response = self.c.unload()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.UNLOAD_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

    def test_delete(self):
        self.c.delete()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.DELETE_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(self.c.response.url, url)

    def test_truncate(self):
        response = self.c.truncate()

        url = "{0}{1}".format(
            self.conn.url,
            self.c.TRUNCATE_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

    def test_info(self):
        assert_equal(
            self.c.info(resource="wrong"),
            self.c.info()
        )

    def test_properties(self):
        response = self.c.properties(
            waitForSync=True
        )

        url = "{0}{1}".format(
            self.conn.url,
            self.c.PROPERTIES_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

        test_data = {"waitForSync": True}
        test_args = {"data": json.dumps(test_data)}

        response = self.c.properties(waitForSync=True)
        assert_equal(response.url, url)
        assert_equal(response.args, test_args)

        response = self.c.properties()
        assert_equal(response.args, {})

    def test_rename(self):
        test_data = {"name": "test1"}
        test_args = {"data": test_data}

        url = "{0}{1}".format(
            self.conn.url,
            self.c.RENAME_COLLECTION_PATH.format(self.c.name)
        )

        mock = Mock()

        prev_c = self.c.connection.put
        self.c.connection.put = mock

        mock(url, test_args).is_error = False

        assert_true(
            self.c.rename(name="test1")
        )

        assert_equal(self.c.response.url, mock().url)

        assert_equal(self.c.name, "test1")
        assert_equal(self.c.cid, "test1")

        assert_equal(self.c, self.conn.collection.test1)
        assert_false("test" in self.conn._collection.collections)

        self.c.rename(name="test")

        self.c.connection.put = prev_c

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
