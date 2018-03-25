# pairs mathching tokens
import pair
# error handleing
import errors

# trees code inside parens


def tree_paren(code):
    # raw token data
    datas = [i['data'] for i in code]
    # get pairs for each type
    pairs = {
        'paren': pair.pair(datas, ['(', ')']),
        'curly': pair.pair(datas, ['{', '}']),
        'square': pair.pair(datas, ['[', ']']),
    }
    pl = 0
    ret = [[]]
    # iterate over and make tuples and code out of the comma placement
    while pl < len(code):
        # is it left
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type': 'tuple',
                'data': tree_paren(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # is it right
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type': 'code',
                'data': tree(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp\
                # is it comma
        elif code[pl]['type'] == 'comma':
            ret.append([])
        # its not a paren or comma
        else:
            ret[-1].append(code[pl])
        pl += 1
    # delete empty sequences
    # this is why (1,,1,,1,,) returns [1,1,1]
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        recal.append(tree_line(i))
    return recal

# a single "line" of code, lines end at newlines outside of paired things


def tree_line(code):
    # none is deleted, so no empty lines
    if len(code) == 0:
        return None
    # raw token data
    datas = [i['data'] for i in code]
    # types of tokens
    types = [i['type'] for i in code]
    # currently implemneted: if, else, loop, and while
    if datas[0] in ['if', 'else', 'elif', 'while', 'do', 'loop']:
        ret = {
            'type': 'flow',
            'flow': datas[0],
            'condition': tree_line(code[1:-1]),
            'then': code[-1]
        }
        # loops take no perams
        if datas[0] == 'loop':
            ret['condition'] = {'type': 'int', 'data': '1'}
        return ret
    # its just a return value
    if len(code) == 1:
        return {'type': code[0]['type'], 'data': code[0]['data']}
    # its math or listop
    if 'oper' in types:
        finds = []
        # error and listop
        finds += [['error'], ['.'], ['!', '!!'], ['..']]
        # common math
        finds += [['**', '^'], ['*', '/', '%'], ['+', '-']]
        #<> is in, not implemneted fully, equality part 1
        finds += [['<>'], ['<', '>', '<=', '>=']]
        # equality part 2
        finds += [['!=', '=='], ['&&'], ['||']]
        # list push and pop
        finds += [['->', '<-']]
        # set
        finds += [['-=', '+=', '/=', '**=', '*=', '=', '?=']]
        # new op, force return and force stay
        finds += [['~']]
        # its backwards
        finds = finds[::-1]
        # ob is operator break flag
        ob = False
        # finds operator that best matches
        for order in finds:
            for oper in order:
                if oper in datas:
                    ob = True
                    break
            if ob:
                break
        # if it was not fount: raise an error
        if oper == 'error':
            errors.e_unk_oper(datas[types.index('oper')])
        # list of backwards operators
        negitive = ['.', '->']
        if oper not in negitive:
            oper_ind = datas.index(oper)
        else:
            oper_ind = len(datas) - 1 - datas[:: -1].index(oper)
        # set operators get their own logic
        if oper in ['-=', '+=', '/=', '**=', '*=', '=', '?=']:
            return {
                'type': 'set',
                'set': datas[oper_ind],
                'pre': tree_line(code[:oper_ind]),
                'post': tree_line(code[oper_ind + 1:])
            }
        return {
            'type': 'oper',
            'oper': oper,
            'pre': tree_line(code[:oper_ind]),
            'post': tree_line(code[oper_ind + 1:])
        }
    # handle regular and multi tuples
    if len(code) > 1 and code[-1]['type'] == 'tuple':
        return {
            'type': 'fn',
            'fn': tree_line(code[:-1]),
            'perams': code[-1]['data']
        }
# what to call from external code, code is tokens from lex.py


def tree(code, typ='newline'):
    # raw token datsa
    datas = [i['data'] for i in code]
    # get pairs for each type
    pairs = {
        'paren': pair.pair(datas, ['(', ')']),
        'curly': pair.pair(datas, ['{', '}']),
        'square': pair.pair(datas, ['[', ']']),
    }
    pl = 0
    ret = [[]]
    # iterate over and make tuples and code out of the comma placement
    while pl < len(code):
        # is it left
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type': 'tuple',
                'data': tree_paren(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # is it right
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type': 'code',
                'data': tree(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # it is newline
        elif code[pl]['type'] == 'newline':
            ret.append([])
        # its not left, right, or newline
        else:
            ret[-1].append(code[pl])
        pl += 1
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        recal.append(tree_line(i))
    return recal
