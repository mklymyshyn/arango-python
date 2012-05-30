import logging
import requests
import urllib

from .collection import Collections
from .utils import json

__all__ = ("Connection", "Response", "Resultset")


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

    def __init__(self,
            host="localhost",
            port=8529,
            is_https=False,
            **kwargs):

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

        req = getattr(requests, method)

        def requests_factory_wrapper(path, **kwargs):
            """To avoid auto JSON encoding of `data` keywords
            pass `rawData=True` argument
            """
            url = "%s%s" % (self.url, path)
            logger.debug(
                "'{method}' request to '{url}'".format(
                    method=method,
                    url=url
                ))

            # Py 2.7 only, yeah!
            kw = dict((k, v) for k, v in self.additional_args)
            kw.update(kwargs)

            # NB: don't pass `data` argument in case
            # it's empty
            if "data" in kw and kw.get("data") == {}:
                kw.pop("data")

            # Encode automatically data for POST/PUT
            if "data" in kw and \
                    isinstance(kw.get("data"), (dict, list)) \
                    and not kw.pop("rawData", False):
                kw["data"] = json.dumps(kw.get("data"))

            return Response(url, req(url, **kw), args=kw)

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
        if not self._collection:
            self._collection = Collections(self)

        return self._collection

    def __repr__(self):
        return "<Connection to ArangoDB ({0})>".format(self.url)


class Response(dict):
    def __init__(self, url, response, args=None):
        self.url = url
        self.response = response
        self.status = response.status_code
        self.args = args or {}
        self.message = ""

        # TODO: load it lazy
        try:
            self.update(dict((k, v) \
                for k, v in json.loads(response.text).iteritems()))

        except (TypeError, ValueError) as e:
            msg = "Can't parse response from ArangoDB:"\
                " {0} (URL: {1}, Response: {2})".format(
                str(e),
                url,
                repr(response)
            )

            logger.error(msg)
            self.status = 500
            self.message = msg

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

    def limit(self, limit=0):
        self._limit = limit
        return self

    def offset(self, offset=0):
        self._offset = offset
        return self

    def first(self):
        """Return only first element from response"""
        self.limit(1)
        try:
            return list(self)[0]
        except IndexError:
            return None

    def last(self):
        """Return last element from response"""
        try:
            return list(self)[-1]
        except IndexError:
            return None

    def __iter__(self):
        return self.base.query(self)
