
try:
    import cjson as json_lib
except ImportError:
    import json as json_lib
except ImportError:
    import simplejson as json_lib


__all__ = ("json",)


class json(object):
    @classmethod
    def loads(cls, str):
        if hasattr(json_lib, "decode"):
            try:
                return json_lib.decode(str)
            except json_lib.DecodeError, e:
                raise TypeError(e)

        return json_lib.loads(str)

    @classmethod
    def dumps(cls, obj):
        if hasattr(json_lib, "encode"):
            return json_lib.encode(obj)

        return json_lib.dumps(obj)
