from enum import IntEnum, auto
from typing import TypeVar, Type

from .parser import Token, TInt, TStr, TError, TKeyword, Keyword, TIdent, TOp, TSym
from .value import Int, String


class Op(IntEnum):
    CONSTANT = auto()
    TRUE = auto()
    FALSE = auto()
    PRINT = auto()
    POP = auto()
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
    SET_GLOBAL = auto()
    GET_GLOBAL = auto()


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
            case TOp(value=op):
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
        self.constants = list()

    def advance(self):
        self.previous = self.current

        self.current = next(self.parser, None)
        if isinstance(self.current, TError):
            self.exhausted = True
            raise SyntaxError(self.current.text)
        if self.current is None:
            self.exhausted = True

    def consume(self, t: Type[T], value):
        if isinstance(self.current, t) and self.current.value == value:
            self.advance()
            return
        raise SyntaxError

    def check(self, t: Type[T], value):
        return isinstance(self.current, t) and self.current.value == value

    def match(self, t: Type[T], value=None):
        if not isinstance(self.current, t):
            return False

        if value is not None and self.current.value != value:
            return False

        self.advance()
        return True

    def make_constant(self, constant):
        index = len(self.constants)
        self.constants.append(constant)
        return index

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
                constant = self.make_constant(Int(x))
                self.code.append(Op.CONSTANT)
                self.code.append(constant)
            case TStr(s):
                constant = self.make_constant(String(s))
                self.code.append(Op.CONSTANT)
                self.code.append(constant)
            case TIdent(name):
                if self.match(TSym, ":"):
                    raise NotImplementedError("function calls")
                else:
                    constant = self.make_constant(String(name))
                    self.code.append(Op.GET_GLOBAL)
                    self.code.append(constant)
            case TSym("("):
                self.expression()
                self.consume(TSym, ")")
            case TOp(op):
                self.parse_precedence(Precedence.UNARY)
                match op:
                    case "!":
                        self.code.append(Op.NOT)
                    case other:
                        raise SyntaxError(other)

        while precedence <= Precedence.get(self.current):
            self.advance()
            match self.previous:
                case TOp(value=op):
                    self.binary(op)
                case default:
                    raise SyntaxError(default)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    def print_statement(self):
        self.expression()
        self.code.append(Op.PRINT)

    def expression_statement(self):
        self.expression()
        self.code.append(Op.POP)

    def call_arguments(self):
        arity = 0
        while self.match(TSym, ","):
            self.expression()
            arity += 1
        return arity

    def statement(self):
        if self.match(TKeyword, Keyword.PRINT):
            self.print_statement()
            return False
        elif self.match(TIdent):
            name = self.previous.value
            if self.match(TOp, "="):
                self.expression()
                constant = self.make_constant(String(name))
                self.code.append(Op.SET_GLOBAL)
                self.code.append(constant)
            elif self.match(TIdent):
                raise NotImplementedError("function definitions")
                # self.expression()
                # arity = self.call_arguments() + 1
                # self.code.append(Op.CALL)
            else:
                raise SyntaxError("expect `=` or arguments after identifier")
            return False
        else:
            self.expression_statement()
            return True

    def declaration(self):
        self.statement()

    def compile(self):
        if not self.exhausted:
            self.advance()
            while not self.exhausted:
                self.declaration()

    def __iter__(self):
        self.compile()
        return iter(self.code)
