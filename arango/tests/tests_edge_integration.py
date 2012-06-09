import logging
import os

from nose.tools import assert_equal, assert_not_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsEdge",)


class TestsEdge(TestsIntegration):

    def setUp(self):
        super(TestsEdge, self).setUp()

        self.c = self.conn.collection
        self.c.test.create()

        body = {"key": 1}

        self.from_doc = self.c.test.documents.create(body)
        self.to_doc = self.c.test.documents.create(body)

    def tearDown(self):
        super(TestsEdge, self).tearDown()

        c = self.conn
        c.collection.test.delete()

    def test_edge_creation(self):
        # creating edge with custom data
        self.c.test.edges.create(
            self.from_doc,
            self.to_doc,
            {"custom": 1}
        )

        # getting edge by document
        assert_not_equal(
            self.c.test.edges(self.from_doc).count,
            0
        )

        result = self.c.test.edges(
            self.from_doc, direction="out").first()

        assert_equal(
            result.to_document,
            self.to_doc
        )

        assert_equal(
            self.c.test.edges(self.from_doc, direction="in").first(),
            None
        )

    def test_edge_deletion(self):
        # creating edge with custom data
        self.c.test.edges.create(
            self.from_doc,
            self.to_doc,
            {"custom": 1}
        )

        self.c.test.edges(self.from_doc).first().delete()

        assert_equal(
            self.c.test.edges(self.from_doc).first(),
            None
        )


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsEdge = None
