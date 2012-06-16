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


.. _document:

Document
~~~~~~~~
