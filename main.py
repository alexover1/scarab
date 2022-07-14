from scarab import Lexer, Compiler, VM

if __name__ == '__main__':
    lexer = Lexer('''
    if 0 or 1 print "True"
    else print "False"
    ''')

    compiler = Compiler(lexer)
    compiler.compile()

    vm = VM(compiler.code, compiler.constants, ir=True, trace=True)
    vm.run()
