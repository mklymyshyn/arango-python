import requests

from nose.tools import assert_equal, assert_not_equal, \
                        assert_true, assert_false, raises

from mock import Mock

from .tests_base import TestsBase

from avocado import create
from avocado.core import Connection, Response


class TestConnectionInit(TestsBase):

    def test_basic(self):
        conn = Connection()

        assert_equal(conn.prefix, "http://")
        assert_equal(conn.url, "http://localhost:8529")

        conn.is_https = True
        conn.port = 1234

        assert_not_equal(conn.url, "https://localhost:1234")

    def test_create_shortcut(self):
        assert_equal(repr(Connection().collection), repr(create()))
        assert_equal(repr(Connection()), repr(create().connection))

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


class TestConnectionRequestsFactory(TestsBase):

    methods = ["post", "put", "get", "delete"]

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

    @raises(AttributeError)
    def test_wrong_http_method(self):
        conn = Connection()
        conn.wrong("/")


class TestResponse(TestsBase):
    def response(self, status=500, text="text"):
        response_mock = Mock()
        response_mock.status_code = status
        response_mock.text = text

        return Response(self.url, response_mock)

    def test_unparseable_response(self):
        response = self.response()

        assert_equal(response.status, 500)
        assert_true(response.is_error)

        assert_true(
            "Can't parse response from AvocadoDB: " in \
            response.message
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

    def test_parse_response(self):
        response = self.response(
            status=200,
            text='{"status": 200, "message": "test", "value": 1}'
        )

        assert_false(response.is_error)
        assert_equal(response.status, 200)
        assert_equal(
            response.get("message"),
            "test"
        )
        assert_equal(
            response.get("value"),
            1
        )
