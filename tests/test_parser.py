import pytest

from scarab.parser import Parser, TInt, TStr, TSym, TError


def test_parse_int():
    parser = Parser("543")
    assert isinstance(next(parser), TInt)


def test_parse_string():
    parser = Parser('"Hello, World"')
    assert isinstance(next(parser), TStr)


def test_parse_symbol():
    parser = Parser("*")
    assert isinstance(next(parser), TSym)


def test_parse_expression():
    tokens = list(iter(Parser("1 + 2 * 3")))
    assert len(tokens) == 5


@pytest.mark.parametrize("symbol", [
    "'",
    "`",
])
def test_unknown_symbol(symbol):
    parser = Parser(symbol)
    assert isinstance(next(parser), TError)
