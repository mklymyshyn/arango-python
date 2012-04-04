
from tests_base import TestsBase

from nose.tools import assert_equal

from avocado.core import Response
from avocado.collection import Collection, Collections
from avocado.document import Document


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

        assert_equal(response.url, url)
