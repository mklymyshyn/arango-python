import re

from .tests_base import TestsBase

from arango.aql import AQLQuery, F, V
from nose.tools import assert_equal


def CLEANUP(s):
    """
    Normalize spaces in queries
    """

    REPLACEMENTS = (
        (r"\(\s*", "("),
        (r"\s*\)", ")"),
        (r"\s*([\{\}])\s*", "\\1"),
        (r"\s+", " "))

    for ex, rpl in REPLACEMENTS:
        s = re.sub(ex, rpl, s, flags=re.S | re.M)
    return s.strip()


class TestAqlGeneration(TestsBase):
    def test_simple(self):
        q = AQLQuery(collection="user", no_cache=True)

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
                    {"user*age": user[\'*age\'],
                    "user-first-name": user.first_name,
                    "user-last-name": user.last_name
                    }
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
            """))

    def test_sub_queries_in_return(self):
        q1 = AQLQuery(collection="user")
        q2 = AQLQuery(collection="membership")

        assert_equal(
            CLEANUP(q1.result(user="obj",
                              members=F.LENGTH(q2))
                      .build_query()),
            CLEANUP("""
                FOR obj IN user
                RETURN {"members": LENGTH(
                            FOR obj IN membership RETURN obj ),
                        "user": obj}
            """))

    def test_let_expr(self):
        q = AQLQuery(collection="user")
        q.let("name", "u.first_name")\
         .let("email", F.LENGTH("u.email"))\
         .result(name="name", email="email")\

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP("""
                FOR obj IN user
                    LET name = u.first_name
                    LET email = LENGTH(u.email)
                RETURN {"email": email, "name": name}
            """))

    def test_let_subquery_expr(self):
        m = AQLQuery(collection="memberships")
        c = AQLQuery(collection="memberships")
        q = AQLQuery(collection="user")

        q.let("membership", m.iter("m1").result(
            within="m1.within",
            count=F.LENGTH(c.iter("m")
                            .result(groups="m.groups"))))\
         .result(name="obj.name", email="obj.email")

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP(u"""
                FOR obj IN user
                    LET membership = (
                        FOR m1 IN memberships
                        RETURN {"count": LENGTH(
                                FOR m IN memberships
                                RETURN
                                {"groups": m.groups} ),
                         "within": m1.within} )
                RETURN {"email": obj.email, "name": obj.name}
            """))

    def test_filter_expr(self):
        q = AQLQuery(collection="user")
        q.iter("u")\
         .filter("u.age >= 18 && u.name != ''")\
         .filter("u.email.length > 10")\
         .result(name="u.name", email="email")\

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP("""
                FOR u IN user
                FILTER u.age >= 18 && u.name != ''
                FILTER u.email.length > 10
                RETURN {"email": email, "name": u.name}
            """))

    def test_collect_expr(self):
        q1 = AQLQuery(collection="user")
        q2 = AQLQuery(collection="user")
        q3 = AQLQuery(collection="user")
        q1.iter("u")\
          .collect("emails", "u.email")\
          .result(u="u", emails="emails")\

        assert_equal(
            CLEANUP(q1.build_query()),
            CLEANUP(u"""
                FOR u IN user
                COLLECT emails = u.email
                RETURN {"emails": emails, "u": u}
            """))

        q2.iter("u")\
          .collect("emails", "u.email", into="g")\
          .result(u="u", g="g")\

        assert_equal(
            CLEANUP(q2.build_query()),
            CLEANUP(u"""
                FOR u IN user
                COLLECT emails = u.email INTO g
                RETURN {"g": g, "u": u}
            """))

        sq = AQLQuery(collection="members")
        q3.iter("u")\
          .collect("emails", "u.email", into="g")\
          .result(u="u", g=F.MAX(sq.iter("c").over("g")))

        assert_equal(
            CLEANUP(q3.build_query()),
            CLEANUP(u"""
                FOR u IN user
                COLLECT emails = u.email INTO g
                RETURN {
                    "g": MAX(
                        FOR c IN g RETURN c
                    ),
                    "u": u
                }
            """))

    def test_sort(self):
        q = AQLQuery(collection="user")
        q.iter("u")\
         .sort("u.email DESC", "u.name")

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP("""
                FOR u IN user
                SORT u.email DESC, u.name
                RETURN u
            """))

    def test_limit(self):
        # - LIMIT, no offset
        # - LIMIT, with offset
        q = AQLQuery(collection="user")
        q.iter("u")\
         .limit(10)

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP("""
                FOR u IN user
                LIMIT 10
                RETURN u
            """))

        q = AQLQuery(collection="user")
        q.iter("u")\
         .limit(10, offset=100)

        assert_equal(
            CLEANUP(q.build_query()),
            CLEANUP("""
                FOR u IN user
                LIMIT 100, 10
                RETURN u
            """))

    def test_function_factory(self):
        assert_equal(
            F.LENGTH("a").build_query(),
            "LENGTH(a)")

        assert_equal(
            F.PATH("a", "b", "c").build_query(),
            "PATH(a, b, c)")

        assert_equal(
            CLEANUP(F.PATH("a", "b", "c").build_query()),
            "PATH(a, b, c)")

        assert_equal(
            CLEANUP(F.PATH("a", "b", "c").build_query()),
            CLEANUP(F.PATH(V("a"), V("b"), V("c")).build_query()))

        assert_equal(
            CLEANUP(F.MERGE(
                {"user1": {"name": "J"}},
                {"user2": {"name": "T"}}).build_query()),
            CLEANUP(u"""
                MERGE(
                    {"user1": {"name": "J"}},
                    {"user2": {"name": "T"}})
            """))

        assert_equal(
            CLEANUP(F.MERGE(
                {"user1": {"name": V("u.name")}},
                {"user2": {"name": "T"}}).build_query()),
            CLEANUP(u"""
                MERGE(
                    {"user1": {"name": u.name}},
                    {"user2": {"name": "T"}})
            """))

    def test_bind(self):
        q = AQLQuery(collection="user")

        assert_equal(
            q.bind(**{"data": "test"}).execute().bindVars,
            {"data": "test"})

    def test_cursor_args(self):
        q = AQLQuery(collection="user")
        assert_equal(
            q.cursor(batchSize=1).execute().batchSize,
            1)
