import logging

from nose.tools import assert_equal, assert_true

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

        for iid in self.cl.index().keys():
            c.collection.test.index.delete(iid)

        c.collection.test.delete()

        super(TestsIndexIntegration, self).tearDown()

    def test_index_create(self):
        self.cl.index.delete("name")
        index = self.cl.index.create(["name"])

        assert_equal(
            list(index.indexes.values())[0]["fields"],
            ["name"])

    def test_index_list(self):
        ids = self.cl.index()

        count = len(ids)

        self.cl.index.create(["value"])
        assert_equal(len(self.cl.index()), count + 1)

    def test_index_get(self):
        self.cl.index.create(["value"])
        ids = self.cl.index()
        key = list(ids.keys())[0]

        index = self.cl.index.get(key)

        assert_equal(str(index.get("id")), str(key))

    def test_index_delete(self):
        key = list(
            self.cl.index.create(["value"]).indexes.values())[0]["id"]
        count = len(self.cl.index())

        assert_true(self.cl.index.delete(key))
        assert_equal(len(self.cl.index()), count - 1)
