from scarab.compiler import Compiler, Op
from scarab.parser import Parser
from scarab.value import Int, String


def run(com: Compiler):
    ops = iter(com)
    stack = []
    for op in ops:
        match op:
            case Op.LOAD_CONST:
                stack.append(Int(next(ops)))
            case Op.LOAD_STRING:
                string = com.strings[next(ops)]
                stack.append(String(string))
            case Op.ADD:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            case Op.SUB:
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            case Op.MUL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
            case Op.DIV:
                b = stack.pop()
                a = stack.pop()
                stack.append(a // b)
            case Op.PRINT:
                print(stack.pop())
            case Op.POP:
                stack.pop()
            case _:
                print(Op(op))


if __name__ == '__main__':
    parser = Parser('print 1 + 2 * 3')
    compiler = Compiler(parser)
    run(compiler)
