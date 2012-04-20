
from .tests_document import TestDocumentBase

from nose.tools import assert_equal, assert_true, raises
from avocado.edge import Edge
from avocado.utils import json

from avocado.exceptions import EdgeAlreadyCreated


__all__ = ("TestEdge",)


class TestEdge(TestDocumentBase):
    def setUp(self):
        super(TestEdge, self).setUp()
        self.c = self.conn.collection.test
        self.e = self.c.e

    def delete_edge_response_mock(self):
        return self.response_mock(
            status_code=204,
            text=json.dumps(dict(
                _from="7848004/9289796",
                _to="7848004/9355332",
                _rev=30967598,
                _id=1,
                error=False,
                code=204
            )),
            method="delete"
        )

    def create_edge_response_mock(self, body=None):
        body = body if body != None else {}
        defaults = dict(
            _from="7848004/9289796",
            _to="7848004/9355332",
            _rev=30967598,
            _id="7848004/9683012",
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

    def create_edge(self, from_doc, to_doc, body):
        patcher = self.create_edge_response_mock(body=body)
        patcher.start()

        doc, response = self.c.e.create(
            from_doc,
            to_doc,
            body
        )
        patcher.stop()

        return doc, response

    def test_collection_shortcut(self):
        assert_equal(type(self.e), Edge)
        assert_equal(type(self.e), type(self.c.edge))

    def test_edge_create(self):
        body = dict(
            key="value",
            num=1
        )

        doc1, r1 = self.create_document(123, body)
        doc2, r2 = self.create_document(234, body)

        url = lambda p: "{0}{1}".format(
            self.conn.url,
            self.conn.qs(
                self.e.EDGE_PATH,
                **p
            )
        )

        params = {
            "collection": "test",
            "from": doc1.id,
            "to": doc2.id
        }

        edge, response = self.create_edge(doc1, doc2, body)
        assert_equal(response.url, url(params))

        for k in body.keys():
            assert_true(k in edge._body)

    @raises(EdgeAlreadyCreated)
    def test_edge_create_of_created(self):
        body = {"value": "test"}
        edge, response = self.c.e.create(None, None, body)
        edge._id = 1
        edge.create(None, None, body)

    def test_get_edge_fields(self):
        body = {
            "array": [1, 2, 3],
            "options": None,
            "number": 5.5,
            "tree": {
                "sample1": "1",
                "sample2": "2"
            }
        }

        doc1, r1 = self.create_document(123, body)
        doc2, r2 = self.create_document(234, body)

        edge, response = self.create_edge(doc1, doc2, body)

        assert_equal(
            edge.get("array", default=None),
            [1, 2, 3]
        )

        for key in body.keys():
            assert_true(key in edge.get().keys())

        assert_equal(
            edge["tree"]["sample1"],
            body["tree"]["sample1"]
        )
