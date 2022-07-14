import pytest

from scarab import Parser, Compiler, VM, Int, String, Bool


def test_add():
    compiler = Compiler(Parser("print 1 + 2"))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(3)


def test_order_operations():
    compiler = Compiler(Parser("print 1 + 2 * 3"))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(7)


def test_grouping():
    compiler = Compiler(Parser("print (1 + 2) * 3"))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(9)


def test_out_of_scope():
    with pytest.raises(NameError):
        compiler = Compiler(Parser('''
        {
            a = 10
        }
        print a
        '''))
        compiler.compile()
        vm = VM(compiler.code, compiler.constants, capture=True)
        vm.run()


@pytest.mark.parametrize('test_input', [
    'print 1 == 1',
    'print 1 != 0',
    'print 10 > 5',
    'print 2 < 3',
    'print 6 >= 6',
    'print 6 >= 5',
])
def test_truthy(test_input):
    compiler = Compiler(Parser(test_input))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Bool(True)


def test_if_else():
    compiler = Compiler(Parser('''
    if 1 print "Yes"
    else print "No"
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == String("Yes")


@pytest.mark.parametrize('test_input,expected', [
    ('print 1 and 1', Int(1)),
    ('print 1 and 0', Int(0)),
    ('print 0 and 1', Int(0)),
    ('print 0 and 0', Int(0)),
    ('print 1 or 1', Int(1)),
    ('print 1 or 0', Int(1)),
    ('print 0 or 1', Int(1)),
    ('print 0 or 0', Int(0)),
    ('print "yes" and "no"', String("no")),
    ('print "yes" or "no"', String("yes")),
    ('print "" or "no"', String("no")),
    ('print "yes" or ""', String("yes")),
    ('print "yes" and ""', String("")),
])
def test_and_or(test_input, expected):
    compiler = Compiler(Parser(test_input))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == expected
