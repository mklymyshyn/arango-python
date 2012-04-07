
from tests_base import TestsBase

from nose.tools import assert_equal, assert_false, assert_true, raises
from mock import Mock

from avocado.core import Response
from avocado.collection import Collection, Collections
from avocado.document import Document
from avocado.utils import json
from avocado.exceptions import CollectionIdAlreadyExist, InvalidCollectionId, \
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
        assert_equal(
            self.conn.collection().__class__,
            Response
        )


class TestCollection(TestsBase):
    def setUp(self):
        super(TestCollection, self).setUp()
        self.c = self.conn.collection.test

    def test_cid(self):
        assert_equal(self.c.cid, "test")

    def test_document(self):
        assert_equal(
            Document(collection=self.c).__class__,
            self.c.document.__class__
        )

        # check shortcut
        assert_equal(
            self.c.d.__class__,
            self.c.document.__class__
        )

    def test_create(self):
        response = self.c.create()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.CREATE_COLLECTION_PATH
        )

        test_data = {"name": "test", "waitForSync": False}
        test_args = {"data": json.dumps(test_data)}

        assert_equal(response.url, url)
        assert_equal(response.args, test_args)

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
        response = self.c.delete()
        url = "{0}{1}".format(
            self.conn.url,
            self.c.DELETE_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

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

    def test_param(self):
        response = self.c.param(
            waitForSync=True
        )

        url = "{0}{1}".format(
            self.conn.url,
            self.c.PARAM_COLLECTION_PATH.format(self.c.name)
        )

        assert_equal(response.url, url)

        test_data = {"waitForSync": True}
        test_args = {"data": json.dumps(test_data)}

        response = self.c.param(waitForSync=True)
        assert_equal(response.url, url)
        assert_equal(response.args, test_args)

        response = self.c.param()
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

        response = self.c.rename(
            name="test1"
        )

        assert_equal(response.url, mock().url)

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
