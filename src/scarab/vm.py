from scarab.compiler import Op
from scarab.value import Object, Nil, Bool


class TooFarToJump(RuntimeError):
    pass


class StackOverflow(RuntimeError):
    pass


class StackUnderflow(RuntimeError):
    pass


class UnknownOpCode(RuntimeError):
    pass


NIL = Nil()
TRUE = Bool(True)
FALSE = Bool(False)


class VM:
    def __init__(self, code: bytearray, constants: list[Object], *, trace=False, capture=False):
        self.code = code
        self.constants = constants
        self.ip = -1
        self.stack = list()
        self.table = dict()
        self.trace_execution = trace
        self.capture_output = capture
        self.captured = list()

    @property
    def end(self):
        return len(self.code) - 1

    @property
    def next(self):
        return self.code[self.ip]

    def read_byte(self):
        self.ip += 1
        return self.next

    def read_constant(self):
        return self.constants[self.read_byte()]

    def read_short(self):
        upper = self.read_byte()
        lower = self.read_byte()
        return (upper << 8) | lower

    def push(self, value: Object):
        self.stack.append(value)

    def pop(self):
        if len(self.stack) < 1:
            raise StackUnderflow
        return self.stack.pop()

    def run(self):
        while self.ip < self.end:
            op = self.read_byte()

            if self.trace_execution:
                print("----------")
                if len(self.stack) > 0:
                    for slot in self.stack:
                        print(f"[ {slot} ]", end="")
                    print()
                else:
                    print("[]")
                print(Op(op).name)

            match op:
                case Op.CONSTANT:
                    self.push(self.read_constant())
                case Op.TRUE:
                    self.push(TRUE)
                case Op.FALSE:
                    self.push(FALSE)
                case Op.PRINT:
                    if self.capture_output:
                        self.captured.append(self.pop())
                    else:
                        print(self.pop())
                case Op.POP:
                    self.pop()
                case Op.ADD:
                    b = self.pop()
                    a = self.pop()
                    self.push(a + b)
                case Op.SUB:
                    b = self.pop()
                    a = self.pop()
                    self.push(a - b)
                case Op.MUL:
                    b = self.pop()
                    a = self.pop()
                    self.push(a * b)
                case Op.DIV:
                    b = self.pop()
                    a = self.pop()
                    self.push(a // b)
                case Op.SET_GLOBAL:
                    name = self.read_constant()
                    self.table[name] = self.pop()
                case Op.GET_GLOBAL:
                    name = self.read_constant()
                    if name in self.table:
                        self.push(self.table[name])
                    else:
                        raise NameError(name)
                case Op.SET_LOCAL:
                    slot = self.read_byte()
                    self.stack[slot] = self.stack[-1]
                case Op.GET_LOCAL:
                    slot = self.read_byte()
                    self.push(self.stack[slot])
                case _:
                    raise UnknownOpCode(op)
