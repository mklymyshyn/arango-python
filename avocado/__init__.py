from .core import Connection


def create(**kwargs):
    """Connection factory"""

    return Connection(**kwargs)

c = Connection()
collection = c.collection
