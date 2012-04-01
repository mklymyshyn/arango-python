import unittest
import requests

from nose.tools import assert_equal, assert_not_equal
from mock import patch

from avocado.core import Connection


class TestConnectionInit(unittest.TestCase):

    def test_basic(self):
        conn = Connection()

        assert_equal(conn.prefix, "http://")
        assert_equal(conn.url, "http://localhost:8529")

        conn.is_https = True
        conn.port = 1234

        assert_not_equal(conn.url, "https://localhost:1234")

    def test_modify(self):
        conn = Connection()

        conn.is_https = True
        conn.port = 1234

        assert_equal(conn.url, "https://localhost:1234")

        conn.is_https = False
        conn.port = 9922

        assert_not_equal(conn.url, "http://localhost:9922")

    def test_repr(self):
        conn = Connection()

        assert_equal(
            str(conn),
            "<Connection to AvocadoDB (http://localhost:8529)>"
        )


class TestConnectionRequestsFactory(unittest.TestCase):

    methods = ["post", "put", "get", "delete"]

    def setUp(self):
        def stub_url(*args, **kwargs):
            return "Response"

        for m in self.methods:
            setattr(self, m, patch("requests.{0}".format(m)))
            getattr(self, m).start()

    def tearDown(self):
        for m in self.methods:
            getattr(self, m).stop()

    def test_http_methods_factory(self):
        conn = Connection()

        for method in self.methods:
            assert_equal(
                getattr(conn, method)("/").raw.read(),
                conn.requests_factory(method=method)("/").raw.read()
            )

    def test_http_methods_execution(self):
        conn = Connection()

        url = "%s%s" % (conn.url, "/")
        for method in self.methods:
            assert_equal(
                getattr(conn, method)("/").raw.read(),
                getattr(requests, method)(url).raw.read()
            )
