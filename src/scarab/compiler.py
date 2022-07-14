from dataclasses import dataclass
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
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    SET_GLOBAL = auto()
    GET_GLOBAL = auto()
    SET_LOCAL = auto()
    GET_LOCAL = auto()
    JUMP_IF_FALSE = auto()
    JUMP = auto()


BUILTIN_SYMBOLS = {
    '+': Op.ADD,
    '-': Op.SUB,
    '*': Op.MUL,
    '/': Op.DIV,
    "==": Op.EQUAL,
    "!=": Op.NOT_EQUAL,
    "<": Op.LESS,
    "<=": Op.LESS_EQUAL,
    ">": Op.GREATER,
    ">=": Op.GREATER_EQUAL,
}


class Precedence(IntEnum):
    NONE = auto()
    ASSIGNMENT = auto()  # =
    OR = auto()  # or
    AND = auto()  # and
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
            case TOp(op):
                return cls.get_op(op)
            case TKeyword(Keyword.OR):
                return cls.OR
            case TKeyword(Keyword.AND):
                return cls.AND
            case _:
                return cls.NONE


@dataclass
class Local:
    name: str
    depth: int


T = TypeVar('T')


class Compiler:
    """Compiles tokens into bytecode"""

    def __init__(self, parser):
        self.parser = iter(parser)
        self.previous = None
        self.current = None
        self.exhausted = False
        self.code = bytearray()
        self.constants = list()

        # Local variables & Scoping
        self.locals: list[Local] = list()
        self.depth = 0

    def advance(self):
        self.previous = self.current

        self.current = next(self.parser, None)
        if isinstance(self.current, TError):
            self.exhausted = True
            raise SyntaxError(self.current.text)
        if self.current is None:
            self.exhausted = True

    def check(self, t: Type[T], value=None):
        if not isinstance(self.current, t):
            return False

        if value is not None and self.current.value != value:
            return False

        return True

    def consume(self, t: Type[T], value=None, msg=None):
        if self.check(t, value):
            self.advance()
            return
        raise SyntaxError(msg)

    def match(self, t: Type[T], value=None):
        if not self.check(t, value):
            return False
        self.advance()
        return True

    @property
    def in_local_scope(self):
        return self.depth > 0

    def make_constant(self, constant):
        index = len(self.constants)
        self.constants.append(constant)
        return index

    def make_local(self, name, depth):
        index = len(self.locals)
        self.locals.append(Local(name, depth))
        return index

    def binary(self, op):
        self.parse_precedence(Precedence.get_op(op) + 1)
        if op in BUILTIN_SYMBOLS:
            self.code.append(BUILTIN_SYMBOLS[op])
            return
        raise SyntaxError(op)

    def set_global(self, name):
        constant = self.make_constant(String(name))
        self.code.append(Op.SET_GLOBAL)
        self.code.append(constant)

    def set_local(self, name):
        for i, local in reversed(list(enumerate(self.locals))):
            if local.depth < self.depth:
                break
            if name == local.name:
                # Reassigning variables
                self.code.append(Op.SET_LOCAL)
                self.code.append(i)
                return
        index = self.make_local(name, self.depth)
        self.code.append(Op.SET_LOCAL)
        self.code.append(index)

    def get_global(self, name):
        constant = self.make_constant(String(name))
        self.code.append(Op.GET_GLOBAL)
        self.code.append(constant)

    def get_local(self, name):
        for i, local in reversed(list(enumerate(self.locals))):
            if name == local.name:
                self.code.append(Op.GET_LOCAL)
                self.code.append(i)
                break
        else:
            self.get_global(name)

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
            case TSym("("):
                self.expression()
                self.consume(TSym, ")")
            case TIdent(name):
                if self.match(TSym, ":"):
                    raise NotImplementedError("function calls")
                    # self.expression()
                    # arity = self.call_arguments() + 1
                    # self.code.append(Op.CALL)
                else:
                    if self.in_local_scope:
                        self.get_local(name)
                    else:
                        self.get_global(name)
            case TKeyword(Keyword.NOT):
                self.parse_precedence(Precedence.UNARY)
                self.code.append(Op.NOT)
            case TOp(op):
                # TODO: add unary operators
                raise SyntaxError(op)

        while precedence <= Precedence.get(self.current):
            self.advance()
            match self.previous:
                case TKeyword(Keyword.AND):
                    end_jump = self.emit_jump(Op.JUMP_IF_FALSE)
                    self.code.append(Op.POP)

                    self.parse_precedence(Precedence.AND)
                    self.patch_jump(end_jump)
                case TKeyword(Keyword.OR):
                    else_jump = self.emit_jump(Op.JUMP_IF_FALSE)
                    end_jump = self.emit_jump(Op.JUMP)

                    self.patch_jump(else_jump)
                    self.code.append(Op.POP)

                    self.parse_precedence(Precedence.OR)
                    self.patch_jump(end_jump)
                case TOp(value=op):
                    self.binary(op)
                case default:
                    raise SyntaxError(default)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    def call_arguments(self):
        arity = 0
        while self.match(TSym, ","):
            self.expression()
            arity += 1
        return arity

    def block(self, t: Type[T], value):
        while not self.exhausted and not self.match(t, value):
            self.statement()

    def emit_jump(self, op):
        self.code.append(op)
        where = len(self.code)
        self.code.append(0xff)
        self.code.append(0xff)
        return where

    def patch_jump(self, offset):
        # -2 to adjust for the bytecode for the jump offset itself
        jump = len(self.code) - offset - 2

        if jump > (2 ** 16 - 1):
            raise Exception("Too far to jump")

        self.code[offset] = (jump >> 8) & 0xff
        self.code[offset + 1] = jump & 0xff

    def print_statement(self):
        self.expression()
        self.code.append(Op.PRINT)

    def if_statement(self):
        self.expression()

        then_jump = self.emit_jump(Op.JUMP_IF_FALSE)
        self.code.append(Op.POP)
        self.statement()

        else_jump = self.emit_jump(Op.JUMP)

        self.patch_jump(then_jump)
        self.code.append(Op.POP)

        if self.match(TKeyword, Keyword.ELSE):
            self.statement()
        self.patch_jump(else_jump)

    def block_statement(self):
        self.depth += 1
        self.block(TSym, "}")
        self.depth -= 1

        while len(self.locals) > 0 and self.locals[-1].depth > self.depth:
            # Pop the local from the VM's stack
            self.code.append(Op.POP)
            self.locals.pop()

    def assignment_statement(self, name):
        if self.in_local_scope:
            self.set_local(name)
        else:
            self.set_global(name)

    def expression_statement(self):
        self.expression()
        self.code.append(Op.POP)

    def declaration(self):
        name = self.previous.value
        if self.match(TOp, "="):
            self.expression()
            self.assignment_statement(name)
        elif self.match(TIdent):
            raise NotImplementedError("function definitions")
        else:
            raise SyntaxError("expect `=` or arguments after identifier")

    def statement(self) -> bool:
        """Compiles the next statement and returns True if it was pure"""
        if self.match(TKeyword, Keyword.PRINT):
            self.print_statement()
        elif self.match(TKeyword, Keyword.IF):
            self.if_statement()
        elif self.match(TSym, "{"):
            self.block_statement()
        elif self.match(TIdent):
            self.declaration()
        else:
            self.expression_statement()
            return True
        return False

    def compile(self):
        if not self.exhausted:
            self.advance()
            while not self.exhausted:
                self.statement()

    def __iter__(self):
        self.compile()
        return iter(self.code)
