import pair
import view
import errors
def tree_paren(code):
    datas =[i['data'] for i in code]
    pairs = {
        'paren':pair.pair(datas,['(',')']),
        'curly':pair.pair(datas,['{','}']),
        'square':pair.pair(datas,['[',']']),
    }
    pl = 0
    ret = [[]]
    while pl < len(code):
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type' : 'tuple',
                'data' : tree_paren(code[pl+1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type' : 'code',
                'data' : tree(code[pl+1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        elif code[pl]['type'] == 'comma':
            ret.append([])
        else:
            ret[-1].append(code[pl])
        pl += 1
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        recal.append(tree_line(i))
    return recal
def tree_line(code):
    if len(code) == 0:
        return None
    datas =[i['data'] for i in code]
    types =[i['type'] for i in code]
    if datas[0] in ['if','else','elif','while','do','loop']:
        ret = {
            'type' : 'flow',
            'flow' : datas[0],
            'condition' : tree_line(code[1:-1]),
            'then' : code[-1]
        }
        if datas[0] == 'loop':
            ret['condition'] = {'type':'int','data':'1'}
        return ret
    if len(code) == 1:
        return {'type':code[0]['type'],'data':code[0]['data']}
    if 'oper' in types:
        #view.view(datas)
        finds = [['error'],['.'],['!','!!'],[':'],['**','^'],['*','/','%'],['+','-'],['<>'],['<','>','<=','>='],['!=','=='],['&&'],['||'],['-=','+=','/=','**=','*=','=','?=']]
        finds = finds[::-1]
        ob = False
        for order in finds:
            for oper in order:
                if oper in datas:
                    ob = True
                    break
            if ob:
                break
        if oper == 'error':
            errors.e_unk_oper(datas[types.index('oper')])
        negitive = ['.']
        if oper not in negitive:
            oper_ind = datas.index(oper)
        else:
            oper_ind = len(datas)-1-datas[::-1].index(oper)
        if oper in ['-=','+=','/=','**=','*=','=','?=']:
            return {
                'type': 'set',
                'set': datas[oper_ind],
                'pre': tree_line(code[:oper_ind]),
                'post': tree_line(code[oper_ind+1:])
            }
        return {
            'type': 'oper',
            'oper': oper,
            'pre' : tree_line(code[:oper_ind]),
            'post' : tree_line(code[oper_ind+1:])
        }
    if len(code) > 1 and code[-1]['type'] == 'tuple':
        return {
            'type': 'fn',
            'fn': tree_line(code[:-1]),
            'perams':code[-1]['data']
        }
def tree(code,typ='newline'):
    datas =[i['data'] for i in code]
    pairs = {
        'paren':pair.pair(datas,['(',')']),
        'curly':pair.pair(datas,['{','}']),
        'square':pair.pair(datas,['[',']']),
    }
    pl = 0
    ret = [[]]
    while pl < len(code):
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type' : 'tuple',
                'data' : tree_paren(code[pl+1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type' : 'code',
                'data' : tree(code[pl+1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        elif code[pl]['type'] == 'newline':
            ret.append([])
        else:
            ret[-1].append(code[pl])
        pl += 1
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        #print(i)
        #print(i)
        recal.append(tree_line(i))
    return recal
