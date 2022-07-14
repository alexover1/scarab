import pytest

from scarab import Parser, Compiler, VM, Int


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
