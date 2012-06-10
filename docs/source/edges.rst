.. _edges:

Working with Edges
------------------

To specify vertex ``from_document`` and ``to_document`` should be
specified during **Edge** creation::


    from arango import collection as c

    c.test.create()

    # create FROM document
    from_doc = c.test.documents.create({
        "sample_key": "sample_value"
    })

    # create TO document
    to_doc = c.test.documents.create({
        "sample_key1": "sample_value1"
    })

    # creating edge with custom data
    c.test.edges.create(from_doc, to_doc, {"custom": 1})

    # getting edge by document
    c.test.edges(from_doc)

    # getting with direction
    c.test.edges(from_doc, direction="in")

    assert c.test.edges(from_doc).first().from_document == from_doc
    assert c.test.edges(from_doc).first().to_document == to_doc


Edges for Collection instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edges are accessible via collection instance for example ``connection.collection.sample_collection.edges``. Usually this expressions looks lot shorter.

Basically via `edges` shortcut accessible **Edges Proxy** - Proxy object which have several shortcuts and produce ``Resultset`` object.

Below described basic method within ``Edges`` proxy:

.. autoclass:: arango.edge.Edges
    :members: create, delete, update, count


Making queries
~~~~~~~~~~~~~~

It's easy enough to making queries. Last line of :ref:`edges` example consist
from simple Edges query::

    ...

    # getting with direction
    c.test.edges(from_doc, direction="in")

There's possible to specify ``direction`` of edges to:

 #. ``in``
 #. ``out``
 #. ``any``

More details in :term:`Edges REST Api` documentation of **ArangoDB**


Edge instance methods
~~~~~~~~~~~~~~~~~~~~~

Edge instances methods consist from basic **CRUD** methods and additional
methods specific obly for **Edges**:

.. autoclass:: arango.edge.Edge
    :members: create, update, delete, save, body, response,
              from_document, to_document
