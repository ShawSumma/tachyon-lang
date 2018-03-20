import time
import view
import errors
import lex
import view
import tree as tmake
import time, math
import operator
import extern
import inspect
from types import ModuleType
def run_fn(ts,perams):
    global fopt
    global vs
    global optimize
    if not callable(ts):
        tup = tuple(perams)
        best = None
        bestvar = None
        mat_peram = None
        rec = -1
        for fn in ts['data']:
            fn,var = fn['fn'],fn['vs']
            per = fn[0]
            bet = {0:0,1:0,2:0}
            mp = {}
            if len(per) == len(perams):
                for pl,i in enumerate(per):
                    rp = run_peram(i)
                    if rp[1] == 1:
                        mp[rp[0]] = perams[pl]
                    if rp[0] == perams[pl]:
                        bet[2-rp[1]] += 1
                    else:
                        bet[rp[1]] += 1
                if bet[0] == 0:
                    #print(bet)
                    if bet[2] > rec:
                        best = fn[1]
                        bestvar = var
                        mat_peram = mp
                        rec = bet[2]
        vx = vs
        if mat_peram == None:
            print
        vs = {**bestvar,**mat_peram}
        for i in vx:
            if isinstance(vx[i],dict):
                vs[i] = vx[i]
        #print(best)
        ret = run_line(best)['data']
        vs = vx
        return ret
    else:
        return ts(*perams)
def run_peram(peram):
    if peram['type'] == 'name':
        return [peram['data'],1]
    return [run_line(peram)['data'],0]
def rewrap(tree,data):
    view.view(tree)
    return replace(tree,data)
def replace(tree,data):
    if isinstance(tree,list): return [replace(i,data) for i in tree]
    if 1:
        if tree['type'] == 'tuple':
            tree['data'] =  [replace(i,data) for i in tree['data']]
        elif tree['type'] == 'code':
            tree['data'] =  [replace(i,data) for i in tree['data']]
        elif tree['type'] == 'set':
            tree['pre'] = replace(tree['pre'],data)
            tree['post'] = replace(tree['post'],data)
        elif tree['type'] == 'oper':
            tree['pre'] = replace(tree['pre'],data)
            tree['post'] = replace(tree['post'],data)
        elif tree['type'] == 'fn':
            tree['fn'] = replace({'type':'name','data':tree['fn']},data)['data']
            tree['perams'] = [replace(i,data) for i in tree['perams']]
            #print(tree)
        elif tree['type'] == 'int':
            pass
        elif tree['type'] == 'str':
            pass
        elif tree['type'] == 'name':
            if tree['data'] in data:
                tree = data[tree['data']]
        elif tree['type'] == 'flow':
            tree['condition'] = replace(tree['condition'],data)
            tree['then'] = replace(tree['then'],data)
        return tree
