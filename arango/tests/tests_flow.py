import logging
import os

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsFlow",)


class TestsFlow(TestsIntegration):
    """
    Class to test usecases of ArangoDB driver.

    Sample cases:
     - create document
     - update document
     - create edge
     etc.
    """
    def setUp(self):
        super(TestsFlow, self).setUp()

        c = self.conn
        c.collection.test.create()
        self.cl = c.collection.test

    def tearDown(self):
        c = self.conn

        for iid in self.cl.index()[0].keys():
            c.collection.test.index.delete(iid)

        c.collection.test.delete()

        super(TestsFlow, self).tearDown()


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsFlow = None
