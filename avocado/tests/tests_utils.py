import unittest

from nose.tools import assert_equal
from avocado.utils import json


class TestsUtils(unittest.TestCase):
    def test_json_loads_dumps(self):
        resource = {
            "a": 1,
            "b": [1, 2]
        }

        result = """{"a": 1, "b": [1, 2]}"""
        assert_equal(
            json.dumps(resource),
            result
        )

        assert_equal(
            json.loads(result),
            resource
        )
