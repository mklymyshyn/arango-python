import logging
import os

from nose.tools import assert_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsEdge",)


class TestsEdge(TestsIntegration):

    def tearDown(self):
        super(TestsEdge, self).tearDown()

        c = self.conn
        c.collection.test.delete()

    def test_edge_creation(self):
        c = self.conn

        logger.info("Creationg new collection 'test'")

        body = {
            "value": 1,
            "testing": True,
            "options": [
                1,
                2,
                3
            ]
        }

        c.collection.test.create()
        count_before = c.collection.test.count()

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 1)

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 2)


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsEdge = None
