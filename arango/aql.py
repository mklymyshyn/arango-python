import logging

from .cursor import Cursor

__all__ = ("AQLQuery", "F", "V", "S")

logger = logging.getLogger(__name__)


class Variable(object):
    """
    AQL Variable
    """
    def __init__(self, value):
        self.value = value
        self.invert = False

    def __invert__(self):
        self.invert = True
        return self

    def __repr__(self):
        return "<AQL Variable: {}>".format(self.value)


class Func(object):
    """
    AQL Function instance
    """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args

    def proceed_list(self, l):
        """
        Process all arguments of Function
        """
        result = []

        for item in l:
            if isinstance(item, dict):
                result.append(self.proceed_dict(item))
                continue
            if issubclass(type(item), AQLQuery):
                result.append(item.build_query())
                continue
            if issubclass(type(item), Variable):
                if item.invert is True:
                    result.append('"{}"'.format(item.value))
                else:
                    result.append(item.value)
                continue

            result.append(item)

        return result

    def proceed_dict(self, d):
        """
        Process all arguments which is dict
        """
        pairs = []

        for key, val in d.items():
            if isinstance(val, (list, tuple)):
                val = self.proceed_list(val)
            elif isinstance(val, dict):
                val = self.proceed_dict(val)
            elif issubclass(type(val), AQLQuery):
                val = val.build_query()
            elif issubclass(type(val), Variable):
                val = val.value
            else:
                val = "\"{}\"".format(val)

            pairs.append("\"{name}\": {value}".format(
                name=key, value=val))

        return "{{{}}}".format(", ".join(pairs))

    def build_query(self):
        """
        Proceed list of arguments
        """
        return "{}({})".format(self.name, ", ".join(
            self.proceed_list(self.args)))


class FuncFactory(object):
    """
    AQL Function factory.
    This is ``F`` object in ``arango.aql`` module.

    .. code::

        from arango.aql import F

        c.test.query.over(F.PATH("a", "b", "c")).execute()

    Execute query::

        FOR obj IN PATH(a, b, c)
        RETURN obj

    """
    def __getattribute__(self, name):
        def f(*args, **kwargs):
            return Func(name, *args, **kwargs)

        return f


def V(name):
    """
    Factory for defining variables in requests.
    By default in functions arguments which are dicts
    all fields wrapped with double quoutes ``"``.
    To specify members of variables defined above
    ``V`` factory should be used.

    .. testcode::

        expect = 'MERGE({"user1": u.name}, {"user1": "name"})'
        assert F.MERGE(
            {"user1": V("u.name")},
            {"user1": "name"}).build_query() == expect

    """
    return Variable(name)


