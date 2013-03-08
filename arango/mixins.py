

__all__ = ("ComparsionMixin", "LazyLoadMixin")


class ComparsionMixin(object):
    """
    Mixin to help compare two instances
    """
    def __eq__(self, other):
        """
        Compare two items
        """

        if not issubclass(type(other), self.__class__):
            return False

        if (self.body == other.body and self._id == other._id and
                self._rev == other._rev):
            return True

        keys = lambda o: [key for key in o.body.keys()
                          if key not in self.IGNORE_KEYS]

        # compare keys only
        if keys(self) != keys(other):
            return False

        # compare bodies but ignore sys keys
        if (self.body is not None and other.body is not None):
            for key in keys(other):
                if self.body.get(key, None) != other.body.get(key, None):
                    return False

        if (self._id is not None and self._rev is not None and
                (self._id != other._id or str(self._rev) != str(other._rev))):
            return False

        return True


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
