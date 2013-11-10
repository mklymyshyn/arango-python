import os
import types
import unittest

from nose import SkipTest
from mock import patch, MagicMock
from arango.clients import Client

from arango.clients.base import RequestsBase
from arango.core import Connection

__all__ = ("TestsBase",)


class TestsBase(unittest.TestCase):

    methods = ["post", "put", "get", "delete"]

    def setUp(self):
        if "NOSMOKE" in os.environ:
            raise SkipTest

        self.conn = Connection()
        for m in self.methods:
            setattr(
                self, m,
                patch.object(self.conn.client, m, MagicMock()))
            getattr(self, m).start()

        self.url = "{0}{1}".format(self.conn.url, "/document")

    def tearDown(self):
        for m in self.methods:
            try:
                getattr(self, m).stop()
            except RuntimeError:
                pass

        self.conn.client = Client

    def build_mock_response(self, *args, **kwargs):
        return RequestsBase.build_response(
            200, "{}", [], "{}")

    def response_mock(self, status_code=200, text='', method="get"):
        mock_method = lambda self, *a, **kw: RequestsBase.build_response(
            status_code, "", [], text)

        mock_method = types.MethodType(mock_method, Client)
        patcher = patch.object(Client, method, mock_method)

        return patcher
