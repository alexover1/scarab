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
    def __init__(self, code: bytearray, constants: list[Object], *, ir=False, trace=False, capture=False):
        self.code = code
        self.constants = constants
        self.ip = -1
        self.stack = list()
        self.table = dict()

        self.output_ir = ir
        self.stack_trace = trace
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

    def peek(self, distance=1):
        return self.stack[-distance]

    def debug_ir(self):
        offset = 0
        print("=== code ===")
        while offset < len(self.code):
            op = Op(self.code[offset])
            match op:
                case Op.CONSTANT:
                    constant = self.constants[self.code[offset + 1]]
                    print(f"{str(offset).zfill(3)} {op.name}\t({constant!s})")
                    offset += 2
                case Op.GET_GLOBAL | Op.SET_GLOBAL | Op.GET_LOCAL | Op.SET_LOCAL:
                    constant = self.constants[self.code[offset + 1]]
                    print(f"{str(offset).zfill(3)} {op.name}\t({constant!s})")
                    offset += 2
                case Op.JUMP_IF_FALSE | Op.JUMP:
                    upper = self.code[offset + 1]
                    lower = self.code[offset + 2]
                    operand = (upper << 8) | lower
                    print(f"{str(offset).zfill(3)} {op.name}\t({operand!s})")
                    offset += 3
                case _:
                    print(f"{str(offset).zfill(3)} {op.name}")
                    offset += 1

    def run(self):
        if self.output_ir:
            self.debug_ir()
            print()

        while self.ip < self.end:
            op = self.read_byte()

            if self.stack_trace:
                print(Op(op).name, "".join(list(map(lambda x: f"[ {x} ]", self.stack))))

            match op:
                case Op.POP:
                    self.pop()
                case Op.JUMP:
                    offset = self.read_short()
                    self.ip += offset
                case Op.JUMP_IF_FALSE:
                    offset = self.read_short()
                    if not self.peek():
                        self.ip += offset
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
                case Op.EQUAL:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a == b))
                case Op.NOT_EQUAL:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a != b))
                case Op.LESS:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a < b))
                case Op.LESS_EQUAL:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a <= b))
                case Op.GREATER:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a > b))
                case Op.GREATER_EQUAL:
                    b = self.pop()
                    a = self.pop()
                    self.push(Bool(a >= b))
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
