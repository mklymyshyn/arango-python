.. _indexes:

Indexes
-------

Indexes are used to allow fast access to documents. For each collection there is always the primary index which is a hash index for the document identifier.

Usage example::

    from arango import create

    # here we define connection to Arango
    c = create()

    # here we creating collection explicitly
    c.test.create()

    # create `hash` index for two fields: `name` and `num`,
    # not unque
    c.test.index.create(["name", "num"])

    # create unique `hash` index for `slug` field
    c.test.index.create(
        "slug",
        index_type="hash",
        unique=True
    )


.. autoclass:: arango.index.Index
    :members: __call__, create, delete, get, response
