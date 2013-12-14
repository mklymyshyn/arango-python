.. testsetup::

    from arango import create
    c = create(db="test")
    c.database.create()

.. _collections:

Collections
-----------

Collections is something similar to tables in SQL databases world. Collection
consist from **documents** and :ref:`edges`.

It's quite easy to create collection::

    from arango import create

    # here we define connection to Arango
    c = create(db="test")

    # make sure database exists
    c.database.create()

    # here we creating collection explicitly
    c.test.create()

    assert len(c.collections()) == 1

    # here we creating edges collection
    c.test_edges.create_edges()

    assert len(c.collections()) == 2

Collection ``test`` being created.

.. note::
    It's not necessary to create collection before adding documents to it.
    You can specify ``createCollection`` as keyed argument during creation
    of new **Document**


If you don't want to create collection explicitly use

.. testcode::

    # here we creating document AND collection
    c.test.documents.create({"sample": 1}, createCollection=True)


Get list of collections
~~~~~~~~~~~~~~~~~~~~~~~

To get list of **Collections** simply call connection like `c()`

For example:

.. testcode::

    # here we creating collection explicitly
    c.test.create()

    assert c(), ["test"]


.. autoclass:: arango.collection.Collections
    :members: __call__, database, __getitem__, __getattr__



.. _collection:

Collection
~~~~~~~~~~

**Arango DB** provide rich API to manipulate collections
Collection instance methods is quite rich. Here is
documentation which describe :term:`Collections REST Api`

.. autoclass:: arango.collection.Collection
    :members: cid, info, properties, query,
              create, create_edges, delete, rename,
              count, __len__,
              index, documents, edges,
              load, unload, truncate

