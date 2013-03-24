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
        # providing details when multiple keywords or
        # structures are provided.
        # TODO: covert any nested elements to proper AQL
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
    """
    def __init__(self, collection=None, no_cache=False):
        self.collection = collection
        self.let_expr = []
        self.for_var = "obj"
        self.for_expr = None
        self.filter_expr = []
        self.collect_expr = []
        self.sort_expr = []
        self.limit_expr = None, None
        self.nested_expr = []
        self.return_expr = None

        self.bind = {}
        self._built_query = None
        self._no_cache = no_cache

    def iter(self, name):
        self.for_var = name
        return self

    def over(self, expression):
        """
        Implementation of FOR operation::

            FOR variable-name IN expression

        """
        self.for_expr = expression
        return self

    def nested(self, *args):
        self.nested_expr.extend(args)
        return self

    def let(self, name, value):
        """
        LET operation::

            LET variable-name = expression

        """
        self.let_expr.append((name, value))
        return self

    def filter(self, condition):
        """
        FILTER operation::

            FILTER a==b && c==d

        """
        self.filter_expr.append(condition)
        return self

    def collect(self, *pairs, **kwargs):
        """
        COLLECT operation::

            COLLECT variable-name = expression
            COLLECT variable-name = expression INTO groups

        """

        if len(pairs) % 2 != 0:
            raise ValueError(
                u"Arguments should be pairs variable-name and expression")

        into = kwargs.get("into")
        self.collect_expr.append((pairs, into))
        return self

    def sort(self, *args):
        """
        """
        self.sort_expr.extend(args)
        return self

    def limit(self, count, offset=None):
        """
        """
        self.limit_expr = count, offset
        return self

    def bind(self, **kwargs):
        """
        """
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

    def process_expr(self, expr, parentheses=True):
        if issubclass(type(expr), Func):
            return expr.build_query()

        if issubclass(type(expr), AQLQuery):
            if parentheses:
                return u"({})".format(expr.build_query())

            return expr.build_query()

        return expr

    @property
    def expr_return(self):
        """
        Build expression
        """

        return_expr = self.return_expr or self.for_var

        if isinstance(return_expr, dict):
            pairs = []
            for key, expr in self.return_expr.items():
                expr = self.process_expr(expr)
                pairs.append('"{}": {}'.format(key, expr))
            return "{{{}}}".format(", ".join(pairs))
        elif return_expr and isinstance(return_expr, (tuple, list)):
            return_expr = return_expr[0]

        if issubclass(type(return_expr), Func):
            return_expr = return_expr.build_query()

        return return_expr

    @property
    def expr_for(self):
        for_expr = self.for_expr or self.collection

        return self.process_expr(for_expr)

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
            pairs.append(u"LET {name} = {expr}".format(
                name=name, expr=self.process_expr(expr)))

        return u"\n".join(pairs)

    @property
    def expr_filter(self):
        conds = []
        for cond in self.filter_expr:
            conds.append(u"FILTER {}".format(cond))

        return u"\n".join(conds)

    @property
    def expr_collect(self):
        collect = []
        for pairs, into in self.collect_expr:
            exprs = []
            into = u" INTO {}".format(into) if into else u""

            for name, expr in zip(pairs[0::2], pairs[1::2]):
                exprs.append(u"{} = {}".format(name, self.process_expr(expr)))

            collect.append(u"COLLECT {pairs}{into}".format(
                pairs=", ".join(exprs), into=into))

        return u"\n".join(collect)

    @property
    def expr_sort(self):
        if not self.sort_expr:
            return u""

        return u"SORT {}".format(", ".join(self.sort_expr))

    @property
    def expr_limit(self):
        count, offset = self.limit_expr

        if count is None and offset is None:
            return u""

        if offset is None:
            return u"LIMIT {}".format(count)

        return u"LIMIT {}, {}".format(offset, count)

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
        """
        Here we building query. Wohoo.
        """
        if self._built_query is not None and self._no_cache is False:
            return self._built_query

        query = u"""
            FOR {for_var} IN {for_expr}
                {for_nested}
                {let_expr}
                {filter_expr}
                {collect_expr}
                {sort_expr}
                {limit_expr}
            RETURN
                {return_expr}
        """.format(
            for_var=self.for_var,
            for_expr=self.expr_for,
            for_nested=self.expr_nested,
            let_expr=self.expr_let,
            filter_expr=self.expr_filter,
            collect_expr=self.expr_collect,
            sort_expr=self.expr_sort,
            limit_expr=self.expr_limit,
            return_expr=self.expr_return)

        logger.debug(query)
        self._built_query = query
        return query

    def execute(self):
        # TODO: create cursor
        # TODO: build query
        pass

F = FuncFactory()
