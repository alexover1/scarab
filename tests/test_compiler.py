import pytest

from scarab import Parser
from scarab.compiler import Compiler, Op


def test_int():
    compiler = Compiler(Parser("123"))
    compiler.compile()
    assert compiler.code == bytearray([Op.CONSTANT, 0, Op.POP])
    assert compiler.constants[0].value == 123


def test_string():
    compiler = Compiler(Parser('"Hello, World"'))
    compiler.compile()
    assert compiler.code == bytearray([Op.CONSTANT, 0, Op.POP])
    assert compiler.constants[0].value == "Hello, World"


def test_expression():
    compiler = Compiler(Parser("1 + 2 * 3"))
    compiler.compile()
    assert compiler.code == bytearray([
        Op.CONSTANT, 0,
        Op.CONSTANT, 1,
        Op.CONSTANT, 2,
        Op.MUL,
        Op.ADD,
        Op.POP
    ])


@pytest.mark.parametrize("test_input", [
    "*",
    "+ 3",
    "10 -"
    "1 + * 2",
    "50 + -",
])
def test_invalid_expression(test_input):
    with pytest.raises(SyntaxError):
        iter(Compiler(Parser(test_input)))


def test_scope():
    compiler = Compiler(Parser('''
    a := 100
    do
      a := a
      b := 6
      print a + b
    end
    '''))
    compiler.compile()
    assert compiler.code == bytearray([
        Op.CONSTANT, 0,
        Op.DEFINE_GLOBAL, 1,
        Op.POP,
        Op.GET_GLOBAL, 2,
        Op.SET_LOCAL, 0,
        Op.CONSTANT, 3,
        Op.SET_LOCAL, 1,
        Op.GET_LOCAL, 0,
        Op.GET_LOCAL, 1,
        Op.ADD,
        Op.PRINT,
        Op.POP,
        Op.POP,
    ])


@pytest.mark.parametrize("test_input", [
    "1 + 2 * 3",
    "(1 + 2) * 3",
    "2 * 3 + 1",
    "1 + (2 * 3 + 4)",
])
def test_compiles(test_input):
    compiler = Compiler(Parser(test_input))
    compiler.compile()
