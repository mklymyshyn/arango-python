

__all__ = ("ComparsionMixin", "LazyLoadMixin")


class ComparsionMixin(object):
    """
    Mixin to help compare two instances
    """
    def __cmp__(self, other):
        """
        Compare two items
        """

        if not issubclass(type(other), self.__class__):
            return -1

        if (self.body == other.body and self._id == other._id and
                self._rev == other._rev):
            return 0

        ignore_keys = lambda k: k not in self.IGNORE_KEYS

        # compare keys only
        if filter(ignore_keys, self.body.keys()) != \
                filter(ignore_keys, other.body.keys()):
            return -1

        # compare bodies but ignore sys keys
        if (self.body is not None and other.body is not None):
            for key in other.body.keys():
                if key in self.IGNORE_KEYS:
                    continue

                if self.body.get(key, None) != other.body.get(key, None):
                    return -1

        if (self._id is not None and self._rev is not None and
                self._id != other._id or str(self._rev) != str(other._rev)):
            return -1

        return 0


class LazyLoadMixin(object):
    """
    Mixin to lazily load some objects
    before processing some of methods.

    Required attributes:

     * LAZY_LOAD_HANDLERS - list of methods which should be handled
     * lazy_loader - method which should check status of loading
                      and make decision about loading something
                      or simply process next method in chain
     * _lazy_loaded - property which provide status of the lazy loading,
                      should be False by default
    """

    def __getattribute__(self, name):
        """Fetching lazy document"""
        if name in object.__getattribute__(self, "LAZY_LOAD_HANDLERS"):
            object.__getattribute__(self, "_handle_lazy")()

        return object.__getattribute__(self, name)

    def _handle_lazy(self):
        if self._lazy_loaded is False:
            self._lazy_loaded = True
            self.lazy_loader()
