.. _queries:

AQL Query Buidler
-----------------

Query Builder is abstraction layer around **AQL**
to work with it in more *pythonic* way.

Simplest start point is to use
:py:attr:`arango.collection.Collection.query`.

Simple example:

.. testcode::

    from arango import collection as c

    # create collection
    c.test.create()

    c.test.docs.create({"name": "John", "email": "john@example.com"})
    c.test.docs.create({"name": "Jane", "email": "jane@example.com"})

    c.test.query.filter("name == 'John'").build_query()

will generate AQL query::

    FOR obj IN test
        FILTER name == 'John'
    RETURN
        obj



Making raw queries with AQL
---------------------------

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


Custom data wrapper for raw queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's not necessary to wrap all documents within
``Document`` object. ``Cursor`` do it by default
but you can provide custom wrapper by overriding
``wrapper`` argument during execution of
``connection.query`` method.

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