def run_line(tree):
    #print(tree)
    global vs
    global fopt
    global optimize
    #print('vs')
    #print(list(vs))
    #view.view(tree)
    #print(tree)
    #time.sleep(0.02)
    if isinstance(tree,list):
        return {'data':run(tree)['data'],'flags':[]}
    if tree['type'] == 'set':
        if tree['pre']['type'] == 'name':
            val = run_line(tree['post'])
            name = tree['pre']['data']
            typ = tree['set']
            to = val['data']
            if typ == '=':
                vs[name] = to
            elif typ == '*=':
                vs[name] *= to
            elif typ == '/=':
                vs[name] /= to
            elif typ == '+=':
                if isinstance(vs[name],dict):
                    if vs[name]['type'] == 'fn':
                        vs[name] = {'type':'fn','data':vs[name]['data']+to['data']}
                else:
                    vs[name] += to
            elif typ == '-=':
                vs[name] -= to
            elif typ == '?=':
                if name not in vs:
                    vs[name] = to
            return {'data':vs[name],'flags':[]}
        if tree['pre']['type'] == 'fn':
            perams = [i for i in tree['pre']['perams']]
            name = tree['pre']['fn']['data']
            if not name in vs:
                vs[name] = {'type':'fn','data':[]}
            ret = {
                'fn':[perams,tree['post']],
                'vs':vs
            }
            vs[name]['data'].append(ret)
            return {'data':vs[name]['data'],'flags':[]}
        if tree['pre']['type'] == 'tuple':
            perams = [i for i in tree['pre']['data']]
            ret = {
                'fn':[perams,tree['post']],
                'vs':vs
            }
            return {'data':{'type':'fn','data':[ret]},'flags':['return']}
        if tree['pre']['type'] == 'oper' and tree['pre']['oper'] == '!':
            tup = tree['pre']['post']['data']
            name = tree['pre']['pre']['data']
            perams = [i['data'] for i in tup]
            to = tree['post']
            vs[name] = {'type':'macro','data':to,'perams':perams}
            return {'data':vs[name],'flags':[]}
    if tree['type'] == 'int':
        return {'data':int(tree['data']),'flags':['return']}
    if tree['type'] == 'float':
        return {'data':float(tree['data']),'flags':['return']}
    if tree['type'] == 'str':
        ret = tree['data']
        ret = ret.replace('\\n','\n')
        ret = ret.replace('\\t','\t')
        ret = ret.replace('\\s',' ')
        return {'data':ret,'flags':['return']}
    if tree['type'] == 'name':
        if tree['data'] in vs:
            return {'data':vs[tree['data']],'flags':['return']}
        else:
            errors.e_var_miss(tree['data'],vs)
    if tree['type'] == 'oper':
        if tree['oper'] in ['.']:
            a = run_line(tree['pre'])['data']
            #print(a)
            if tree['post']['type'] == 'fn':
                b = tree['post']['fn']
                pers = [run_line(i)['data'] for i in tree['post']['perams']]
                ret = None
                flags = False
                if isinstance(a,dict):
                    ret = None
                    if b == 'call':
                        ret = run_fn(a,pers)
                    return {'data':ret,'flags':['return'] if flags == 0 else []}
                elif isinstance(a,ModuleType) or inspect.isclass(a):
                    ret = eval('a.'+b['data'])
                    if not callable(ret):
                        return {'data':ret,'flags':['return']}
                    else:
                        return {'data':run_fn(ret,pers),'flags':['return']}
                elif isinstance(a,str):
                    if b == 'replace':
                        ret = a.replace(*pers)
                    elif b == 'sort':
                        ret = list(a)
                        ret.sort()
                        ret = ''.join(ret)
                elif isinstance(a,list):
                    if b == 'sort':
                        ret = a
                        ret.sort()
                    elif b == 'map':
                        ret = [run_fn(pers[0],[i]) for i in a]
                    elif b == 'sum':
                        ret = sum([run_fn(pers[0],[i]) for i in a])
                    elif b == 'get':
                        ret = a
                        while len(pers) > 0:
                            ret = ret[pers[0]]
                            pers = pers[1:]
                    elif b == 'filter':
                        ret = [i for i in a if run_fn(pers[0],[i]) ]
                return {'data':ret,'flags':['return'] if flags == 0 else []}
        if tree['oper'] in ['!','!!']:
            if tree['oper'] == '!':
                if tree['pre']['data'] not in vs:
                    print(errors.colors.FAIL,end='')
                    print('macro not found', tree['pre']['data'])
                    print('aborting due to error')
                    print(errors.colors.ENDC,end='')
                    exit()
                macro = vs[tree['pre']['data']]
                uperams = tree['post']['data']
                mapdata = {}
                for pl,i in enumerate(macro['perams']):
                    mapdata[i] = uperams[pl]
                treedata = macro['data']
                repd = replace(treedata,mapdata)
                #print(repd)
                ret = run_line(repd)['data']
                return {'data':ret,'flags':['return']}
        if tree['pre'] != None:
            a = run_line(tree['pre'])['data']
        else:
            a = None
        #print(tree['post'])
        if tree['post'] != None:
            b = run_line(tree['post'])['data']
        else:
            b = None
        o = None
        if tree['oper'] == '+':
            if isinstance(a,dict):
                if a['type'] == 'fn':
                    o = {'type':'fn','data':a['data']+b['data']}
            else:
                o = a+b
        elif tree['oper'] == '-':
            if a != None:
                o = a-b
            else:
                o = -b
        elif tree['oper'] == '*':
            o = a*b
        elif tree['oper'] == '/':
            o = a/b
        elif tree['oper'] == '%':
            if isinstance(b,list):
                b = tuple(b)
            o = a%b
        elif tree['oper'] in ['**','^']:
            o = a**b
        elif tree['oper'] == '<':
            o = a<b
        elif tree['oper'] == '>':
            o = a>b
        elif tree['oper'] == '<=':
            o = a<=b
        elif tree['oper'] == '>=':
            o = a>=b
        elif tree['oper'] == '==':
            o = a==b
        elif tree['oper'] == '!=':
            o = a!=b
        elif tree['oper'] == '&&':
            o = a and b
        elif tree['oper'] == '||':
            o = a or b
        elif tree['oper'] == ':':
            o = list(range(a,b))
        if isinstance(o,bool):
            o = int(o)
        return {'data':o,'flags':['return']}
    if tree['type'] == 'code':
        return run(tree['data'])
    if tree['type'] == 'flow':
        ret = None
        flags = []
        if tree['flow'] == 'if':
            if run_line(tree['condition'])['data']:
                return run_line(tree['then'])
            return {'data':False,'flags':[]}
        if tree['flow'] == 'while':
            while run_line(tree['condition'])['data']:
                ret = run_line(tree['then'])
                if 'return' in ret['flags']:
                    ret = ret['data']
                    return {'data':ret,'flags':['return']}
            return {'data':None,'flags':[]}
        if tree['flow'] == 'loop':
            while 1:
                ret = run_line(tree['then'])
                if 'return' in ret['flags']:
                    ret = ret['data']
                    return {'data':ret,'flags':['return']}
            return {'data':None,'flags':[]}
    if tree['type'] == 'fn':
        name = tree['fn']
        if 'data' not in name:
            perams = []
            for i in tree['perams']:
                perams.append(run_line(i)['data'])
            fn = run_line(name)['data']
            ret = run_fn(fn,perams)
            return {'data':ret,'flags':['return']}
        name = name['data']
        if name in vs:
            ts = vs[name]
            perams = []
            for i in tree['perams']:
                perams.append(run_line(i)['data'])
            ret = run_fn(ts,perams)
            return {'data':ret,'flags':['return']}
        elif name == 'print':
            sepr = run_line(tree['perams'][2])['data'] if len(tree['perams']) > 2 else ''
            newl = run_line(tree['perams'][1])['data'] if len(tree['perams']) > 1 else '\n'
            ret = run_line(tree['perams'][0])
            print(ret['data'],end=newl,sep=sepr)
            return {'data':ret,'flags':[]}
        elif name == 'len':
            ret = run_line(tree['perams'][0])['data']
            return {'data':len(ret),'flags':[]}
        elif name == 'join':
            ret = run_line(tree['perams'][0])['data']
            return {'data':''.join(ret),'flags':[]}
        elif name == 'uxtime':
            return {'data':time.time(),'flags':[]}
        elif name == 'eval':
            ret = None
            for i in tree['perams']:
                code = run_line(i)['data']
                toks = lex.make(code)
                code_tree = tmake.tree(toks)
                ret = run(code_tree)['data']
            return {'data':ret,'flags':['return']}
        elif name == 'exec':
            ret = None
            for i in tree['perams']:
                code = run_line(i)['data']
                toks = lex.make(code)
                code_tree = tmake.tree(toks)
                ret = run(code_tree)['data']
            return {'data':ret,'flags':[]}
        elif name == 'exit':
            exit()
        elif name == 'optimize':
            fopt = {}
            ret = run_line(tree['perams'][0])['data']
            optimize = ret
            return {'data':ret,'flags':[]}
        elif name == 'vars':
            if len(tree['perams']) > 0:
                ret = vs[run_line(tree['perams'][0])['data']]
            else:
                ret = list(vs)
            return {'data':ret,'flags':['return']}
        elif name == 'int':
            return {'data':int(run_line(tree['perams'][0])['data']),'flags':['return']}
        elif name == 'read':
            return {'data':open(run_line(tree['perams'][0])['data']).read(),'flags':['return']}
        elif name == 'float':
            return {'data':float(run_line(tree['perams'][0])['data']),'flags':['return']}
        elif name == 'str':
            return {'data':str(run_line(tree['perams'][0])['data']),'flags':['return']}
        elif name == 'input':
            return {'data':input(str(run_line(tree['perams'][0])['data'])) if len(tree['perams']) > 0 else input(),'flags':['return']}
        elif name == 'import':
            f = open(run_line(tree['perams'][0])['data']).read()
            toks = lex.make(f)
            code_tree = tmake.tree(toks)
            ret = run(code_tree)
            return {'data':ret,'flags':[]}
        elif name == 'inline':
            f = run_line(tree['perams'][0])['data']
            return {'data':f,'flags':[]}
        elif name == 'fp':
            return {'data':fopt,'flags':[]}
        elif name == 'sum':
            ret = sum([run_line(i) for i in tree['perams']])
            return {
                'data' : ret,
                'flags' : ['return']
            }
        elif name == 'callable':
            ret = run(tree['perams'])
            ret = isinstance(ret,dict) and ret['type'] == 'fn'
            return {
                'data' : ret['data'][0],
                'flags' : ['return']
            }
        elif name == 'del':
            ret = run_line(tree['perams'][0])['data']
            del vs[ret]
            return {
                'data' : None,
                'flags' : []
            }
        elif name == 'slice':
            ret = run_line(tree['perams'][0])
            to = run_line(tree['perams'][1])['data']
            fr = run_line(tree['perams'][2])['data'] if len(tree['perams']) > 2 else 0
            return {
                'data' : ret['data'][fr:to],
                'flags' : ['return']
            }
        elif name == 'extern':
            ret = extern.imp(run_line(tree['perams'])['data'])
            return {'data':ret,'flags':['return']}
        else:
            errors.e_var_miss(name,vs)
    if tree['type'] == 'tuple':
        ret = []
        for i in tree['data']:
            tap = run_line(i)
            ret.append(tap['data'])
        return {'data':ret,'flags':['return']}
    print(errors.colors.FAIL,end='')
    print('unknown sequence of tokens')
    print(errors.colors.ENDC,end='')
    exit()
def run(tree):
    ret = None
    for i in tree:
        #view.view(i)
        ret = run_line(i)
        if 'return' in ret['flags']:
            ret = ret['data']
            return {'data':ret,'flags':['return']}
    return {'data':None,'flags':[]}
def init():
    global vs
    global optimize
    global fopt
    vs = {'true':1,'false':0}
    optimize = 0
    fopt = {}
def end():
    pass
    #print(vs)
