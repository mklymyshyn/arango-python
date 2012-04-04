import unittest
import requests

from nose.tools import assert_equal, assert_not_equal, assert_true

from mock import patch, Mock

from avocado.core import Connection, Response


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
                getattr(conn, method)("/"),
                conn.requests_factory(method=method)("/")
            )

    def test_http_methods_execution(self):
        conn = Connection()

        url = "{0}{1}".format(conn.url, "/")
        for method in self.methods:
            assert_equal(
                getattr(conn, method)("/"),
                Response(
                    url,
                    getattr(requests, method)(url)
                )
            )


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.conn = Connection()
        self.url = "{0}{1}".format(self.conn.url, "/document")

    def response(self, status=500, text="text"):
        response_mock = Mock()
        response_mock.status_code = status
        response_mock.text = text

        return Response(self.url, response_mock)

    def test_unparseable_response(self):
        response = self.response()

        assert_equal(response.status, 500)
        assert_true(response.is_error)

        assert_equal(
            response.message,
            "Can't parse response from AvocadoDB: "\
            "{0} (URL: {1}, Response: {2})".format(
                "No JSON object could be decoded",
                self.url,
                repr(response.response)
            )
        )

    def test_repr(self):
        response = self.response()
        assert_equal(
            str(response),
            "<Response for {0}: {1}>".format(
                repr(response.__dict__),
                self.url
            )
        )
