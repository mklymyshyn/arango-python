.. _exceptions:

**********
Exceptions
**********

Exceptions Overview
-------------------

All ``arango-python`` exceptions are placed into
``arango.exceptions`` module. Feel free to imprort it like
this::

    from arango.exceptions import InvalidCollection


List of exceptions
------------------

.. glossary::
    :sorted:
    ``DatabaseSystemError``
        Something went completely wrong during execution of request to the server

    ``InvalidCollection``
        Collection should exist and be subclass of
        Collection object

    ``InvalidCollectionId``
        Invalid name of the collection provided

    ``CollectionIdAlreadyExist``
        Raised in case you try to rename collection and
        new name already available

    ``DocumentAlreadyCreated``
        Raised in case document already exist and
        `create` method is called

    ``DocumentIncompatibleDataType``
        Raised in case you trying to update document
        with non-``dict`` or non-``list`` data

    ``DocumentNotFound``
        Raised in case Document not exist in database

    ``WrongIndexType``
        Raises in case index type is undefined

    ``EmptyFields``
        Raised in case no fields for index provied

    ``EdgeAlreadyCreated``
        Raised in case Edge have identifier and already created

    ``EdgeNotYetCreated``
        Raised in case you try to update Edge which is not created

    ``EdgeIncompatibleDataType``
        Raised when you provide new body not ``None`` or not ``dict``

    ``EdgeNotFound``
        Raised in case edge not found in database

    ``DatabaseAlreadyExist``
        Raised during execution of database creation method
