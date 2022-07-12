from scarab.parser import Parser, TInt, TStr


def test_parse_int():
    parser = Parser("543")
    assert isinstance(next(parser), TInt)


def test_parse_string():
    parser = Parser('"Hello, World"')
    assert isinstance(next(parser), TStr)


def test_parse_expression():
    tokens = list(iter(Parser("1 + 2 * 3")))
    assert len(tokens) == 5
