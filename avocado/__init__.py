

def create_connection(**kwargs):
    """Connection factory"""
    from .core import Connection
    return Connection(**kwargs)

# default connection
c = create_connection()
