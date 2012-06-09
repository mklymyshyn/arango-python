

__all__ = ("ComparsionMixin",)


class ComparsionMixin(object):
    """
    Mixin to help compare two instances
    """
    def __cmp__(self, other):
        """
        Compare two items
        """

        if other == None:
            return -1

        if self.body != None and other.body != None and \
                set(self.body).symmetric_difference(other.body) not in \
                    [self.IGNORE_KEYS, set([])]:
            return -1

        # compare bodies but ignore sys keys
        if self.body != None and self.body == other.body:
            for key in other.body.keys():
                if key in self.IGNORE_KEYS:
                    continue

                if self.body.get("key", None) != other.body.get("key", None):
                    return -1

        if self.body == None and self.body != other.body:
            return -1

        if self.id == other.id and self.rev == other.rev:
            return 0

        return -1
