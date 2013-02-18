.. testsetup::

    from arango import create

    c = create()
    c.test.create()

    # create FROM document
    from_doc = c.test.documents.create({
        "sample_key": "sample_value"
    })

    # create TO document
    to_doc = c.test.documents.create({
        "sample_key1": "sample_value1"
    })

.. _edges:

Edges
-----

Edges is entyties which represend connection between two
documents. The main idea of **Edges** is that you can buidl your own
graph (tree) between set of documents and make search within hierarchy of
documents.

To specify vertex ``from_document`` and ``to_document`` should be
specified during **Edge** creation


.. testcode::

    from arango import create

    c = create()
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

.. warning::
    Code below should be implemented by using ``AQL`` (:doc:`queries`).
    Not implemented at the moment.


.. testcode::

    # getting edge by document
    # c.test.edges(from_doc)

    # getting with direction
    # c.test.edges(from_doc, direction="in")

    # assert c.test.edges(from_doc).first.from_document == from_doc
    # assert c.test.edges(from_doc).first.to_document == to_doc


.. _edges proxy:

Edges for Collection instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edges are accessible via collection instance for example ``connection.collection.sample_collection.edges``. Usually this expressions looks lot shorter.

Basically via `edges` shortcut accessible **Edges Proxy** - Proxy object which have several shortcuts and produce ``Resultset`` object.

Below described basic method within ``Edges`` proxy:

.. autoclass:: arango.edge.Edges
    :members: create, delete, update


Making queries
~~~~~~~~~~~~~~

.. warning::
    This functionality not implmented yet. Use **AQL** -
    :doc:`queries` section with custom wrapper to work with Edges.

More details in :term:`Edges REST Api` documentation of **ArangoDB**


.. _edge:

Edge
~~~~

Edge instance methods consist from basic **CRUD** methods and additional
methods specific obly for **Edges**:

.. autoclass:: arango.edge.Edge
    :members: id, rev, create, update, delete, save, body,
              from_document, to_document, get
