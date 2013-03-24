import re

from .tests_base import TestsBase

from arango.aql import AQLQuery, F
# from nose.tools import assert_equal, assert_true, raises
from nose.tools import assert_equal


CLEANUP = lambda s: re.sub(r"\s+", " ", s).strip()


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
                RETURN {"user": obj,
                        "members": LENGTH(
                            FOR obj IN membership RETURN obj )}
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
                RETURN {"name": name, "email": email}
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
                RETURN {"name": obj.name, "email": obj.email}
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
                RETURN {"name": u.name, "email": email}
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
                RETURN {"u": u, "emails": emails}
            """))

        q2.iter("u")\
          .collect("emails", "u.email", into="g")\
          .result(u="u", g="g")\

        assert_equal(
            CLEANUP(q2.build_query()),
            CLEANUP(u"""
                FOR u IN user
                COLLECT emails = u.email INTO g
                RETURN {"u": u, "g": g}
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
                RETURN {"u": u, "g": MAX(
                    FOR c IN g RETURN c
                )}
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
