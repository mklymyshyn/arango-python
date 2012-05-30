import logging
import os

from nose.tools import assert_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsIndexIntegration",)


class TestsIndexIntegration(TestsIntegration):

    def setUp(self):
        super(TestsIndexIntegration, self).setUp()

        c = self.conn
        c.collection.test.create()
        self.cl = c.collection.test

    def tearDown(self):
        c = self.conn

        for iid in self.cl.index()[0].keys():
            c.collection.test.index.delete(iid)

        c.collection.test.delete()

        super(TestsIndexIntegration, self).tearDown()

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
        key = self.cl.index.create(["value"]).get("id")
        count = len(self.cl.index()[0])

        rs, resp = self.cl.index.delete(key)
        assert_equal(len(self.cl.index()[0]), count - 1)


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsIndexIntegration = None
