
from nose.tools import assert_equal
from arango.utils import json

from .tests_base import TestsBase


class TestsUtils(TestsBase):
    def test_json_loads_dumps(self):
        resource = {"a": 1, "b": [1, 2]}

        result = json.dumps(json.loads("""{"a": 1, "b": [1, 2]}"""))
        assert_equal(
            json.dumps(resource),
            result
        )

        assert_equal(
            json.loads(result),
            resource
        )
