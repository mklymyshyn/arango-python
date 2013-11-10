Python driver for ArangoDB
--------------------------

Driver for **ArangoDB REST API** inrerface, `arangodb.org <http://arangodb.org>`_

.. image:: https://travis-ci.org/joymax/arango-python.png?branch=master


Installation
************
::

  pip install arango


Usage
*****
To start work with **ArangoDB** try following example::

    from arango import create

    # create connection to database
    conn = create(db="test")
    conn.database.create()

    # create collection with name `test_collection`
    conn.test_collection.create()

    # create document
    conn.test_collection.documents.create({"sample_key": "sample_value"})

    # get first document
    doc = conn.test_collection.documents().first
    # get document body
    doc.body

    # get all documents in collection

    for doc in conn.test_collection.query.execute():
      print doc.id

For more details please read `Documentation <http://arangodb-python-driver.readthedocs.org/en/latest/>`_


Supported Python interpreters and versions:

 - cPython 3.3
 - cPython 2.7
 - PyPy 1.9

Supported **ArangoDB versions**: *1.4x*

Developed by `Maksym Klymyshyn <http://ua.linkedin.com/in/klymyshyn>`_


Changelog
*********

0.2.0
~~~~~~

 * Added support for multiple databases


0.1.8
~~~~~~

 * Added support of **bulk inserts**
