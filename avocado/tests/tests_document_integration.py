import logging
import os

from nose.tools import assert_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsDocument",)


class TestsDocument(TestsIntegration):

    def test_document_creation(self):
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

        c.collection.test.document.create(body)
        assert_equal(c.collection.test.count(), count_before + 1)

        c.collection.test.document.create(body)
        assert_equal(c.collection.test.count(), count_before + 2)



# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsDocument = None
