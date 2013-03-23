import re

from .tests_base import TestsBase

from arango.aql import AQLQuery
# from nose.tools import assert_equal, assert_true, raises
from nose.tools import assert_equal


CLEANUP = lambda s: re.sub(r"\s+", " ", s).strip()


class TestAqlGeneration(TestsBase):
    def test_simple(self):
        q = AQLQuery(collection="user")

        assert_equal(
            CLEANUP(q.build_query()),
            "FOR obj IN user RETURN obj")

        assert_equal(
            CLEANUP(q.over("user").build_query()),
            "FOR obj IN user RETURN obj")

        assert_equal(
            CLEANUP(q.iter("u").over("user").build_query()),
            "FOR u IN user RETURN u")

        assert_equal(
            CLEANUP(q.iter("usr").over("user").build_query()),
            "FOR usr IN user RETURN usr")

        assert_equal(
            CLEANUP(q.iter("usr")
                     .over("user")
                     .result("usr").build_query()),
            "FOR usr IN user RETURN usr")

    def test_field_names(self):
        q1 = AQLQuery()
        q1.iter("user")\
          .over("users")\
          .result(
              fields={
                  "user-first-name": "user.first_name",
                  "user-last-name": "user.last_name",
                  "user*age": "user['*age']"
              })

        assert_equal(
            CLEANUP(q1.build_query()),
            CLEANUP(u"""
                FOR user IN users RETURN
                    {"user-last-name": user.last_name,
                    "user-first-name": user.first_name,
                    "user*age": user[\'*age\']}
            """))

    def test_nested_queries(self):
        q1 = AQLQuery(collection="user")
        q2 = AQLQuery(collection="membership")

        assert_equal(
            CLEANUP(q1.nested(q2)
                      .result(user="obj",
                              member="obj1")
                      .build_query()),
            CLEANUP("""
                FOR obj IN user
                    FOR obj1 IN membership
                RETURN {"member": obj1, "user": obj}
            """)
        )

    def test_sub_queries_in_return(self):
        pass
