import sys
import time

from datetime import datetime

from arango import create
from arango.document import Document
from arango.clients import Client

try:
    import simplejson as json
except ImportError:
    import json


class Timer(object):
    def __init__(self):
        self.start = datetime.now()
        self.end = None

    @property
    def result(self):
        self.end = datetime.now()
        t2 = self.end - self.start
        return t2.seconds * 1000 + t2.microseconds * 0.001

    @classmethod
    def measure(cls, func):
        timer = cls()
        func()
        return timer.result


def cleanup(conn):
    try:
        db_coll = getattr(conn, collection_name)
    except:
        print "Not connected to a database."
        raise

    created = db_coll.create()

    if created and created.is_error:
        try:
            db_coll.delete()
            time.sleep(4)
            print "Deleted collection '%s'." % collection_name
        except:
            print "Could not delete collection '%s'." % collection_name

    db_coll.create(collection_name)
    time.sleep(3)

    print "Created collection '%s'." % collection_name

    return getattr(conn, collection_name)


def get_connection():

    db_host = '127.0.0.1'
    db_port = 8529
    db_conn = None

    try:
        db_conn = create(host=db_host, port=db_port)
    except:
        print "Not connected to a database."
        raise

    return db_conn


collection_name = 'testdocs_py'
collection_items = int(sys.argv[1])

conn = get_connection()
documents = cleanup(conn).documents


def pycurl_client():
    """
    Simple example
    """
    import pycurl

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        documents.create(body)


def urllib2_client():
    """
    Simple example with urllib2
    """
    from arango.clients.urllib2client import Urllib2Client
    default_client = documents.connection.client
    documents.connection.client = Urllib2Client
    documents.connection.client.config(timeout=3)

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        try:
            documents.create(body)
        except Exception, exc:
            print "Connection timeout on {} iteration".format(i)

    documents.connection.client = default_client


def requests_client():
    """
    Simple example
    """

    from arango.clients.requestsclient import RequestsClient
    default_client = documents.connection.client
    documents.connection.client = RequestsClient

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        documents.create(body)

    documents.connection.client = default_client


def plain_request():
    """
    Use only core functionality, no abstraction
    """
    conn = documents.connection

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        conn.post(
            conn.qs(
                Document.DOCUMENT_PATH,
                createCollection=False),
            data=body,
            _expect_raw=True)


def plain_request_urllib2():
    """
    Use only core functionality, no abstraction
    """
    conn = documents.connection

    from arango.clients.urllib2client import Urllib2Client
    default_client = documents.connection.client
    documents.connection.client = Urllib2Client
    documents.connection.client.config(timeout=3)

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        conn.post(
            conn.qs(
                Document.DOCUMENT_PATH,
                createCollection=False),
            data=body,
            _expect_raw=True)

    documents.connection.client = default_client


def plain_request_requests():
    """
    Use only core functionality, no abstraction
    """
    conn = documents.connection

    from arango.clients.requestsclient import RequestsClient
    default_client = documents.connection.client
    documents.connection.client = RequestsClient

    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        conn.post(
            conn.qs(
                Document.DOCUMENT_PATH,
                createCollection=False),
            data=body,
            _expect_raw=True)

    documents.connection.client = default_client


def pycurl_client_raw():
    """
    PyCURL
    """
    import StringIO
    import pycurl

    url = "http://127.0.0.1:8529/_api/document?collection=testdocs_py"

    for i in range(collection_items):
        c = pycurl.Curl()

        body = {"value": "test_%d" % i}
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, json.dumps(body))

        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()

        b.getvalue()


try:
    print "SIMPLE (PYCURL/Default): "\
        "Inserted: %d items, insertion time: %.3fms." % (
            collection_items, Timer.measure(pycurl_client))
except ImportError:
    print "SIMPLE: Install PyCURL binding to measure this kind of client"

documents = cleanup(conn).documents
print "SIMPLE (URLLIB2): Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(urllib2_client))

documents = cleanup(conn).documents
print "SIMPLE (REQUESTS): Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(requests_client))

documents = cleanup(conn).documents
print "REST API: Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(plain_request))

documents = cleanup(conn).documents
print "REST API (requests): Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(plain_request_requests))

documents = cleanup(conn).documents
print "REST API (urllib2): Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(plain_request_urllib2))


documents = cleanup(conn).documents
try:
    print "PYCURL + REST API: Inserted: %d items, insertion time: %.3fms." % (
        collection_items, Timer.measure(pycurl_client_raw))
except ImportError:
    print "PyCURL NOT INSTALLED, IGNORE"
