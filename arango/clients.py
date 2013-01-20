import urllib2

import StringIO
import pycurl


class RequestsBase(object):
    """
    Base class to implement HTTP client
    """
    @classmethod
    def build_response(cls, d):
        return type('ArangoHttpResponse', (object,), d)

    def get(*args, **kwargs):
        raise NotImplementedError

    def post(*args, **kwargs):
        raise NotImplementedError

    def put(*args, **kwargs):
        raise NotImplementedError

    def delete(*args, **kwargs):
        raise NotImplementedError


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


class PyCurlClient(RequestsBase):
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
