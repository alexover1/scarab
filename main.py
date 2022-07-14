from scarab import Parser, Compiler, VM

if __name__ == '__main__':
    parser = Parser('''
    if 0 or 1 print "True"
    else print "False"
    ''')
    compiler = Compiler(parser)
    compiler.compile()

    vm = VM(compiler.code, compiler.constants, ir=True, trace=True)
    vm.run()
