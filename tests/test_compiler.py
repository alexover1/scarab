import pytest

from scarab import Parser
from scarab.compiler import Compiler, Op


def test_int():
    compiler = Compiler(Parser("123"))
    compiler.compile()
    assert compiler.code == bytearray([Op.LOAD_CONST, 123])


def test_string():
    compiler = Compiler(Parser('"Hello, World"'))
    compiler.compile()
    assert compiler.code == bytearray([Op.LOAD_STRING, 0])
    assert compiler.strings[0] == "Hello, World"


def test_expression():
    compiler = Compiler(Parser("1 + 2 * 3"))
    compiler.compile()
    assert compiler.code == bytearray([
        Op.LOAD_CONST, 1,
        Op.LOAD_CONST, 2,
        Op.LOAD_CONST, 3,
        Op.MUL,
        Op.ADD
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


@pytest.mark.parametrize("test_input", [
    "1 + - 2",
    "* 3",
    "50 + -",
])
def test_syntax_error(test_input):
    with pytest.raises(SyntaxError):
        iter(Compiler(Parser(test_input)))
