.. _collections:

Collections
-----------

Collections is something similar to tables in SQL databases world. Collection
consist from **documents** and :ref:`edges`.

It's quite easy to create collection::

    from arango import create

    # here we define connection to Arango
    c = create()

    # here we creating collection explicitly
    c.test.create()


Collection ``test`` being created.

.. note::
    It's not necessary to create collection before adding documents to it.
    You can specify ``createCollection`` as keyed argument during creation
    of new **Document**


If you don't want to create collection explicitly use::

    from arango import create

    # here we define connection to Arango
    c = create()

    # here we creating document AND collection
    c.test.documents.create({"sample": 1}, createCollection=True)


Get list of collections
~~~~~~~~~~~~~~~~~~~~~~~

To get list of **Collections** simply call connection like `c()`

For example::

    from arango import create

    # here we define connection to Arango
    c = create()

    # here we creating collection explicitly
    c.test.create()

    assert c(), ["test"]


.. autoclass:: arango.collection.Collections
    :members: __call__




Manipulate collection
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: arango.collection.Collection
    :members: cid, response, info,
              create, delete, update, rename,
              count, __len__, param,
              index, documents, edges,
              load, unload, truncate

