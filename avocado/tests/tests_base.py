import unittest
import requests

from mock import patch

from avocado.core import Connection


__all__ = ("TestsBase",)


class TestsBase(unittest.TestCase):

    methods = ["post", "put", "get", "delete"]

    def setUp(self):
        for m in self.methods:
            setattr(self, m, patch("requests.{0}".format(m)))
            getattr(self, m).start()

        self.conn = Connection()
        self.url = "{0}{1}".format(self.conn.url, "/document")

    def tearDown(self):
        for m in self.methods:
            getattr(self, m).stop()
