# comment me
import time
import view
import errors
import lex
import tree as tmake
import extern
import inspect
from types import ModuleType


def run_fn(ts, perams):
    global fopt
    global vs
    if isinstance(perams[-1], dict) and perams[-1]['type'] == 'unpack':
        perams = perams[:-1] + perams[-1]['data']
    if not isinstance(perams, list) and not isinstance(perams, tuple):
        perams = (perams,)
    if not callable(ts):
        best = None
        bestvar = None
        mat_peram = None
        unpack = None
        upnum = 0
        bestpack = [0, 0]
        rec = -1
        for fn in ts['data']:
            fn, var = fn['fn'], fn['vs']
            per = fn[0]
            bet = {0: 0, 1: 0, 2: 0}
            mp = {}
            if isinstance(per[-1], dict) and per[-1]['type'] == 'oper':
                unpack = per[-1]['post']['data']
                upnum = len(perams) - len(per)
            if len(per) + upnum == len(perams):
                for pl, i in enumerate(per):
                    rp = run_peram(i)
                    if rp[1] == 1:
                        mp[rp[0]] = perams[pl]
                    if rp[0] == perams[pl]:
                        bet[2 - rp[1]] += 1
                    else:
                        bet[rp[1]] += 1
                if bet[0] == 0:
                    if bet[2] > rec:
                        best = fn[1]
                        bestvar = var
                        mat_peram = mp
                        rec = bet[2]
                        bestpack = [unpack, upnum]
        vx = vs
        vs = {}
        gk = True
        if bestpack[0] is not None:
            vs[bestpack[0]] = perams[-bestpack[1] - 1:]
            gk = False
        elif mat_peram is None:
            print('canidate error')
            exit()
        for i in bestvar:
            vs[i] = bestvar[i]
        if gk:
            for i in mat_peram:
                vs[i] = mat_peram[i]
        ret = run_line(best)['data']
        vs = vx
        return ret
    else:
        return ts(*perams)


def run_peram(peram):
    if peram['type'] == 'name':
        return [peram['data'], 1]
    if peram['type'] == 'oper':
        if peram['oper'] == '*':
            return [peram['post']['data'], 1]
    elif peram['type'] == 'int':
        return [run_line(peram)['data'], 0]


def rewrap(tree, data):
    view.view(tree)
    return replace(tree, data)


def replace(tree, data):
    if isinstance(tree, list):
        return [replace(i, data) for i in tree]
    if 1:
        if tree['type'] == 'tuple':
            tree['data'] = [replace(i, data) for i in tree['data']]
        elif tree['type'] == 'code':
            tree['data'] = [replace(i, data) for i in tree['data']]
        elif tree['type'] == 'set':
            tree['pre'] = replace(tree['pre'], data)
            tree['post'] = replace(tree['post'], data)
        elif tree['type'] == 'oper':
            tree['pre'] = replace(tree['pre'], data)
            tree['post'] = replace(tree['post'], data)
        elif tree['type'] == 'fn':
            tree['fn'] = replace(
                {'type': 'name', 'data': tree['fn']}, data)['data']
            tree['perams'] = [replace(i, data) for i in tree['perams']]
        elif tree['type'] == 'int':
            pass
        elif tree['type'] == 'str':
            pass
        elif tree['type'] == 'name':
            if tree['data'] in data:
                tree = data[tree['data']]
        elif tree['type'] == 'flow':
            tree['condition'] = replace(tree['condition'], data)
            tree['then'] = replace(tree['then'], data)
        return tree


