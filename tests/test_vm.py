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
