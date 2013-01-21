import logging
import urllib2

from .base import RequestsBase

__all__ = ("Urllib2Client",)

logger = logging.getLogger("arango.urllib2")


class Urllib2Client(RequestsBase):
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
