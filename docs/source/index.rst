ArangoDB Driver for Python
==========================

Features support
----------------

Driver for Python is not entirely completed. It supports
**Connections to ArangoDB with custom options**,
**Collections**, **Documents**, **Indexes** **Cursors**
and partially **Edges**.

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


Contents
---------
.. toctree::
   :maxdepth: 2

   collections
   documents
   queries
   indexes
   edges
   exceptions
   glossary
   guidelines


Arango versions, Platforms and Python versions
-----------------------------

Supported versions of ArangoDB: **1.1x** and **1.2x**

This release support **Python 3.3**, *Python 2.7*, *PyPy 1.9*.



Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

