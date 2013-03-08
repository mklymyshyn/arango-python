import os
import logging


from nose.tools import assert_equal, assert_true
from arango.cursor import Cursor

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


class TestsCursor(TestsIntegration):
    def setUp(self):
        super(TestsCursor, self).setUp()
        self.c = self.conn.collection.test
        self.cursor = lambda *args, **kwargs: Cursor(
            self.conn, *args, **kwargs)

        logger.info("Creating collection `test`")
        self.c.create()

    def tearDown(self):
        super(TestsCursor, self).tearDown()

        self.c.delete()

    def test_cursor_basic(self):
        [self.c.documents.create({"num": n}) for n in range(10)]
        cursor = self.cursor("FOR d IN test RETURN d", count=True)

        try:
            print([repr(cr) for cr in cursor])
        except Exception:
            logger.error("Can't print", exc_info=True)
            raise


class TestQueries(TestsIntegration):
    def test_query(self):
        c = self.conn.collection
        c.test.create()

        cursor = self.conn.query("FOR d IN test RETURN d", count=True)
        prev_len = len(cursor)

        doc1 = c.test.docs.create({"doc": 1})
        doc2 = c.test.docs.create({"doc": 2})
        self.wait()

        cursor = self.conn.query("FOR d IN test RETURN d", count=True)
        assert_equal(len(cursor), prev_len + 2)

        total = 0

        for doc in cursor:
            for cdoc in [doc1, doc2]:
                if cdoc == doc:
                    total += 1
                    break

        assert_equal(
            total, 2,
            "One of docs are not added to database")

# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsCursor = None
    TestQueries = None
