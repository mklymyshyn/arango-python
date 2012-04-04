
from tests_base import TestsBase

from nose.tools import assert_equal

from avocado.core import Response
from avocado.collection import Collection, Collections


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
    pass
