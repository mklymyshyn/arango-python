from arango.core import Connection


def create(**kwargs):
    """Connection factory"""

    return Connection(**kwargs).collection

c = Connection()
collection = c.collection
