from collections import namedtuple
from pso.constants import NoValue, Operator


class Range(namedtuple('Range', ['fr', 'to', 'fr_incl', 'to_incl'])):

    def __new__(cls, fr=NoValue, to=NoValue, fr_incl=False, to_incl=False):
        return super(Range, cls).__new__(cls, fr, to, fr_incl, to_incl)

    def _check_overlap(self, other):
        if self.to and other.fr:
            incl = (self.to_incl or other.fr_incl)
            if other.fr > self.to or (other.fr == self.to and not incl):
                return False

        if self.fr and other.to:
            incl = (self.fr_incl or other.to_incl)
            if self.fr > other.to or (self.fr == other.to and not incl):
                return False

        return True

    @staticmethod
    def _merge(func, v1, v2):
        if v1[0] and v2[0]:
            return func(v1, v2)
        else:
            return v1 if v1[0] else v2

    def merge(self, other, operator):
        if operator is Operator.OR:
            return self.__or__(other)
        else:
            return self.__and__(other)

    def __and__(self, other):
        """
        Merge range with AND operator
        """
        if not self._check_overlap(other):
            raise ValueError("Can not merge non overlapped ranges")

        fr, fr_incl = self._merge(
            max, (self.fr, not self.fr_incl), (other.fr, not other.fr_incl))
        fr_incl = not fr_incl

        to, to_incl = self._merge(
            min, (self.to, self.to_incl), (other.to, other.to_incl))

        return Range(fr, to, fr_incl, to_incl)

    def __or__(self, other):
        """
        Merge range with AND operator
        """
        if not self._check_overlap(other):
            raise ValueError("Can not merge non overlapped ranges")

        fr, fr_incl = self._merge(
            min, (self.fr, not self.fr_incl), (other.fr, not other.fr_incl))
        fr_incl = not fr_incl

        to, to_incl = self._merge(
            max, (self.to, self.to_incl), (other.to, other.to_incl))

        return Range(fr, to, fr_incl, to_incl)

    @classmethod
    def from_range(cls, r):
        """
        Ability to use Python's standart range object

        Model.field_name == range(0, 100) -> {0 TO 100}
        Model.field_name == range(0, 100, True) -> [0 TO 100]
        """
        include = (True, True) if r.step is True else (False, False)
        return cls(r.start, r.stop, *include)


def range_sort_func(x):
    return (
        x.value.fr is not NoValue,  # Startless first.  * TO ..
        x.value.fr,                 # By start position
        x.value.to is NoValue,      # Endless last
        x.value.to,                 # By end position
    )
