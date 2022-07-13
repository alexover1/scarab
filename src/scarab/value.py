from dataclasses import dataclass


def _process_binary_ops(cls, add, sub, mul, div):
    def __add__(self, other):
        if other.__class__ != self.__class__:
            raise TypeError
        return type(self)(self.value + other.value)

    def __sub__(self, other):
        if other.__class__ != self.__class__:
            raise TypeError
        return type(self)(self.value - other.value)

    def __mul__(self, other):
        if other.__class__ != self.__class__:
            raise TypeError
        return type(self)(self.value * other.value)

    def __truediv__(self, other):
        if other.__class__ != self.__class__:
            raise TypeError
        return type(self)(self.value / other.value)

    if add:
        cls.__add__ = __add__
    if sub:
        cls.__sub__ = __sub__
    if mul:
        cls.__mul__ = __mul__
    if div:
        cls.__truediv__ = __truediv__

    return cls


def binary_ops(cls=None, /, *, add=False, sub=False, mul=False, div=False):
    def wrap(cls_):
        return _process_binary_ops(cls_, add, sub, mul, div)

    # See if we're being called as @binary_ops or @binary_ops().
    if cls is None:
        return wrap

    # We're called as @binary_ops without parens.
    return wrap(cls)


@dataclass(frozen=True, order=True)
@binary_ops(add=True, sub=True, mul=True, div=True)
class String:
    value: str

    def __str__(self):
        return self.value

    def __bool__(self):
        return len(self.value) > 0


@dataclass(frozen=True, order=True)
@binary_ops(add=True, sub=True, mul=True, div=True)
class Int:
    value: int

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return self.value != 0


@dataclass(frozen=True, order=True)
class Bool:
    value: bool

    def __str__(self):
        return "true" if self.value else "false"

    def __bool__(self):
        return self.value


@dataclass(frozen=True, order=True)
class NoneObject:
    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mul__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __bool__(self):
        return False


Nil = NoneObject()
