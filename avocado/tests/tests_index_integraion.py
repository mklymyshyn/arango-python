import logging
import os

from nose.tools import assert_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsIndex",)


class TestsIndex(TestsIntegration):

    def setUp(self):
        super(TestsIndex, self).setUp()

        c = self.conn
        c.collection.test.create()
        self.cl = c.collection.test

    def tearDown(self):
        super(TestsIndex, self).tearDown()

        c = self.conn
        c.collection.test.delete()

    def test_index_create(self):
        response = self.cl.index.create(["name"])

        assert_equal(
            response.get("code"),
            201
        )

    def test_index_list(self):
        ids = self.cl.index()[0]

        count = len(ids)

        self.cl.index.create(["value"])
        assert_equal(len(self.cl.index()[0]), count + 1)

    def test_index_get(self):
        self.cl.index.create(["value"])
        ids = self.cl.index()[0]
        key = ids.keys()[0]

        index = self.cl.index.get(key)
        assert_equal(str(index.get("id")), str(key))

    def test_index_delete(self):
        self.cl.index.create(["value"])
        ids = self.cl.index()[0]
        key = filter(lambda k: str(k) != str(0), ids.keys())[0]

        count = len(ids)

        self.cl.index.delete(key)
        assert_equal(len(self.cl.index()[0]), count - 1)


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsIndex = None
