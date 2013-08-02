import logging

from nose.tools import assert_equal, assert_not_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


class TestsCoreIntegration(TestsIntegration):
    def test_version(self):
        response = self.conn.version
        assert_equal(response.server, "arango")
        assert_not_equal(response.version, "")
        assert_equal(repr(response), "<{0} {1}>".format(
            response.server.title(), response.version))
