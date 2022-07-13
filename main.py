from scarab.compiler import Compiler, Op
from scarab.parser import Parser
from scarab.value import Object, Bool, Nil

DEBUG = False


def debug(byte: int, operand=None):
    if not DEBUG:
        return

    op = Op(byte)
    if operand is not None:
        print(f"{op.name}\t({operand!s})")
    else:
        print(op.name)


def run(com: Compiler):
    ops = iter(com)
    stack = []
    table: dict[Object, Object] = dict()

    nil = Nil()
    true = Bool(True)
    false = Bool(False)

    for op in ops:
        match op:
            case Op.CONSTANT:
                constant = com.constants[next(ops)]
                stack.append(constant)
                debug(op, constant)
            case Op.TRUE:
                stack.append(true)
            case Op.FALSE:
                stack.append(false)
            case Op.PRINT:
                print(stack.pop())
                debug(op)
            case Op.POP:
                stack.pop()
                debug(op)
            case Op.ADD:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
                debug(op)
            case Op.SUB:
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
                debug(op)
            case Op.MUL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
                debug(op)
            case Op.DIV:
                b = stack.pop()
                a = stack.pop()
                stack.append(a // b)
                debug(op)
            case Op.SET_GLOBAL:
                name = com.constants[next(ops)]
                table[name] = stack.pop()
                debug(op, name)
            case Op.GET_GLOBAL:
                name = com.constants[next(ops)]
                if name in table:
                    stack.append(table[name])
                else:
                    raise NameError(name)
                debug(op, name)
            case _:
                raise RuntimeError(f"Unknown op code: {op}")


if __name__ == '__main__':
    parser = Parser('''
    meal = "eggs"
    beverage = "coffee"
    breakfast = meal + " with " + beverage
    
    print breakfast
    ''')
    compiler = Compiler(parser)
    run(compiler)
