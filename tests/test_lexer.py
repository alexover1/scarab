import pytest

from scarab.lexer import Lexer, TInt, TStr, TSym, TError, TOp, TIdent


def test_int():
    lexer = Lexer("543")
    assert isinstance(next(lexer), TInt)


def test_string():
    lexer = Lexer('"Hello, World"')
    assert isinstance(next(lexer), TStr)


def test_op():
    lexer = Lexer("*")
    assert isinstance(next(lexer), TOp)


def test_symbol():
    lexer = Lexer(",")
    assert isinstance(next(lexer), TSym)


def test_expression():
    tokens = list(Lexer("1 + 2 * 3"))
    assert len(tokens) == 5


@pytest.mark.parametrize("symbol", [
    "'",
    "`",
])
def test_unknown_symbol(symbol):
    lexer = Lexer(symbol)
    assert isinstance(next(lexer), TError)


def test_whitespace():
    lexer = Lexer('   x = 5     \n  \n   y=\n6 \n ')
    assert list(iter(lexer)) == [TIdent("x", 1, "x"), TOp("=", 1, "="), TInt("5", 1, 5),
                                 TIdent("y", 3, "y"), TOp("=", 3, "="), TInt("6", 4, 6)]
