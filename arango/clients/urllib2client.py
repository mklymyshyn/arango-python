from contextlib import closing
import logging
import functools
import urllib2

from .base import RequestsBase

__all__ = ("Urllib2Client",)

logger = logging.getLogger("arango.urllib2")


def safe_request(func):
    """
    Handle 404 errors and so on
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except urllib2.HTTPError, e:
            e.close()
            return RequestsBase.build_response(
                e.code, e.msg, e.headers, "")

    return wrap


class Urllib2Client(RequestsBase):
    """
    If no PyCURL bindings available or
    client forced by hands. Quite useful for PyPy.
    """
    _config = {}

    @classmethod
    def config(cls, **kwargs):
        cls._config.update(kwargs)

    @classmethod
    def parse_response(cls, r, content=None):
        headers = {}
        headers.update(r.headers.__dict__["dict"])
        return cls.build_response(r.code, r.msg, headers, content)

    @classmethod
    @safe_request
    def get(cls, url, **kwargs):
        response = urllib2.urlopen(url)
        content = response.read()
        response.close()
        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def post(cls, url, data=None):
        if data is None:
            data = ""

        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data)
        response = urllib2.urlopen(req, **cls._config)

        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def put(cls, url, data=None):
        if data is None:
            data = ""

        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data)
        req.get_method = lambda: "put"
        response = urllib2.urlopen(req)

        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)

    @classmethod
    @safe_request
    def delete(cls, url, data=None):
        req = urllib2.Request(url)
        req.get_method = lambda: "delete"
        response = urllib2.urlopen(req)
        content = response.read()
        response.close()

        return cls.parse_response(response, content=content)
