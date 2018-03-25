import lex
import tree
import run
import sys


def run_code(code):
    toks = lex.make(code)
    code_tree = tree.tree(toks)
    ret = run.run(code_tree)
    return ret


def repl():
    while 1:
        uin = input('>>> ')
        ran = run_code(uin)['data']
        if ran != None:
            print(ran)

def init():
    run.init()


init()
if len(sys.argv) > 1:
    run_code(open(sys.argv[1]).read())
else:
    repl()
