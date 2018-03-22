import lex
import tree
import run
import sys

def run_code(code):
    toks = lex.make(code)
    code_tree = tree.tree(toks)
    ret = run.run(code_tree)
    return ret


def init():
    run.init()


init()
run_code(open(sys.argv[1]).read())
