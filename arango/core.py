import logging
import urllib
import urllib2

# from _profile import profile

from .utils import json

__all__ = ("Connection", "Response", "Resultset", "ResponseProxy")


logger = logging.getLogger(__name__)


class Requests(object):
    @classmethod
    def build_response(cls, d):
        return type('ArangoHttpResponse', (object,), d)

    @classmethod
    def get(cls, url, **kwargs):
        response = urllib2.urlopen(url)
        return cls.build_response({
            "text": response.read(),
            "status_code": response.code})

    @classmethod
    def post(cls, url, data=None):
        req = urllib2.Request(url=url, data=data)

        try:
            response = urllib2.urlopen(req)
            return cls.build_response({
                "text": response.read(),
                "status_code": response.code})
        except urllib2.HTTPError, e:
            return cls.build_response({
                "status_code": e.code,
                "text": e.reason})


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
                 port=8529, is_https=False, **kwargs):

        self.host = host
        self.port = port
        self.is_https = is_https

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
        """Factory of requests wrapped around requests library
        and pass custom arguments provided by init of connection"""

        req = getattr(Requests, method)

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
            if "data" in kw and \
                    isinstance(kw.get("data"), (dict, list)) \
                    and not kw.pop("rawData", False):
                kw["data"] = json.dumps(kw.get("data"))

            return Response(
                url, req(url, **kw),
                args=kw,
                expect_raw=expect_raw
            )

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
        return "{0}?{1}".format(path, urllib.urlencode(params))

    @property
    def collection(self):
        from .collection import Collections

        if not self._collection:
            self._collection = Collections(self)

        return self._collection

    def __repr__(self):
        return "<Connection to ArangoDB ({0})>".format(self.url)


class Response(dict):
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
                             json.loads(response.text).iteritems()})

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
            self._data = json.loads(self.response.text)
        return self._data

    @property
    def is_error(self):
        if self.status not in [200, 201]:
            return True

        return False

    def __repr__(self):
        return "<Response for {0}: {1}>".format(repr(self.__dict__), self.url)


class ResponseProxy(object):
    """
    Proxy object which should behave exactly like
    provided `result` argument or `resultset` property but
    provide additional ``response`` property to have
    access to Arango DB Response.

    .. warning::
        In case ``result`` **equal to ** ``None`` all attribute
        calls will be proxied directly to ``Response`` instance
    """
    def __init__(self, response, result=None):
        self._response = response

        # avoiding multiinheritance
        if isinstance(result, ResponseProxy):
            self._resultset = result.resultset

            result.resultset = None
            result.response = None
        else:
            self._resultset = result

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def resultset(self):
        return self._resultset

    @resultset.setter
    def resultset(self, value):
        self._resultset = value

    def __getattr__(self, attr, **kwargs):
        if attr in ("_resultset", "_response"):
            return self.__dict__[attr]

        if self.resultset is None:
            return getattr(self.response, attr)

        return getattr(self.resultset, attr)

    def __setattr__(self, attr, value):
        if attr in ("_resultset", "_response"):
            self.__dict__[attr] = value
            return

        if not self.resultset:
            return self.response.__setattr__(attr, value)

        return self.resultset.__setattr__(attr, value)

    def __nonzero__(self):
        return bool(self.resultset)

    def __len__(self):
        return len(self._resultset)

    def __iter__(self):
        return self._resultset.__iter__()

    def __eq__(self, item):
        return self.resultset == item

    def __call__(self, *args, **kwargs):
        return self.resultset.__call__(*args, **kwargs)

    def __str__(self):
        return str(self.resultset)

    def __repr__(self):
        return repr(self.resultset)

    def __getitem__(self, *args, **kwargs):
        return self.resultset.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.resultset.__setitem__(*args, **kwargs)

    def __get__(self, *args, **kwargs):
        return self.resultset.__get__(*args, **kwargs)


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
        self._count = 0
        self._data = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    def _prepare(self):
        """Prepare data"""
        if not self.data:
            self.base.prepare_resultset(
                self, args=self._args, kwargs=self._kwargs)

    @property
    def count(self):
        self._prepare()
        return self._count

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
        try:
            return list(self)[-1]
        except IndexError:
            return None

    def __len__(self):
        self._prepare()
        return len(self.data)

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
