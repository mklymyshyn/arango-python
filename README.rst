Python driver for ArangoDB
--------------------------

Driver for **ArangoDB REST API** inrerface, `arangodb.org <http://arangodb.org>`_

.. image:: https://travis-ci.org/joymax/arango-python.png?branch=master


Features support
****************

Driver for Python is incomplete. It supports at the moment:
**Connections to ArangoDB with custom options**,
**Collections**, **Documents**, **Indexes** **Cursors**
and have partial support of **Edges**

Installation
************
::

  pip install arango


Usage
*****
To start work with **ArangoDB** try following example::

    from arango import create

    # create connection to database
    voca = create()
    # create collection with name `test_collection`
    voca.test_collection.create()
    # create document
    voca.test_collection.documents.create({"sample_key": "sample_value"})
    # get first document
    doc = voca.test_collection.documents().first
    # get document body
    doc.body

    # get all documents in collection

    for doc in voca.test_collection.query.execute():
      print doc.id

For more details please read `Documentation <http://arangodb-python-driver.readthedocs.org/en/latest/>`_


Supported Python interpreters and versions:

 - cPython 3.3
 - cPython 2.7
 - PyPy 1.9

Supported **ArangoDB versions**: *1.1x* and *1.2x*

Developed by Maksym Klymyshyn
