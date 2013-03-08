import logging

try:
    from urllib import urlencode
except ImportError:
    # python3 fix
    from urllib.parse import urlencode

from .utils import json
from .clients import Client
from .cursor import Cursor

__all__ = ("Connection", "Response",
           "Resultset")


logger = logging.getLogger(__name__)


class Connection(object):
    """Connetion to ArangoDB
    """

    _prefix = "http://"
    _url = None

    _pass_args = (
        "get",
        "put",
        "post",
        "delete"
    )

    def __init__(self, host="localhost",
                 port=8529, is_https=False,
                 client=None, **kwargs):
        """
         - ``client`` - this param provide ability
           to customize HTTP client
        """
        self.host = host
        self.port = port
        self.is_https = is_https
        self.client = client or Client
        self.additional_args = kwargs
        self._collection = None

    def __getattr__(self, name):
        """Handling different http methods and wrap requests
        with custom arguments
        """
        if name in self._pass_args:
            return self.requests_factory(method=name)

        raise AttributeError(
            "{cls} object has no attribute '{attr}'".format(
                cls=self.__class__,
                attr=name
            )
        )

    def requests_factory(self, method="get"):
        """Factory of requests wrapped around HTTP library
        and pass custom arguments provided by init of connection"""

        req = getattr(self.client, method)

        def requests_factory_wrapper(path, **kwargs):
            """To avoid auto JSON encoding of `data` keywords
            pass `rawData=True` argument
            """
            url = "{0}{1}".format(self.url, path)
            logger.debug(
                "'{method}' request to '{url}'".format(
                    method=method,
                    url=url
                ))

            # Py 2.7 only, yeah!
            kw = {k: v for k, v in self.additional_args}
            kw.update(kwargs)

            # NB: don't pass `data` argument in case
            # it's empty
            if "data" in kw and kw.get("data") == {}:
                kw.pop("data")

            expect_raw = kw.pop("_expect_raw", False)

            # Encode automatically data for POST/PUT
            if ("data" in kw and
                isinstance(kw.get("data"), (dict, list)) and
                    not kw.pop("rawData", False)):
                kw["data"] = json.dumps(kw.get("data"))

            return Response(
                url, req(url, **kw),
                args=kw,
                expect_raw=expect_raw)

        return requests_factory_wrapper

    @property
    def prefix(self):
        return self._prefix

    @property
    def url(self):
        """Build URL to the database, only once"""

        if self.is_https:
            self._prefix = "https://"

        if not self._url:
            self._url = "{prefix}{host}:{port}".format(
                prefix=self.prefix,
                host=self.host,
                port=self.port
            )

        return self._url

    def qs(self, path, **params):
        """Encode params  as GET argumentd and concat it with path"""
        return "{0}?{1}".format(path, urlencode(params))

    @property
    def collection(self):
        from .collection import Collections

        if not self._collection:
            self._collection = Collections(self)

        return self._collection

    def query(self, *args, **kwargs):
        """
        Proceed query (AQL) to the Database
        """
        return Cursor(self, *args, **kwargs)

    def __repr__(self):
        return "<Connection to ArangoDB ({0})>".format(self.url)


class Response(dict):
    """
    Representation of HTTP response with
    additional fields to make response more readable.
    """
    def __init__(self, url, response, args=None, expect_raw=False):
        self.url = url
        self.response = response
        self.status = response.status_code
        self.args = args or {}
        self.message = ""
        self._data = None

        try:
            if expect_raw is False:
                self.update({k: v
                             for k, v in
                             json.loads(response.text).items()})

        except (TypeError, ValueError) as e:
            msg = "Can't parse response from ArangoDB:"\
                " {0} (URL: {1}, Response: {2})".format(
                str(e),
                url,
                repr(response))

            logger.error(msg)
            self.status = 500
            self.message = msg

    @property
    def data(self):
        if self._data is None:
            try:
                self._data = json.loads(self.response.text)
            except TypeError:
                self._data = {}

        return self._data

    @property
    def is_error(self):
        if self.status not in [200, 201]:
            return True

        return False

    def __repr__(self):
        return "<Response for {0}: {1}>".format(repr(self.__dict__), self.url)


class Resultset(object):
    def __init__(self, base, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self._limit = None
        self._offset = 0

        self.base = base
        self.results = []
        self.position = 0

        self.max_repr_items = 4
        self._response = None
        self._count = None
        self._data = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    def _prepare(self):
        """Prepare data"""
        if not self.data and hasattr(self.base, "prepare_resultset"):
            self.base.prepare_resultset(
                self, args=self._args, kwargs=self._kwargs)

    @property
    def count(self):
        return len(self)

    @count.setter
    def count(self, value):
        self._count = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def limit(self, limit=0):
        self._limit = limit
        return self

    def offset(self, offset=0):
        self._offset = offset
        return self

    @property
    def first(self):
        """Return only first element from response"""
        self.limit(1)
        try:
            return list(self)[0]
        except IndexError:
            return None

    @property
    def last(self):
        """Return last element from response"""
        total = len(self.base._cursor(self))
        try:
            return list(self.limit(1).offset(total - 1))[0]
        except IndexError:
            return None

    def __len__(self):
        if self._count is None:
            self._count = len(self.base._cursor(self))

        return self._count

    def __iter__(self):
        self._prepare()
        return self.base.iterate(self)

    def __repr__(self):
        suff = ""
        items = []
        for i, item in enumerate(self):
            if i > self.max_repr_items:
                suff = "... more"
                break

            items.append(str(item))

        return "<Resultset: {0}{1}>".format(
            ", ".join(items), suff
        )