def run_line(tree):
    global vs
    global fopt
    # print(list(vs))
    # print(tree)
    if isinstance(tree, list):
        return {'data': run(tree)['data'], 'flags': []}
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
                if isinstance(vs[name], dict):
                    if vs[name]['type'] == 'fn':
                        vs[name] = {'type': 'fn', 'data': vs[name]
                                    ['data'] + to['data']}
                else:
                    vs[name] += to
            elif typ == '-=':
                vs[name] -= to
            elif typ == '?=':
                if name not in vs:
                    vs[name] = to
            return {'data': vs[name], 'flags': []}
        if tree['pre']['type'] == 'fn':
            perams = [i for i in tree['pre']['perams']]
            name = tree['pre']['fn']['data']
            if name not in vs:
                vs[name] = {'type': 'fn', 'data': []}
            ret = {
                'fn': [perams, tree['post']],
                'vs': vs
            }
            vs[name]['data'].append(ret)
            return {'data': vs[name]['data'], 'flags': []}
        if tree['pre']['type'] == 'tuple':
            perams = [i for i in tree['pre']['data']]
            ret = {
                'fn': [perams, tree['post']],
                'vs': vs
            }
            return {'data': {'type': 'fn', 'data': [ret]}, 'flags': ['return']}
        if tree['pre']['type'] == 'oper' and tree['pre']['oper'] == '!':
            tup = tree['pre']['post']['data']
            name = tree['pre']['pre']['data']
            perams = [i['data'] for i in tup]
            to = tree['post']
            vs[name] = {'type': 'macro', 'data': to, 'perams': perams}
            return {'data': vs[name], 'flags': []}
    if tree['type'] == 'int':
        return {'data': int(tree['data']), 'flags': ['return']}
    if tree['type'] == 'float':
        return {'data': float(tree['data']), 'flags': ['return']}
    if tree['type'] == 'str':
        ret = tree['data']
        ret = ret.replace('\\n', '\n')
        ret = ret.replace('\\t', '\t')
        ret = ret.replace('\\s', ' ')
        return {'data': ret, 'flags': ['return']}
    if tree['type'] == 'name':
        if tree['data'] in vs:
            return {'data': vs[tree['data']], 'flags': ['return']}
        else:
            errors.e_var_miss(tree['data'], vs)
    if tree['type'] == 'oper':
        tree['oper'] = tree['oper'] if 'oper' in tree else tree['data']
        if tree['oper'] in ['.']:
            a = run_line(tree['pre'])['data']
            if tree['post']['type'] != 'fn':
                b = tree['post']['data']
                if isinstance(a, dict):
                    ret = a['data'][b]
                else:
                    ret = eval('a.' + b)
                return {'data': ret, 'flags': []}
            if tree['post']['type'] == 'fn':
                b = tree['post']['fn']['data']
                pers = [run_line(i)['data'] for i in tree['post']['perams']]
                ret = None
                flags = False
                if isinstance(a, dict):
                    if a['type'] == 'fn':
                        ret = run_fn(b, pers)
                        flags = ['return'] if flags == 0 else []
                        return {'data': ret, 'flags': flags}
                    if a['type'] == 'module':
                        ret = run_fn(a['data'][b], pers)
                        return {'data': ret, 'flags': ['return']}
                elif isinstance(a, ModuleType) or inspect.isclass(a):
                    ret = eval('a.' + b)
                    if not callable(ret):
                        return {'data': ret, 'flags': ['return']}
                    else:
                        return {'data': run_fn(ret, pers), 'flags': ['return']}
                elif isinstance(a, str):
                    if b == 'replace':
                        ret = a.replace(*pers)
                    elif b == 'sort':
                        ret = list(a)
                        if pers == []:
                            ret.sort()
                        else:
                            p = run_line(pers[0])
                            ret.sort(run_fn(p))
                        ret = ''.join(ret)
                elif isinstance(a, list):
                    if b == 'sort':
                        ret = list(a)
                        if pers == []:
                            ret.sort()
                        else:
                            f = pers[0]
                            ret.sort(key=lambda p: run_fn(f, p))
                    elif b == 'map':
                        ret = [run_fn(pers[0], [i]) for i in a]
                    elif b == 'op':
                        op = pers[0]
                        if op == '+':
                            ret = a[0]
                            for i in a[1:]:
                                ret += i
                        elif op == '-':
                            ret = a[0]
                            for i in a[1:]:
                                ret -= i
                        elif op == '*':
                            ret = a[0]
                            for i in a[1:]:
                                ret *= i
                        elif op == '/':
                            ret = a[0]
                            for i in a[1:]:
                                ret /= i
                        elif op == '%':
                            ret = a[0]
                            for i in a[1:]:
                                ret %= i
                        elif op == '**':
                            ret = a[0]
                            for i in a[1:]:
                                ret = ret**i
                        elif op == '^':
                            ret = a[0]
                            for i in a[1:]:
                                ret = ret**i
                        elif op == '==':
                            ret = a[0]
                            for i in a[1:]:
                                if i == ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '!=':
                            ret = a[0]
                            sl = [a[0]]
                            for i in a[1:]:
                                if i not in sl:
                                    sl.append(i)
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '>':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i < ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '<':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i > ret:
                                    continue
                                else:
                                    ret = False
                                    break
                        elif op == '>=':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i <= ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '<=':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i >= ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '&&':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i and ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                        elif op == '||':
                            ret = bool(a[0])
                            for i in a[1:]:
                                if i or ret:
                                    continue
                                else:
                                    ret = False
                                    break
                            ret = int(ret)
                    elif b == 'get':
                        ret = a
                        while len(pers) > 0:
                            ret = ret[pers[0]]
                            pers = pers[1:]
                    elif b == 'filter':
                        ret = [i for i in a if run_fn(pers[0], [i])]
                return {'data': ret, 'flags': ['return'] if flags == 0 else []}
            elif tree['post']['type'] == 'module':
                b = tree['post']['module']['data']
                if isinstance(a, dict):
                    if a['type'] == 'module':
                        ret = None
                        ret = a['data'][b]
                        return {'data': ret, 'flags': ['return']}
            elif tree['post']['type'] == 'name':
                b = tree['post']['data']
                if isinstance(a, dict):
                    if a['type'] == 'module':
                        ret = a['data'][b]
                        return {'data': ret, 'flags': ['return']}
        if tree['oper'] in ['->', '<-']:
            if tree['oper'] == '->':
                pre = tree['post']
                post = tree['pre']
            else:
                pre = tree['pre']
                post = tree['post']
            post = run_line(post)['data']
            pre = run_line(pre)['data']
            if isinstance(post, dict) and post['type'] == 'unpack':
                args = post['data']
            else:
                args = [post]
            if callable(pre):
                result = run_fn(pre, args)
            elif isinstance(pre, dict):
                if pre['type'] == 'fn':
                    result = run_fn(pre, args)
            return {'data': result, 'flags': []}
        if tree['oper'] in ['!', '!!']:
            if tree['oper'] == '!':
                if tree['pre'] is None:
                    ret = run_line(tree['post'])['data']
                    return {'data': int(not ret), 'flags': ['return']}
                if tree['pre']['data'] not in vs:
                    print(errors.colors.FAIL, end='')
                    print('macro not found', tree['pre']['data'])
                    print('aborting due to error')
                    print(errors.colors.ENDC, end='')
                    exit()
                macro = vs[tree['pre']['data']]
                uperams = tree['post']['data']
                mapdata = {}
                for pl, i in enumerate(macro['perams']):
                    mapdata[i] = uperams[pl]
                treedata = macro['data']
                repd = replace(treedata, mapdata)
                ret = run_line(repd)['data']
                return {'data': ret, 'flags': ['return']}
        if 'pre' in tree and tree['pre'] is not None:
            a = run_line(tree['pre'])['data']
        else:
            a = None
        if 'post' in tree and tree['post'] is not None:
            b = run_line(tree['post'])['data']
        else:
            b = None
        if a is None and b is None:
            return {'data': tree['oper'], 'flags': ['return']}
        o = None
        if tree['oper'] == '+':
            if isinstance(a, dict):
                if a['type'] == 'fn':
                    o = {'type': 'fn', 'data': a['data'] + b['data']}
            else:
                o = a + b
        elif tree['oper'] == '-':
            if a is not None:
                o = a - b
            else:
                o = -b
        elif tree['oper'] == '*':
            if a is not None:
                o = a * b
            else:
                ret = {'data': b, 'type': 'unpack'}
                return {'data': ret, 'flags': ['return']}
        elif tree['oper'] == '/':
            o = a / b
        elif tree['oper'] == '%':
            if isinstance(b, list):
                b = tuple(b)
            o = a % b
        elif tree['oper'] in ['**', '^']:
            o = a**b
        elif tree['oper'] == '<':
            o = a < b
        elif tree['oper'] == '>':
            o = a > b
        elif tree['oper'] == '<=':
            o = a <= b
        elif tree['oper'] == '>=':
            o = a >= b
        elif tree['oper'] == '==':
            o = a == b
        elif tree['oper'] == '!=':
            o = a != b
        elif tree['oper'] == '&&':
            o = a and b
        elif tree['oper'] == '||':
            o = a or b
        elif tree['oper'] == '..':
            if a < b:
                o = list(range(a, b))
            else:
                o = list(range(b, a))
        elif tree['oper'] == '~':
            return {'data':b,'flags':[]}
        if isinstance(o, bool):
            o = int(o)
        return {'data': o, 'flags': ['return']}
    if tree['type'] == 'code':
        return run(tree['data'])
    if tree['type'] == 'flow':
        ret = None
        flags = []
        if tree['flow'] == 'if':
            if run_line(tree['condition'])['data']:
                return run_line(tree['then'])
            return {'data': False, 'flags': []}
        if tree['flow'] == 'while':
            while run_line(tree['condition'])['data']:
                ret = run_line(tree['then'])
                if 'return' in ret['flags']:
                    ret = ret['data']
                    return {'data': ret, 'flags': ['return']}
            return {'data': None, 'flags': []}
        if tree['flow'] == 'loop':
            while 1:
                ret = run_line(tree['then'])
                if 'return' in ret['flags']:
                    ret = ret['data']
                    return {'data': ret, 'flags': ['return']}
            return {'data': None, 'flags': []}
    if tree['type'] == 'fn':
        name = tree['fn']
        if 'data' not in name:
            perams = []
            for i in tree['perams']:
                perams.append(run_line(i)['data'])
            fn = run_line(name)['data']
            ret = run_fn(fn, perams)
            return {'data': ret, 'flags': ['return']}
        name = name['data']
        if name in vs:
            ts = vs[name]
            perams = []
            for i in tree['perams']:
                perams.append(run_line(i)['data'])
            ret = run_fn(ts, perams)
            return {'data': ret, 'flags': ['return']}
        elif name == 'print':
            sepr = run_line(tree['perams'][2])['data'] if len(
                tree['perams']) > 2 else ''
            newl = run_line(tree['perams'][1])['data'] if len(
                tree['perams']) > 1 else '\n'
            ret = run_line(tree['perams'][0])
            print(ret['data'], end=newl, sep=sepr)
            return {'data': ret, 'flags': []}
        elif name == 'len':
            ret = run_line(tree['perams'][0])['data']
            return {'data': len(ret), 'flags': []}
        elif name == 'join':
            ret = run_line(tree['perams'][0])['data']
            return {'data': ''.join(ret), 'flags': []}
        elif name == 'uxtime':
            return {'data': time.time(), 'flags': []}
        elif name == 'eval':
            ret = None
            for i in tree['perams']:
                code = run_line(i)['data']
                toks = lex.make(code)
                code_tree = tmake.tree(toks)
                ret = run(code_tree)['data']
            return {'data': ret['data'], 'flags': ['return']}
        elif name == 'exec':
            ret = None
            for i in tree['perams']:
                code = run_line(i)['data']
                toks = lex.make(code)
                code_tree = tmake.tree(toks)
                ret = run(code_tree)['data']
            return {'data': ret, 'flags': []}
        elif name == 'exit':
            exit()
        elif name == 'vars':
            if len(tree['perams']) > 0:
                ret = vs[run_line(tree['perams'][0])['data']]
            else:
                ret = list(vs)
            return {'data': ret, 'flags': ['return']}
        elif name == 'int':
            ret = int(run_line(tree['perams'][0])['data'])
            return {'data': ret, 'flags': ['return']}
        elif name == 'read':
            ret = open(run_line(tree['perams'][0])['data']).read()
            return {'data': ret, 'flags': ['return']}
        elif name == 'float':
            ret = float(run_line(tree['perams'][0])['data'])
            return {'data': ret, 'flags': ['return']}
        elif name == 'str':
            ret = str(run_line(tree['perams'][0])['data'])
            return {'data': ret, 'flags': ['return']}
        elif name == 'input':
            if len(tree['perams']) > 0:
                ret = input(str(run_line(tree['perams'][0])['data']))
            else:
                ret = input()
            return {'data': ret, 'flags': ['return']}
        elif name == 'import':
            pat = run_line(tree['perams'][0])['data']
            path = extern.tach(pat)
            f = open(path).read()
            toks = lex.make(f)
            code_tree = tmake.tree(toks)
            vx = vs
            vs = {}
            run(code_tree)
            ret = {'type': 'module', 'data': vs}
            vs = vx
            return {'data': ret, 'flags': []}
        elif name == 'inline':
            f = run_line(tree['perams'][0])['data']
            return {'data': f, 'flags': []}
        elif name == 'fp':
            return {'data': fopt, 'flags': []}
        elif name == 'callable':
            ft = run(tree['perams'])
            ret = isinstance(ft, dict) and ft['type'] == 'fn'
            if ret is False and callable(ft):
                ret = True
            return {
                'data': ret['data'][0],
                'flags': ['return']
            }
        elif name == 'del':
            ret = run_line(tree['perams'][0])['data']
            del vs[ret]
            return {
                'data': None,
                'flags': []
            }
        elif name == 'slice':
            ret = run_line(tree['perams'][0])
            to = run_line(tree['perams'][1])['data']
            fr = run_line(tree['perams'][2])['data'] if len(
                tree['perams']) > 2 else 0
            return {
                'data': ret['data'][fr:to],
                'flags': ['return']
            }
        elif name == 'extern':
            ret = extern.imp(run_line(tree['perams'])['data'])
            return {'data': ret, 'flags': ['return']}
        else:
            errors.e_var_miss(name, vs)
    if tree['type'] == 'tuple':
        ret = []
        for i in tree['data']:
            tap = run_line(i)
            ret.append(tap['data'])
        return {'data': ret, 'flags': ['return']}
    print(errors.colors.FAIL, end='')
    print('unknown sequence of tokens')
    print(errors.colors.ENDC, end='')
    exit()


def run(tree):
    ret = None
    for i in tree:
        ret = run_line(i)
        if 'return' in ret['flags']:
            ret = ret['data']
            return {'data': ret, 'flags': ['return']}
    return {'data': None, 'flags': []}


def init():
    global vs
    global fopt
    global ops
    vs = {'true': 1, 'false': 0}
    fopt = {}


def end():
    pass
