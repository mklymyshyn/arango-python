import sys
import logging

from .urllib2client import Urllib2Client


__all__ = ("Client",)


ISPY3 = sys.version_info >= (3, 0)

logger = logging.getLogger("arango.client")
Client = Urllib2Client


if ISPY3 is False:
    try:
        from .pycurlclient import PyCurlClient
        Client = PyCurlClient
    except Exception as e:
        logger.warning(
            u"Sorry, can't import PyCurlClient. Reason: %s", str(e))
