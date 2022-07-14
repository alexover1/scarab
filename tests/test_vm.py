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


def test_global_variables():
    compiler = Compiler(Parser('''
    breakfast := "eggs"
    beverage := "coffee"
    breakfast = "eggs with " + beverage

    print breakfast
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == String("eggs with coffee")


def test_local_variables():
    compiler = Compiler(Parser('''
    x := 5
    do
      x := x * x
      print x
    end
    print x
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(25)
    assert vm.captured[1] == Int(5)


def test_out_of_scope():
    with pytest.raises(NameError):
        compiler = Compiler(Parser('''
        do
          a := 10
        end
        print a
        '''))
        compiler.compile()
        vm = VM(compiler.code, compiler.constants, capture=True)
        vm.run()


def test_unknown_local():
    with pytest.raises(NameError):
        compiler = Compiler(Parser('''
        do print x end
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


def test_multi_declare():
    compiler = Compiler(Parser('''
    x := y := 5
    print x
    print y
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(5)
    assert vm.captured[1] == Int(5)


def test_multi_assign():
    compiler = Compiler(Parser('''
    x := y := 5
    x = y = 100
    print x
    print y
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(100)
    assert vm.captured[1] == Int(100)


def test_multi_declare_local():
    compiler = Compiler(Parser('''
    do
      x := y := 2
      x = y = x + 1
      print x
      print y
    end
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    assert vm.captured[0] == Int(3)
    assert vm.captured[1] == Int(3)


def test_while_loop():
    compiler = Compiler(Parser('''
    x := 0
    while x < 10 do
        print x
        x = x + 1
    end
    '''))
    compiler.compile()
    vm = VM(compiler.code, compiler.constants, capture=True)
    vm.run()
    for i in range(10):
        assert vm.captured[i] == Int(i)
