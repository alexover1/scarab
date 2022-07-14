from scarab.compiler import Compiler
from scarab.parser import Parser
from scarab.vm import VM

if __name__ == '__main__':
    parser = Parser('''
    a = 100
    {
        a = a
        b = 6
        print a + b
    }
    ''')
    compiler = Compiler(parser)
    compiler.compile()

    vm = VM(compiler.code, compiler.constants)
    vm.run()
