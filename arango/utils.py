
try:
    import simplejson as json
except ImportError:
    import json


__all__ = ("json", "proxied_document_ref", "Proxy")


def proxied_document_ref(ref_or_document):
    """
    Utility to get reference from document **or** from
    proxied response or return string as is.
    """
    from .document import Document
    from .core import ResponseProxy

    if issubclass(type(ref_or_document), Document):
        return ref_or_document.id
    elif isinstance(ref_or_document, ResponseProxy) and \
            hasattr(ref_or_document, "resultset") and \
            isinstance(ref_or_document.resultset, Document):
        return ref_or_document.resultset.id

    return ref_or_document
