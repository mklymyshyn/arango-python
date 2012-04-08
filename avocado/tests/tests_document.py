
from tests_base import TestsBase

from nose.tools import assert_equal, raises, assert_false

from avocado.document import Document
from avocado.utils import json
from avocado.exceptions import DocumentAlreadyCreated


__all__ = ("TestDocument",)


class TestDocument(TestsBase):
    def setUp(self):
        super(TestDocument, self).setUp()
        self.c = self.conn.collection.test
        self.d = self.c.d

    def create_response_mock(self, body=None):
        body = body if body != None else {}
        defaults = dict(
            _rev=30967598,
            _id=1,
            error=False,
            code=201
        )

        defaults.update(body)

        patcher = self.response_mock(
            status_code=201,
            text=json.dumps(defaults),
            method="post"
        )

        return patcher

    def create_document(self, body):
        patcher = self.create_response_mock()
        patcher.start()

        doc, response = self.c.d.create(body)
        patcher.stop()

        return doc, response

    def test_collection_shortcut(self):
        assert_equal(type(self.d), Document)
        assert_equal(type(self.d), type(self.c.document))

    def test_document_create(self):
        body = dict(
            key="value",
            num=1
        )

        url = lambda p: "{0}{1}".format(
            self.conn.url,
            self.conn.qs(
                self.d.DOCUMENT_PATH,
                **p
            )
        )

        params = dict(
            collection="test"
        )

        doc, response = self.create_document(body)
        assert_equal(response.url, url(params))
        assert_equal(doc._body, body)

        params.update({
            "createCollection": True
        })

        patcher = self.create_response_mock()
        patcher.start()

        doc, response = self.c.d.create(body, createCollection=True)
        assert_equal(response.url, url(params))

        test_args = {"data": json.dumps(body)}
        assert_equal(response.args, test_args)

        patcher.stop()

    @raises(DocumentAlreadyCreated)
    def test_document_create_of_created(self):
        body = {"value": "test"}
        doc, response = self.c.d.create(body)
        doc._id = 1
        doc.create(body)

    def test_document_deletion(self):
        body = {"value": "test"}
        url = "{0}{1}".format(
            self.conn.url,
            self.d.DELETE_DOCUMENT_PATH.format("1"),
        )

        doc, response = self.create_document(body)
        assert_equal(doc._body, body)

        patcher = self.response_mock(
            status_code=204,
            text=json.dumps(dict(
                _rev=30967598,
                _id=1,
                error=False,
                code=204
            )),
            method="delete"
        )

        patcher.start()

        doc._id = 1
        doc._rev = 1
        doc._body = {}

        response = doc.delete()

        assert_equal(response.url, url)

        assert_equal(doc.id, None)
        assert_equal(doc.rev, None)
        assert_equal(doc.doc, None)

        patcher.stop()

    def test_get_document_fields(self):
        body = {
            "array": [1, 2, 3],
            "options": None,
            "number": 5.5,
            "tree": {
                "sample1": "1",
                "sample2": "2"
            }
        }

        doc, response = self.create_document(body)

        assert_equal(
            doc.get("array", default=None),
            [1, 2, 3]
        )

        assert_equal(
            doc.get(),
            body
        )

        assert_equal(
            doc["tree"]["sample1"],
            body["tree"]["sample1"]
        )

    def test_get_document_arr(self):
        body = [1, 2, 3]

        doc, response = self.create_document(body)

        assert_equal(doc.doc, body)
        assert_equal(doc.get(2), body[2])

        # support to getting item by numeric indexes
        # in case we storing plain arrays
        assert_equal(doc[1], body[1])

    def test_document_update_simple(self):
        doc, response = self.create_document({"value": 1})

        assert_equal(doc["value"], 1)
        doc["value"] = 2

        assert_equal(doc["value"], 2)
        assert_false("name" in doc.doc)
        doc.update({"name": "testing", "value": 3})
        assert_equal(doc["name"], "testing")
        assert_equal(doc["value"], 3)

        doc, response = self.create_document([1, 2, 3])
        assert_equal(len(doc.doc), 3)
        assert_equal(doc.doc[1], 2)

        doc.update([4, 5, 6])
        assert_equal(len(doc.doc), 6)
        assert_equal(doc.doc[1], 2)
        assert_equal(doc.doc[3], 4)

    def test_document_update_complex(self):
        doc, response = self.create_document({
            "value": {
                "level1": {
                    "level2": [1, 2, 3]
                }
            }
        })

        doc.doc.get("value").get("level1")["level2"] = [3, 4, 5]

        assert_equal(
            doc.doc.get("value").get("level1").get("level2"),
            [3, 4, 5]
        )
