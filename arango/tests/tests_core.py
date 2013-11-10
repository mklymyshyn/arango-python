from nose.tools import assert_equal, assert_not_equal, \
    assert_true, assert_false, raises


from mock import Mock

from .tests_base import TestsBase

from arango import create
from arango.core import Connection, Response, Resultset
from arango.clients import Client


class TestConnectionInit(TestsBase):

    def test_basic(self):
        conn = Connection()

        assert_equal(conn.prefix, "http://")
        assert_equal(conn.url(), "http://localhost:8529")

    def test_create_shortcut(self):
        assert_equal(repr(Connection().collection), repr(create()))
        assert_equal(repr(Connection()), repr(create().connection))

    def test_modify(self):
        conn = Connection()

        conn.is_https = True
        conn.port = 1234

        assert_equal(conn.url(), "https://localhost:1234")

        conn.is_https = False
        conn.port = 9922

        assert_not_equal(conn.url(), "http://localhost:9922")

    def test_repr(self):
        conn = Connection()

        assert_equal(
            str(conn),
            "<Connection to ArangoDB (http://localhost:8529)>")

    def test_database_prefix(self):
        conn = Connection(db="test")
        assert_equal(conn.url(), "http://localhost:8529/_db/test")
        assert_equal(conn.url(db_prefix=False), "http://localhost:8529")


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
                    getattr(Client, method)(url)
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
            "Can't parse response from ArangoDB: " in
            response.message)

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


class TestResultset(TestsBase):
    def setUp(self):
        super(TestResultset, self).setUp()
        self.Base = Mock()
        self.data = list(range(3))

        def iterate_mock(rs):
            for item in rs.data:
                yield item

        def prepare_resultset_mock(rs, args=None, kwargs=None):
            response = {"sample": 1}

            rs.response = response
            rs.count = len(self.data)

            data = self.data[rs._offset:]

            if rs._limit is not None:
                data = self.data[:rs._limit]

            rs.data = data

        self.Base.iterate = iterate_mock
        self.Base.prepare_resultset = prepare_resultset_mock

        self.rs = Resultset(base=self.Base)
        self.rs.base._cursor = lambda *a, **k: list(range(3))

    def test_init(self):
        rs = Resultset(self.Base, 1, 2, field=True, field2=False)

        assert_equal(rs._args, (1, 2))
        assert_equal(rs._kwargs, {"field": True, "field2": False})

    def test_response(self):
        assert_equal(self.rs.response, None)

        test_value = {"value": 1}
        self.rs._response = test_value

        assert_equal(self.rs.response, test_value)

    def test_iter(self):
        assert_equal(
            [item for item in self.rs],
            self.data
        )

    def test_first_shortcut(self):
        assert_equal(
            self.rs.first,
            self.data[0]
        )

    def test_first_last_shourcut_exceed(self):

        def iterate_mock(arg):
            for item in []:
                yield item

        self.Base.iterate = iterate_mock

        rs = Resultset(base=self.Base)

        assert_equal(rs.first, None)
        assert_equal(rs.last, None)

    def test_offset(self):
        assert_equal(
            len([item for item in self.rs.offset(1)]),
            2
        )

    def test_limit(self):
        assert_equal(
            len([item for item in self.rs.limit(2)]),
            2
        )

    def test_data(self):
        assert_equal(self.rs.data, None)

        self.rs.data = 1

        assert_equal(self.rs.data, 1)

    def test_count_shortcut(self):
        assert_equal(self.rs.count, 3)

    def test_repr(self):
        assert_equal(
            str(self.rs),
            "<Resultset: {0}>".format(
                ", ".join([str(i) for i in self.data])
            )
        )

    def test_repr_large_resultset(self):
        dataset = list(range(self.rs.max_repr_items * 2))

        def iterate_large_dataset(rs):
            for item in dataset:
                yield item

        custom_base = Mock()
        custom_base.iterate = iterate_large_dataset

        assert_equal(
            str(Resultset(base=custom_base)),
            "<Resultset: {0}... more>".format(
                ", ".join([
                    str(i) for i in dataset[:self.rs.max_repr_items + 1]])
            )
        )
