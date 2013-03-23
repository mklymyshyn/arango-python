import logging


__all__ = ("AQLQuery", "F")

logger = logging.getLogger(__name__)


class Func(object):
    """
    AQL Function instance
    """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        # TODO: here we need to improve
        # providing details
        self.expr = args[0]

    def build_query(self):
        if issubclass(type(self.expr), AQLQuery):
            return u"{}({})".format(self.name, self.expr.build_query())

        return u"{}({})".format(self.name, self.expr)


class FuncFactory(object):
    """
    AQL Function factory
    """
    def __getattribute__(self, name):
        def f(*args, **kwargs):
            return Func(name, *args, **kwargs)

        return f


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
        self.let_expr.append([name, value])
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
                if issubclass(type(expr), (AQLQuery, Func)):
                    expr = expr.build_query()

                pairs.append('"{}": {}'.format(key, expr))
            return "{{{}}}".format(", ".join(pairs))
        elif return_expr and isinstance(return_expr, (tuple, list)):
            return_expr = return_expr[0]

        if issubclass(type(return_expr), Func):
            return_expr = return_expr.build_query()

        return return_expr

    @property
    def expr_for(self):
        """
        Build FOR expression
        """
        for_expr = self.for_expr or self.collection

        if issubclass(type(for_expr), Func):
            for_expr = for_expr.build_query()

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

    @property
    def expr_let(self):
        pairs = []
        for name, expr in self.let_expr:
            if issubclass(type(expr), Func):
                expr = expr.build_query()
            elif issubclass(type(expr), AQLQuery):
                expr = "({})".format(expr.build_query())

            pairs.append(u"LET {name} = {expr}".format(
                name=name, expr=expr))

        return u"\n".join(pairs)

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
                {let_expr}
                {for_nested}
            RETURN
                {return_expr}
        """.format(
            for_var=self.for_var,
            for_expr=self.expr_for,
            for_nested=self.expr_nested,
            let_expr=self.expr_let,
            return_expr=self.expr_return)


F = FuncFactory()
