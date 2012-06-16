ArangoDB Driver for Python
==========================

.. warning::
    This is **PRE ALPHA** release, so several required features
    **are not supported**!


Features support
----------------

Driver for Python is incomplete. It supports at the moment:
**Connections to ArangoDB with custom options**,
**Collections**,
**Documents**,
**Edges**,
**Indexes**

What's not supported in current version:

  #. Ability to making Queries
  #. Cursors

Platforms and Python versions
-----------------------------

This release support *Python 2.6*, *Python 2.7* and *PyPy 1.8*.

Next in chain are *PyPy 1.9* and *Python 3.3*

Contents
---------
.. toctree::
   :maxdepth: 2

   collections
   documents
   edges
   exceptions
   glossary
   guidelines


Getting started
---------------

Installation
~~~~~~~~~~~~~

Library isn't public yet so just add it to your ``PYTHONPATH``


Usage example
~~~~~~~~~~~~~

It's quite simple to start work with **ArangoDB**::

    from arango import create

    # create connection to database
    voca = create()

    # create collection with name `test_collection`
    voca.test_collection.create()

    # create document
    voca.test_collection.documents.create({
        "sample_key": "sample_value"
    })

    # get first document
    voca.test_collection.documents().first()

    # get document body
    voca.test_collection.documents().first().body

    # get value of key `sample_key`
    voca.test_collection.documents().first().get("sample_key")



Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

