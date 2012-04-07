
from tests_base import TestsBase

from nose.tools import assert_equal, raises
#from mock import Mock

from avocado.document import Document
from avocado.utils import json
from avocado.exceptions import DocumentAlreadyCreated


class TestDocument(TestsBase):
    def setUp(self):
        super(TestDocument, self).setUp()
        self.c = self.conn.collection.test
        self.d = self.c.d

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
                self.d.CREATE_DOCUMENT_PATH,
                **p
            )
        )

        params = dict(
            collection="test"
        )

        doc, response = self.d.create(body)
        assert_equal(response.url, url(params))

        params.update({
            "createCollection": True
        })
        doc, response = self.d.create(body, createCollection=True)
        assert_equal(response.url, url(params))

        test_args = {"data": json.dumps(body)}
        assert_equal(response.args, test_args)

    @raises(DocumentAlreadyCreated)
    def test_document_create_of_created(self):
        body = {"value": "test"}
        doc, response = self.c.d.create(body)
        doc._id = 1
        doc.create(body)
