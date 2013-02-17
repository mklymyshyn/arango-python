.. _queries:

Making queries with AQL
-----------------------

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


Custom data wrapper
~~~~~~~~~~~~~~~~~~~

It's not necessary to wrap all documents within
``Document`` object.