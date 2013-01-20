import sys
import time
import StringIO

import pycurl

from datetime import datetime

from arango import create
from arango.document import Document
from arango.core import Requests

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


def simple():
    """
    Simple example
    """
    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        documents.create(body)


def raw():
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


def plain_request():
    """
    Example which just using REST API without
    any driver
    """
    url = "http://127.0.0.1:8529/_api/document?collection=testdocs_py"
    for i in range(collection_items):
        body = {"value": "test_%d" % i}
        Requests.post(url, data=json.dumps(body))


def pycurl_client():
    """
    PyCURL
    """
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

        data = b.getvalue()


print "SIMPLE: Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(simple))

documents = cleanup(conn).documents
print "RAW: Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(raw))

documents = cleanup(conn).documents
print "REST API: Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(plain_request))

documents = cleanup(conn).documents
print "PYCURL + REST API: Inserted: %d items, insertion time: %.3fms." % (
    collection_items, Timer.measure(pycurl_client))
