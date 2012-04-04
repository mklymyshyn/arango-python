from .core import Connection


def create_connection(**kwargs):
    """Connection factory"""

    return Connection(**kwargs)

# default connection
c = create_connection()
