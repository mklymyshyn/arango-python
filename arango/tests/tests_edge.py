
from mock import Mock, patch

from nose.tools import assert_equal, assert_true, raises, \
    assert_not_equal

from arango.edge import Edges, Edge
from arango.utils import json
from arango.exceptions import EdgeAlreadyCreated

from .tests_document import TestDocumentBase


__all__ = ("TestEdge",)


class TestEdge(TestDocumentBase):
    def setUp(self):
        super(TestEdge, self).setUp()
        self.c = self.conn.collection.test

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
        body = body if body is not None else {}
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

        edge = self.c.edges.create(
            from_doc,
            to_doc,
            body)

        patcher.stop()

        return edge

    def test_collection_shortcut(self):
        assert_equal(type(self.c.edges), Edges)

    def test_edge_create(self):
        body = dict(
            key="value",
            num=1)

        doc1 = self.create_document(123, body)
        doc2 = self.create_document(234, body)

        edge = self.create_edge(doc1, doc2, body)

        for k in body.keys():
            assert_true(k in edge._body)

    @raises(EdgeAlreadyCreated)
    def test_edge_create_of_created(self):
        body = {"value": "test"}

        edge = Edge(self.c)
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

        doc1 = self.create_document(123, body)
        doc2 = self.create_document(234, body)

        edge = self.create_edge(doc1, doc2, body)

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

    def test_edge_deletion(self):
        body = {"value": "test"}

        doc1 = self.create_document(123, body)
        doc2 = self.create_document(234, body)

        edge = self.create_edge(doc1, doc2, body)

        patcher = self.delete_edge_response_mock()
        patcher.start()

        edge._id = 1
        edge._rev = 1
        edge._body = {}

        assert_true(edge.delete())

        assert_equal(edge.id, None)
        assert_equal(edge.rev, None)
        assert_equal(edge.body, None)
        assert_equal(edge.from_document, None)
        assert_equal(edge.to_document, None)

        patcher.stop()

    def test_edge_comparsion(self):
        body = {"value": 1}
        doc1 = self.create_document(123, body)
        doc2 = self.create_document(234, body)

        edge1 = self.create_edge(doc1, doc2, body)
        edge2 = self.create_edge(doc1, doc2, body)

        mock_from = Mock()
        mock_to = Mock()

        with patch("arango.document.Document.lazy_loader"):
            edge1._from = mock_from
            edge1._to = mock_to
            edge2._from = mock_from
            edge2._to = mock_to

            assert_equal(edge1, edge2)

            edge2._to_document = None
            edge2._to = Mock()
            assert_not_equal(edge1, edge2)
