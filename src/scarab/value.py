from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class String:
    value: str


@dataclass(frozen=True, order=True)
class Int:
    value: int


@dataclass(frozen=True, order=True)
class Bool:
    value: bool


@dataclass(frozen=True, order=True)
class NoneObject:
    pass