class AQLQuery(object):
    """
    An abstraction layer to generate simple AQL queries.
    """
    def __init__(self, connection=None, collection=None, no_cache=False):
        self.collection = collection
        self.connection = connection

        self.let_expr = []
        self.for_var = "obj"
        self.for_expr = None
        self.filter_expr = []
        self.collect_expr = []
        self.sort_expr = []
        self.limit_expr = None, None
        self.nested_expr = []
        self.return_expr = None

        self.bind_vars = {}
        self._built_query = None
        self._no_cache = no_cache
        self.cursor_args = {}

    def cursor(self, **kwargs):
        """
        Method to provide custom arguments for
        :py:attr:`arango.cursor.Cursor` instance. All
        keywords arguments except ``bindVars`` may be changed.

        """
        self.cursor_args = kwargs
        return self

    def iter(self, name):
        """
        ``FOR`` cycle temporary variable,
        ``variable-name`` in AQL expression::

            FOR variable-name IN expression

        """
        self.for_var = name
        return self

    def over(self, expression):
        """
        ``expression`` in ``FOR`` cycle

        .. code::

            FOR variable-name IN expression

        """
        self.for_expr = expression
        return self

    def nested(self, *args):
        self.nested_expr.extend(args)
        return self

    def let(self, name, value):
        """
        Add ``LET`` operation

        .. code::

            LET variable-name = expression

        """
        self.let_expr.append((name, value))
        return self

    def filter(self, condition):
        """
        Filter query by condition ``condition``.
        It's possible to add multiple filter
        expressions.

        .. code::

            FILTER condition

        For exmaple code in python

        .. code::

            c.test.query
                  .filter("a==b && c==d")
                  .filter("d == m")

        """
        self.filter_expr.append(condition)
        return self

    def collect(self, *pairs, **kwargs):
        """
        Specify ``COLLECT`` operators, it's possible
        to use it multiple times

        .. code::

            COLLECT variable-name = expression
            COLLECT variable-name = expression INTO groups

        In python

        .. code::

            c.test.query
                  .collect("emails", "u.email")
                  .collect("names", "u.name", into="eml")
                  .result(emails="eml",
                          names="names")

        """

        if len(pairs) % 2 != 0:
            raise ValueError(
                "Arguments should be pairs variable-name and expression")

        into = kwargs.get("into")
        self.collect_expr.append((pairs, into))
        return self

    def sort(self, *args):
        """
        Sort result by criterias from ``args``.

        .. code::

            query.sort("u.email", "u.first_name DESC")
                 .sort("u.last_name")
        """
        self.sort_expr.extend(args)
        return self

    def limit(self, count, offset=None):
        """
        Limit results with ``count`` items. By default
        ``offset`` is ``0``.

        .. code::

            query.limit(100, offset=10)

        """
        self.limit_expr = count, offset
        return self

    def bind(self, **kwargs):
        """
        Bind some data to AQL Query. Technically it's
        just a proxy to :py:attr:`arango.cursor.Cursor.bind`
        method which attach variables to the ``Cursor``.

        It's mostly for avoding any kind of query injetions.

        .. testcode::

            data = c.test.query.filter("obj.name == @name")\\
                              .bind(name="Jane")\\
                              .execute().first

            assert data != None
            assert data.body["name"] == "Jane"

        """
        self.bind_vars.update(kwargs)
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
                return "({})".format(expr.build_query())

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
            for key in sorted(self.return_expr):
                expr = self.process_expr(self.return_expr[key])
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
                    "Nested expressions have to be"
                    "subclass of AQLQuery")

            queries.append(expr.build_nested_query(n + 1))

        return "\n".join(queries)

    @property
    def expr_let(self):
        pairs = []
        for name, expr in self.let_expr:
            pairs.append("LET {name} = {expr}".format(
                name=name, expr=self.process_expr(expr)))

        return "\n".join(pairs)

    @property
    def expr_filter(self):
        conds = []
        for cond in self.filter_expr:
            conds.append("FILTER {}".format(cond))

        return "\n".join(conds)

    @property
    def expr_collect(self):
        collect = []
        for pairs, into in self.collect_expr:
            exprs = []
            into = " INTO {}".format(into) if into else ""

            for name, expr in zip(pairs[0::2], pairs[1::2]):
                exprs.append("{} = {}".format(name, self.process_expr(expr)))

            collect.append("COLLECT {pairs}{into}".format(
                pairs=", ".join(exprs), into=into))

        return "\n".join(collect)

    @property
    def expr_sort(self):
        if not self.sort_expr:
            return ""

        return "SORT {}\n".format(", ".join(self.sort_expr))

    @property
    def expr_limit(self):
        count, offset = self.limit_expr

        if count is None and offset is None:
            return ""

        if offset is None:
            return "LIMIT {}\n".format(count)

        return "LIMIT {}, {}\n".format(offset, count)

    def build_nested_query(self, n):
        """
        Build simplified query ONLY as nested:
        skip all paramas except ``for_var`` and ``for_expr``
        """
        for_var = self.for_var
        if for_var == "obj":
            for_var = "obj{}".format(n)

        return "FOR {for_var} IN {for_expr}\n".format(
            for_var=for_var,
            for_expr=self.expr_for)

    def build_query(self):
        """
        Build AQL query and return it as
        a string. This is good start to
        debug generated AQL queries.
        """
        if self._built_query is not None and self._no_cache is False:
            return self._built_query

        query = """
            FOR {for_var} IN {for_expr}
                {for_nested}{let_expr}{filter_expr}
                {collect_expr}{sort_expr}{limit_expr}
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

    def execute(self, wrapper=None):
        """
        Execute query: create cursor, put binded variables
        and return instance of :py:attr:`arango.cursor.Cursor` object
        """
        self.cursor_args.update({"bindVars": self.bind_vars})
        if wrapper is not None:
            self.cursor_args.update({"wrapper": wrapper})

        return Cursor(
            self.connection, self.build_query(), **self.cursor_args)

    def __repr__(self):
        return "<AQLQuery: {}>".format(self.build_query())


F = FuncFactory()
