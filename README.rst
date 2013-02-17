Python driver for ArangoDB
--------------------------

Driver for **ArangoDB REST API** inrerface, `arangodb.org <http://arangodb.org>`_

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
    for doc in voca.connection.query("FOR d in test_collection RETURN d"):
      print doc.id

For more details please read `Documentation <http://arangodb-python-driver.readthedocs.org/en/latest/>`_


Supported Python interpreters and versions:

 - cPython 2.7
 - PyPy 1.9


Developed by Maksym Klymyshyn
