import logging


from .utils import json


__all__ = ("AQLQuery",)

logger = logging.getLogger(__name__)


class AQLQuery(object):
    """
    An abstraction layer to generate simple AQL queries.

    Usage::

        conn.u.iter("u")
              .over("PATHS(a, b, c)")
              .let("friends",
                   friends.iter("f")
                          .filter("u.id == f.userId"))
              .let("memberships",
                   memberships.iter("m")
                              .filter("u.id == m.userId"))
              .provide(user="u",
                       friends="friends",
                       numFriends="LENGTH(friends)",
                       memberShips="memberships")

    """
    def __init__(self, collection=None):
        self.collection = collection
        self.let_expr = []
        self.for_var = "obj"
        self.for_expr = None
        self.filter_expr = []
        self.collect_expr = []
        self.sort_expr = []
        self.limit_expr = None
        self.nested_expr = []
        self.return_expr = None

        self.bind = {}

    def iter(self, name):
        self.for_var = name
        return self

    def over(self, expression):
        self.for_expr = expression
        return self

    def nested(self, *args):
        self.nested_expr.extend(args)
        return self

    def let(self, name, value):
        return self

    def filter(self, *args):
        return self

    def collect(self, *args, **kwargs):
        return self

    def sort(self, *args):
        return self

    def limit(self, count=0, offset=0):
        return self

    def bind(self, **kwargs):
        self.bind = kwargs
        return self

    def result(self, *args, **kwargs):
        """
        Expression which will be added as ``RETURN`` of **AQL**.
        You can specify:

         - single name, like ``q.result("u")``
         - named arguments, like ``q.result(users="u", members="m")``
           which transform into ``RETURN {users: u, members: m}``
         - ``fields`` named argument, like ``q.result(fields={"key-a": "a"})``
           to work with names which are not supported by Python syntax.
        """
        self.return_expr = args or kwargs.get("fields") or kwargs
        return self

    @property
    def expr_return(self):
        """
        Build expression
        """
        return_expr = self.return_expr or self.for_var
        if isinstance(return_expr, dict):
            pairs = []
            for key, expr in self.return_expr.items():
                # support of nested queries
                if issubclass(type(expr), AQLQuery):
                    expr = expr.build_query()

                pairs.append('"{}": {}'.format(key, expr))
            return "{{{}}}".format(", ".join(pairs))
        elif return_expr and isinstance(return_expr, (tuple, list)):
            return_expr = return_expr[0]

        return return_expr

    @property
    def expr_for(self):
        """
        Build FOR expression
        """
        for_expr = self.for_expr or self.collection

        return for_expr

    @property
    def expr_nested(self):
        if not self.nested_expr:
            return ""

        queries = []

        for n, expr in enumerate(self.nested_expr):
            if not issubclass(type(expr), AQLQuery):
                raise ValueError(
                    u"Nested expressions have to be"
                    u"subclass of AQLQuery")

            queries.append(expr.build_nested_query(n + 1))

        return "\n".join(queries)

    def build_nested_query(self, n):
        """
        Build simplified query ONLY as nested:
        skip all paramas except ``for_var`` and ``for_expr``
        """
        for_var = self.for_var
        if for_var == "obj":
            for_var = "obj{}".format(n)

        return u"FOR {for_var} IN {for_expr}".format(
            for_var=for_var,
            for_expr=self.expr_for)

    def build_query(self):
        # Building main part
        return u"""
            FOR {for_var} IN
                {for_expr}
                {for_nested}
            RETURN
                {return_expr}
        """.format(
            for_var=self.for_var,
            for_expr=self.expr_for,
            for_nested=self.expr_nested,
            return_expr=self.expr_return)
