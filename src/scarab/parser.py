from dataclasses import dataclass


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
class TError(Token):
    pass


class Parser:
    """Takes in a string and returns a list of tokens"""

    special_characters = "!@#$%^&*()-+?_=,<>/"

    def __init__(self, source: str):
        self.source = source
        self.iter = iter(source)
        self.peeked = list()
        self.line = 1

    def whitespace(self):
        while True:
            item = self.peek()
            if item == "\n":
                self.line += 1
                self.next()
                break
            elif item.isspace():
                self.next()
                break
            else:
                break

    def next(self):
        if len(self.peeked) > 0:
            return self.peeked.pop()
        return next(self.iter)

    def peek(self):
        item = self.next()
        self.peeked.append(item)
        return item

    def __next__(self) -> Token:
        self.whitespace()
        match self.next():
            case sym if sym in self.special_characters:
                while self.peek() in self.special_characters:
                    sym += self.next()
                return TSym(sym, self.line, sym)
            case ident if ident.isalpha():
                while self.peek().isalnum():
                    ident += self.next()
                return TIdent(ident, self.line, ident)
            case s if s == '"':
                string = ''
                while self.peek() != '"':
                    item = self.next()
                    if item is None:
                        return TError("Unclosed string literal", self.line)
                    string += item
                return TStr(string, self.line, string)
            case d if d.isdigit():
                return TInt(d, self.line, int(d))
            case default:
                return TError(default, self.line)

    def __iter__(self):
        return self
