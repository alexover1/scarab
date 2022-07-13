import pytest

from scarab.parser import Parser, TInt, TStr, TSym, TError, TOp, TIdent


def test_int():
    parser = Parser("543")
    assert isinstance(next(parser), TInt)


def test_string():
    parser = Parser('"Hello, World"')
    assert isinstance(next(parser), TStr)


def test_op():
    parser = Parser("*")
    assert isinstance(next(parser), TOp)


def test_symbol():
    parser = Parser(",")
    assert isinstance(next(parser), TSym)


def test_expression():
    tokens = list(iter(Parser("1 + 2 * 3")))
    assert len(tokens) == 5


@pytest.mark.parametrize("symbol", [
    "'",
    "`",
])
def test_unknown_symbol(symbol):
    parser = Parser(symbol)
    assert isinstance(next(parser), TError)


def test_whitespace():
    parser = Parser('   x = 5     \n  \n   y=\n6 \n ')
    assert list(iter(parser)) == [TIdent("x", 1, "x"), TOp("=", 1, "="), TInt("5", 1, 5),
                                  TIdent("y", 3, "y"), TOp("=", 3, "="), TInt("6", 4, 6)]
