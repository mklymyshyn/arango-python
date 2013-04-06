.. testsetup::

    from arango import collection as c
    from arango.aql import F, V

    c.test.delete()
    c.test.create()

    c.test.docs.create({
        "name": "John", "email": "john@example.com",
        "last_name": "McDonald"})
    c.test.docs.create({
        "name": "Jane", "email": "jane@example.com",
        "last_name": "McDonald"})


.. _queries:

AQL Queries
-----------

Query Builder is abstraction layer around **AQL**
to work with it in more *pythonic* way.

Simplest start point is to use
:py:attr:`arango.collection.Collection.query`.

Simple example:

.. testcode::

    from arango import collection as c

    # create collection
    c.test1.create()

    c.test1.docs.create({"name": "John", "email": "john@example.com"})
    c.test1.docs.create({"name": "Jane", "email": "jane@example.com"})

    c.test1.query.filter("obj.name == 'John'").build_query()

    c.test1.delete()

will generate AQL query::

    FOR obj IN test
        FILTER obj.name == 'John'
    RETURN
        obj


.. _queries_api:

AQL Query Builder API
~~~~~~~~~~~~~~~~~~~~~

This API typically accesible via ``query`` method of
collection instance.

Builder methods to generate AQL query:

.. autoclass:: arango.aql.AQLQuery
    :members: iter, over, nested, let, filter, collect,
              sort, limit, bind, cursor, result, execute, build_query


Helpers to work with query variables and functions.

.. automodule:: arango.aql
    :members: V, FuncFactory


Making raw queries with AQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now it's possible to querieng database by
using :term:`Arango Query Language (AQL)`.

This functionality implementation based on
:term:`HTTP Interface for AQL Query Cursors`
and provide lazy iterator over dataset and
with ability to customize (wrap) result item by
custom wrapper.

Alternative way to do such king of functionality
is by using :term:`Documents REST Api` which is
not implemented in driver.


.. autoclass:: arango.cursor.Cursor
    :members: first, last, bind


Custom data wrapper for raw queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's not necessary to wrap all documents within
``Document`` object. ``Cursor`` do it by default
but you can provide custom wrapper by overriding
``wrapper`` argument during execution of
``connection.query`` method.

.. note::
    Also it's possible to provide custom wrapper via
    :py:attr:`arango.aql.AQLQuery.cursor` method during
    building of the **AQL** query:

    .. code::

        c.test1.query.cursor(wrapper=lambda conn, item: item)
                     .filter("obj.name == 'John'").build_query()


``wrapper`` should accept two arguments:

  - ``connection`` - first argument, current connection
    instnace
  - ``item`` - dictionary with data provided from ArangoDB query

.. testcode::

    from arango import c

    wrapper = lambda conn, item: item

    c.collection.test.create()
    c.collection.test.documents.create({"1": 2})

    # create connection to database
    for item in c.query("FOR d in test RETURN d", wrapper=wrapper):
        item
