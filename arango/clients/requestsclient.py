import logging

try:
    import requests
except ImportError:
    raise ImportError(
        "Please, install ``requests`` library to use this client")

from .base import RequestsBase

__all__ = ("RequestsClient",)

logger = logging.getLogger("arango.requests")


class RequestsClient(RequestsBase):
    """
    If no PyCURL bindings available or
    client forced by hands. Quite useful for PyPy.
    """
    _config = {}

    @classmethod
    def config(cls, **kwargs):
        cls._config.update(kwargs)

    @classmethod
    def get(cls, url, **kwargs):
        r = requests.get(url, **cls._config)

        return cls.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    @classmethod
    def post(cls, url, data=None):
        if data is None:
            data = ""

        r = requests.post(url, data=data, **cls._config)

        return cls.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    @classmethod
    def put(cls, url, data=None):
        if data is None:
            data = ""

        r = requests.put(url, data=data, **cls._config)

        return cls.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    @classmethod
    def delete(cls, url, data=None):
        r = requests.delete(url, **cls._config)

        return cls.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)
