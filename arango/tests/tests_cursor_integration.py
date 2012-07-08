import os
import logging

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
            print [repr(cr) for cr in cursor]
        except Exception:
            logger.error("Can't print", exc_info=True)
            raise


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsCursor = None
