import logging
import os

from nose.tools import assert_equal, assert_true, \
                       assert_not_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsDocument",)


class TestsDocument(TestsIntegration):

    def tearDown(self):
        super(TestsDocument, self).tearDown()

        c = self.conn
        c.collection.test.delete()

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

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 1)

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 2)

    def test_document_deletion(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Creating sample document")

        doc = c.collection.test.documents.create([1])

        assert_not_equal(doc, None)

        count = c.collection.test.documents.count()

        assert_true(doc.delete())

        assert_equal(
            c.collection.test.documents.count(),
            count - 1
        )


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsDocument = None
