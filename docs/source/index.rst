ArangoDB Driver for Python
==========================

Features support
----------------

Driver for Python is not entirely completed. It supports
**Connections to ArangoDB with custom options**,
**Collections**, **Documents**, **Indexes** **Cursors**
and partially **Edges**.

Presentation about
`Graph Databases and Python <http://www.slideshare.net/MaxKlymyshyn/odessapy2013-pdf>`_
with real-world examples how to work with **arango-python**.

.. _arangodb-description:

  **ArangoDB** is an open-source database with a flexible data model
  for documents, graphs, and key-values. Build high performance
  applications using a convenient sql-like query language or
  JavaScript/Ruby extensions.

More details about **ArangoDB** on `official website <http://arangodb.org>`_.
Some `blog posts <http://blog.klymyshyn.com/search/label/arangodb>`_ about this driver.

Getting started
---------------

Installation
~~~~~~~~~~~~~

Library is in early alpha so it's not on PyPi yet. To install use `pip`::

  pip install arango


Usage example
~~~~~~~~~~~~~

It's quite simple to start work with **ArangoDB**:

.. doctest::

    from arango import create

    # create connection to database
    conn = create(db="test")

    # create database itself
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

    # work with AQL
    conn.test_range.create()

    for n in range(10):
      conn.test_range.documents.create({
        "n": n,
        "mult": n * n})

    conn.test_range.query.filter(
      filter("n == 1 || n == 5")).execute()

    # delete database
    conn.database.delete()


Contents
---------
.. toctree::
   :maxdepth: 2

   collections
   documents
   queries
   indexes
   edges
   db
   exceptions
   glossary
   guidelines


Arango versions, Platforms and Python versions
----------------------------------------------

Supported versions of ArangoDB: **1.1x** and **1.2x**

This release support **Python 3.3**, *Python 2.7*, *PyPy 1.9*.



Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

