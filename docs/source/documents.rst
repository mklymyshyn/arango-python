.. _documents:

Documents
---------

Documents in ArangoDB are JSON objects. These objects can be nested (to any depth) and may contains lists. Each document is unique identified by its document handle.

Small usage example::


    from arango import create

    # connection & collection `test`
    c = create()
    c.test.create()

    # create FROM document
    document = c.test.documents.create({
        "sample_key": "sample_value"
    })

    assert document.get("sample_key") == "sample_value"

    c.test.documents().count


.. _documents proxy:

Documents for Collection instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documents are accessible via collection instance for example ``connection.collection.sample_collection.documents``. Usually this expressions looks lot shorter.

Basically via `docuemnts` shortcut accessible **Docuemnts Proxy** - Proxy object which have several shortcuts and produce ``Resultset`` object.

Below described basic method within ``Documents`` proxy:

.. autoclass:: arango.document.Documents
    :members: create, delete, update, count


Making queries
~~~~~~~~~~~~~~


.. warning::
    This part of functionality isn't implemented at all at the moment.
    It will be implemented in **ALPHA** release of the project.

It's possible to get only all documents for :ref:`Collection`::

    ...

    # getting with direction
    c.test.documents()

More details in :term:`Documents REST Api` documentation of **ArangoDB**



.. _document:

Document
~~~~~~~~

Document instance methods consist from basic **CRUD** methods and serveral
shortcuts to more convenient work with documents.

.. autoclass:: arango.document.Document
    :members: id, rev, response,
              create, update, delete, save,
              body, get
