import logging
import requests

__all__ = ('Connection',)


logger = logging.getLogger(__name__)


class Connection(object):
    """Connetion to AvocadoDB
    """

    _prefix = 'http://'
    _url = None

    _pass_args = (
        'get',
        'put',
        'post',
        'delete'
    )

    def __init__(self,
            host='localhost',
            port=8529,
            is_https=False,
            **kwargs):

        self.host = host
        self.port = port
        self.is_https = is_https

        self.additional_args = kwargs

    def __getattr__(self, name):
        if name in self._pass_args:
            return self.requests_factory(method=name)

        raise AttributeError(
            "{cls} object has no attribute '{attr}'".format(
                cls=self.__class__,
                attr=name
            )
        )

    def requests_factory(self, method='get'):
        """Factory of requests wrapped around requests library
        and pass custom arguments provided by init of connection"""

        req = getattr(requests, method)

        def wrap(path, **kwargs):
            url = "%s%s" % (self.url, path)
            logger.debug(
                "Make `{method}` request to `{url}".format(
                    method=method,
                    url=url
                ))
            return req(url, *kwargs)

        return wrap

    @property
    def prefix(self):
        return self._prefix

    @property
    def url(self):
        """Build URL to the database, only once"""

        if self.is_https:
            self._prefix = 'https://'

        if not self._url:
            self._url = "{prefix}{host}:{port}".format(
                prefix=self.prefix,
                host=self.host,
                port=self.port
            )

        return self._url

    def __repr__(self):
        return "<Connection to AvocadoDB ({0})>".format(self.url)


conn = Connection()
