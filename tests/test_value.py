import pytest

from scarab.value import Int, Bool, String, Nil


def test_int():
    a = Int(5)
    b = Int(10)
    assert a + b == Int(15)


def test_string():
    hello = String("hello")
    world = String("world")
    assert (hello + world).value == "helloworld"


@pytest.mark.parametrize("test_input", [
    Bool(False),
    Int(0),
    String(""),
    Nil,
    not Bool(True),
])
def test_false(test_input):
    assert bool(test_input) is False


@pytest.mark.parametrize("a,b", [
    (Int(5), Bool(True)),
    (Bool(False), Int(600)),
])
def test_wrong_types(a, b):
    with pytest.raises(TypeError):
        a + b
