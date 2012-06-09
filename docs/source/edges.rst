
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
