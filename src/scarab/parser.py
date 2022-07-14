from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable


@dataclass(frozen=True)
class Token:
    __match_args__ = ('text',)
    text: str
    line: int


@dataclass(frozen=True)
class TInt(Token):
    __match_args__ = ('value',)
    value: int


@dataclass(frozen=True)
class TStr(Token):
    __match_args__ = ('value',)
    value: str


@dataclass(frozen=True)
class TIdent(Token):
    __match_args__ = ('value',)
    value: str


@dataclass(frozen=True)
class TSym(Token):
    __match_args__ = ('value',)
    value: str


@dataclass(frozen=True)
class TOp(Token):
    __match_args__ = ('value',)
    value: str


@dataclass(frozen=True)
class TError(Token):
    pass


class Keyword(Enum):
    PRINT = 'print'


@dataclass(frozen=True)
class TKeyword(Token):
    __match_args__ = ('value',)
    value: Keyword


class PeekIterator:
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.peeked = deque()

    def __iter__(self):
        return self

    def __next__(self):
        if self.peeked:
            return self.peeked.popleft()
        return next(self.iterator)

    def peek(self, ahead=0):
        while len(self.peeked) <= ahead:
            self.peeked.append(next(self.iterator))
        return self.peeked[ahead]


class Parser:
    """Takes in a string and returns a list of tokens"""

    operator_characters = "!@#$%^&*-+?_=<>/"
    special_characters = ".,:(){}"

    def __init__(self, source: str):
        self.source = source
        self.iter = PeekIterator(iter(source))
        self.line = 1

    def whitespace(self):
        while self.iter.peek().isspace():
            char = next(self.iter)
            if char == "\n":
                self.line += 1

    def parse_while(self, predicate: Callable[[str], bool]):
        output = ""
        try:
            while predicate(self.iter.peek()):
                output += next(self.iter)
        except StopIteration:
            pass
        return output

    def string_literal(self):
        string = ""
        try:
            while self.iter.peek() != '"':
                string += next(self.iter)
            next(self.iter)
        except StopIteration:
            raise SyntaxError("Unclosed string literal")
        return string

    def __next__(self) -> Token:
        self.whitespace()
        match next(self.iter):
            case sym if sym in self.special_characters:
                return TSym(sym, self.line, sym)
            case op if op in self.operator_characters:
                op += self.parse_while(lambda x: x in self.operator_characters)
                return TOp(op, self.line, op)
            case ident if ident.isalpha():
                ident += self.parse_while(lambda x: x.isalnum())
                key = ident.upper()
                if key in Keyword.__dict__:
                    return TKeyword(ident, self.line, Keyword(ident))
                return TIdent(ident, self.line, ident)
            case d if d.isdigit():
                d += self.parse_while(lambda x: x.isdigit())
                return TInt(d, self.line, int(d))
            case s if s == '"':
                string = self.string_literal()
                return TStr(string, self.line, string)
            case default:
                return TError(default, self.line)

    def __iter__(self):
        return self
