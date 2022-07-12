from enum import IntEnum, auto
from typing import TypeVar, Type

from .parser import Token, TInt, TStr, TSym, TError


class Op(IntEnum):
    LOAD_CONST = auto()
    LOAD_STRING = auto()
    TRUE = auto()
    FALSE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    NOT = auto()
    NOT_EQUAL = auto()
    EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()


BUILTIN_SYMBOLS = {
    '+': Op.ADD,
    '-': Op.SUB,
    '*': Op.MUL,
    '/': Op.DIV,
}


class Precedence(IntEnum):
    NONE = auto()
    ASSIGNMENT = auto()  # =
    EQUALITY = auto()  # == !=
    COMPARISON = auto()  # < > <= >=
    TERM = auto()  # + -
    FACTOR = auto()  # * /
    UNARY = auto()  # ! -
    CALL = auto()
    PRIMARY = auto()

    @classmethod
    def get_op(cls, op: str):
        return {
            '=': cls.ASSIGNMENT,
            '==': cls.EQUALITY,
            '!=': cls.EQUALITY,
            '<': cls.COMPARISON,
            '<=': cls.COMPARISON,
            '>': cls.COMPARISON,
            '>=': cls.COMPARISON,
            '+': cls.TERM,
            '-': cls.TERM,
            '*': cls.FACTOR,
            '/': cls.FACTOR,
            '!': cls.UNARY,
        }.get(op, cls.NONE)

    @classmethod
    def get(cls, token: Token):
        match token:
            case TInt():
                return cls.NONE
            case TStr():
                return cls.NONE
            case TSym(value=op):
                return cls.get_op(op)
            case _:
                return cls.NONE


T = TypeVar('T')


class Compiler:
    """Takes in an iterable of tokens, """

    def __init__(self, parser):
        self.parser = iter(parser)
        self.previous = None
        self.current = None
        self.exhausted = False
        self.code = bytearray()
        self.strings: list[str] = []

    def advance(self):
        self.previous = self.current

        self.current = next(self.parser, None)
        if isinstance(self.current, TError):
            self.exhausted = True
            raise SyntaxError(self.current)
        if self.current is None:
            self.exhausted = True

    def consume(self, t: Type[T], value):
        if isinstance(self.current, t) and self.current.value == value:
            self.advance()
            return
        raise SyntaxError

    def binary(self, op):
        self.parse_precedence(Precedence.get_op(op) + 1)
        if op in BUILTIN_SYMBOLS:
            self.code.append(BUILTIN_SYMBOLS[op])
            return
        raise SyntaxError(op)

    def parse_precedence(self, precedence: int):
        self.advance()

        match self.previous:
            case TInt(x):
                self.code.append(Op.LOAD_CONST)
                self.code.append(x)
            case TStr(s):
                self.code.append(Op.LOAD_STRING)
                self.code.append(len(self.strings))
                self.strings.append(s)
            case TSym("("):
                self.expression()
                self.consume(TSym, ")")
            case TSym(op):
                self.parse_precedence(Precedence.UNARY)
                match op:
                    case "!":
                        self.code.append(Op.NOT)
                    case other:
                        raise SyntaxError(other)

        while precedence <= Precedence.get(self.current):
            self.advance()
            match self.previous:
                case TSym(value=op):
                    self.binary(op)
                case default:
                    raise SyntaxError(default)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    def compile(self):
        if not self.exhausted:
            self.advance()
            self.expression()

    def write(self, file_name: str):
        if not self.exhausted:
            raise Exception("You must call iter() or compile() before trying to save the output")

        with open(file_name, "wb") as f:
            for string in self.strings:
                f.write((string + '\0').encode("utf-8"))
            f.write(self.code)

    def __iter__(self):
        self.compile()
        return iter(self.code)
