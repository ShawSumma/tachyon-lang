import lex
import view
import tree
import run
import sys
def run_code(code):
    toks = lex.make(code)
    code_tree = tree.tree(toks)
    #view.view(code_tree)
    prev = code_tree
    #view.view(code_tree)
    ret = run.run(code_tree)
def init():
    run.init()
init()
run_code(open(sys.argv[1]).read())
