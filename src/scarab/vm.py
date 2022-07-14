from typing import TypeVar

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


T = TypeVar('T')


class Stack:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items: list[T] = [None] * capacity
        self.top = -1

    def __getitem__(self, item):
        if item > self.capacity or self.items[item] is None:
            raise IndexError(item)
        return self.items[item]

    def __setitem__(self, index, value):
        if index > self.capacity:
            raise IndexError(index)

        if index > self.top:
            self.top = index

        self.items[index] = value

    @property
    def empty(self):
        return self.top < 0

    def push(self, value):
        self.top += 1

        if self.top >= self.capacity:
            raise StackOverflow

        self[self.top] = value

    def pop(self):
        if self.empty:
            raise StackUnderflow
        result = self[self.top]
        self[self.top] = None
        self.top -= 1
        return result

    def peek(self, distance=0):
        index = self.top - distance
        if index < 0:
            raise IndexError(index)
        return self.items[index]


NIL = Nil()
TRUE = Bool(True)
FALSE = Bool(False)


class VM:
    def __init__(self, code: bytearray, constants: list[Object], *, ir=False, trace=False, capture=False):
        self.code = code
        self.constants = constants
        self.ip = -1
        self.stack = Stack(256)
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
                case Op.DEFINE_GLOBAL | Op.GET_GLOBAL | Op.SET_GLOBAL:
                    constant = self.constants[self.code[offset + 1]]
                    print(f"{str(offset).zfill(3)} {op.name}\t({constant!s})")
                    offset += 2
                case Op.GET_LOCAL | Op.SET_LOCAL:
                    local = self.code[offset + 1]
                    print(f"{str(offset).zfill(3)} {op.name}\t({local})")
                    offset += 2
                case Op.JUMP_IF_FALSE | Op.JUMP | Op.LOOP:
                    upper = self.code[offset + 1]
                    lower = self.code[offset + 2]
                    operand = (upper << 8) | lower
                    print(f"{str(offset).zfill(3)} {op.name}\t({operand!s})")
                    offset += 3
                case _:
                    print(f"{str(offset).zfill(3)} {op.name}")
                    offset += 1

    def print(self, value):
        if self.capture_output:
            self.captured.append(value)
        else:
            print(value)

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
                    self.stack.pop()
                case Op.JUMP:
                    offset = self.read_short()
                    self.ip += offset
                case Op.JUMP_IF_FALSE:
                    offset = self.read_short()
                    if not self.stack.peek():
                        self.ip += offset
                case Op.LOOP:
                    offset = self.read_short()
                    self.ip -= offset
                case Op.CONSTANT:
                    self.stack.push(self.read_constant())
                case Op.TRUE:
                    self.stack.push(TRUE)
                case Op.FALSE:
                    self.stack.push(FALSE)
                case Op.PRINT:
                    self.print(self.stack.pop())
                case Op.ADD:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a + b)
                case Op.SUB:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a - b)
                case Op.MUL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a * b)
                case Op.DIV:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a / b)
                case Op.EQUAL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a == b))
                case Op.NOT_EQUAL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a != b))
                case Op.LESS:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a < b))
                case Op.LESS_EQUAL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a <= b))
                case Op.GREATER:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a > b))
                case Op.GREATER_EQUAL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(Bool(a >= b))
                case Op.DEFINE_GLOBAL:
                    name = self.read_constant()
                    self.table[name] = self.stack.peek()
                case Op.SET_GLOBAL:
                    name = self.read_constant()
                    if name not in self.table:
                        raise NameError(name)
                    self.table[name] = self.stack.peek()
                case Op.GET_GLOBAL:
                    name = self.read_constant()
                    if name in self.table:
                        self.stack.push(self.table[name])
                    else:
                        raise NameError(name)
                case Op.SET_LOCAL:
                    slot = self.read_byte()
                    self.stack[slot] = self.stack.peek()
                case Op.GET_LOCAL:
                    slot = self.read_byte()
                    self.stack.push(self.stack[slot])
                case _:
                    raise UnknownOpCode(op)
