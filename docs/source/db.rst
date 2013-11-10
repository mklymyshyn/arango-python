.. _database:

Database
--------

Database is abstraction over single one database within ArangoDB.
With basic API you can **create**, **delete** or **get details** about
particular database.


.. note::
    Currently ArangoDB REST API support of getting list of databases.
    Driver doesn't support this functionality at the moment. However it's
    quite easy to implement using
    ``conn.connection.client`` and ``conn.url(db_prefix=False)``.


.. testcode::

    from arango import create

    c = create(db="test")
    c.database.create()

    c.database.info["name"] == "test"
    c.database.delete()


.. autoclass:: arango.db.Database
    :members: create, info, delete
