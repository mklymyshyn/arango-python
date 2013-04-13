import logging
import functools
try:
    from urllib2 import urlopen, HTTPError, Request
except ImportError:
    # for Python 3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

from .base import RequestsBase

__all__ = ("Urllib2Client",)

logger = logging.getLogger("arango.urllib")


def safe_request(func):
    """
    Handle 404 errors and so on
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            content = e.read()
            e.close()
            return RequestsBase.build_response(
                e.code, e.msg, e.headers, content)

    return wrap


class Urllib2Client(RequestsBase):
    """
    If no PyCURL bindings available or
    client forced by hands. Quite useful for PyPy.
    """
    _config = {}
    encoding = "utf-8"

    @classmethod
    def config(cls, encoding=None, **kwargs):
        cls._config.update(kwargs)

        if encoding is not None:
            cls.encoding = encoding

    @classmethod
    def parse_response(cls, r, content=None):
        headers = {}

        if "dict" in r.headers.__dict__:
            headers.update(r.headers.__dict__["dict"])
        else:
            # Python3
            headers.update(dict(r.headers.raw_items()))

        content = content.decode(cls.encoding)
        return cls.build_response(r.code, r.msg, headers, content)

    @classmethod
    @safe_request
    def get(cls, url, **kwargs):
        response = urlopen(url)
        content = response.read()
        response.close()
        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def post(cls, url, data=None):
        if data is None:
            data = ""

        req = Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data.encode(cls.encoding))

        response = urlopen(req, **cls._config)
        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def put(cls, url, data=None):
        if data is None:
            data = ""

        req = Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data.encode(cls.encoding))
        req.get_method = lambda: "put"
        response = urlopen(req)

        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def delete(cls, url, data=None):
        req = Request(url)
        req.get_method = lambda: "delete"
        response = urlopen(req)
        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)
