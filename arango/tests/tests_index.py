
from nose.tools import assert_equal, raises, assert_true, assert_false

from .tests_base import TestsBase


from arango.utils import json
from arango.exceptions import EmptyFields, WrongIndexType


__all__ = ("TestIndex",)


class TestIndex(TestsBase):
    def setUp(self):
        super(TestIndex, self).setUp()
        self.c = self.conn.collection.test

    def delete_response_mock(self):
        return self.response_mock(
            status_code=200,

            text=json.dumps(dict(
                _rev=30967598,
                _id=1,
                error=False,
                code=200
            )),
            method="delete"
        )

    def list_response_mock(self):
        data = {
            "code": 200,
            "indexes": [
                {
                    "fields": [
                       "_id"
                    ],
                    "id": 0,
                    "type": "primary"
                }
            ],
            "error": False,
            "identifiers": {
                "0": {
                    "fields": [
                        "_id"
                    ],
                    "id": 0,
                    "type": "primary"
                }
            }
        }

        return self.response_mock(
            status_code=200,
            text=json.dumps(data),
            method="get"
        )

    def create_response_mock(self, body=None):
        body = body if body != None else {}
        defaults = {
            "code": 201,
            "geoJson": False,
            "fields": [
                "b"
            ],
            "id": 96609552,
            "type": "geo",
            "isNewlyCreated": True,
            "error": False
        }

        defaults.update(body)

        patcher = self.response_mock(
            status_code=201,
            text=json.dumps(defaults),
            method="post"
        )

        return patcher

    def test_create(self):
        url = "{0}{1}".format(
            self.conn.url,
            self.c.index.CREATE.format(self.c.cid)
        )

        response = self.c.index.create(
            ["name"],
            type=self.c.index.HASH,
            unique=False
        )

        assert_equal(response.url, url)

    @raises(WrongIndexType)
    def test_create_wrong_type(self):
        self.c.index.create(
            ["name"],
            type="wrong"
        )

    @raises(EmptyFields)
    def test_create_empty_fields(self):
        self.c.index.create(
            []
        )

    @raises(WrongIndexType)
    def test_create_empty_fields_wrong_type_first(self):
        self.c.index.create(
            [],
            type="wrong"
        )

    def test_list(self):
        url = "{0}{1}".format(
            self.conn.url,
            self.c.index.INDEXES.format(self.c.cid)
        )

        patcher = self.list_response_mock()
        patcher.start()
        ids, response = self.c.index()
        patcher.stop()

        assert_equal(
            response.url,
            url
        )

        assert_equal(
            ids,
            response.get("identifiers")
        )

    def test_delete(self):
        url = "{0}{1}".format(
            self.conn.url,
            self.c.index.DELETE.format(self.c.cid, "1")
        )

        is_deleted, response = self.c.index.delete("1")

        assert_equal(
            response.url,
            url
        )

        assert_false(is_deleted)

    def test_delete_response(self):
        patcher = self.delete_response_mock()
        patcher.start()

        is_deleted, response = self.c.index.delete(1)
        patcher.stop()

        assert_true(is_deleted)

    def test_get_index(self):
        url = "{0}{1}".format(
            self.conn.url,
            self.c.index.READ.format(self.c.cid, "1")
        )

        response = self.c.index.get(1)

        assert_equal(
            url,
            response.url
        )
