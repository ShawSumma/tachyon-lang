import re
t_ignore = ' \n\t'
t_int = re.compile(r'[0-9]+')
t_float = re.compile(r'[0-9]+\.[0-9]+')
t_paren = '()'
t_curly = '{}'
t_list = '[]'
t_oper = re.compile(r'[\/\~\!\@\#\$\%\^\&\*\=\+\-\<\>\?\|\\\:\.]+')
t_comma = ','
t_newline = ';\n'
#t_emoji = re.compile(r'[\U00010000-\U0010ffff]+', flags=re.UNICODE)


def make(code):
    while '\\\n' in code:
        code = code.replace('\\\n', '')
    tokens = []
    line = 1
    while True:
        while len(code) > 0 and code[0] in t_ignore:
            if code[0] == '\n':
                tokens.append({
                    'type': 'newline',
                    'data': code[0],
                    'line': line
                })
                line += 1
            code = code[1:]
        if len(code) == 0:
            return tokens
        m_int = t_int.match(code)
        m_float = t_float.match(code)
        m_oper = t_oper.match(code)
        d_paren = code[0] in t_paren
        d_curly = code[0] in t_curly
        d_list = code[0] in t_list
        d_comma = code[0] in t_comma
        d_newline = code[0] in t_newline
        if code[0] in '\"\'':
            mat = code[0]
            code = code[1:]
            strx = ''
            while code[0] != mat:
                strx += code[0]
                code = code[1:]
            code = code[1:]
            tokens.append({
                'type': 'str',
                'data': strx,
                'line': line,
            })
        elif code[:2] == '/*':
            code = code[2:]
            while code[:2] != '*/':
                code = code[1:]
            code = code[2:]
        elif m_float != None:
            tokens.append({
                'type': 'float',
                'data': code[:m_float.span()[1]],
                'line': line,
            })
            code = code[m_float.span()[1]:]
        elif m_int != None:
            tokens.append({
                'type': 'int',
                'data': code[:m_int.span()[1]],
                'line': line,
            })
            code = code[m_int.span()[1]:]
        elif m_oper != None:
            tokens.append({
                'type': 'oper',
                'data': code[:m_oper.span()[1]],
                'line': line,
            })
            code = code[m_oper.span()[1]:]
        elif d_paren:
            tokens.append({
                'type': 'oper',
                'data': code[:1],
                'line': line,
            })
            code = code[1:]
        elif d_curly:
            tokens.append({
                'type': 'curly',
                'data': code[:1],
                'line': line,
            })
            code = code[1:]
        elif d_list:
            tokens.append({
                'type': 'listop',
                'data': code[:1],
                'line': line,
            })
            code = code[1:]
        elif d_comma:
            tokens.append({
                'type': 'comma',
                'data': code[:1],
                'line': line,
            })
            code = code[1:]
        elif d_newline:
            tokens.append({
                'type': 'newline',
                'data': code[:1],
                'line': line,
            })
            code = code[1:]
        else:
            r = ''
            while len(code) > 1:
                r += code[0]
                code = code[1:]
                m_int = None  # t_int.match(code)
                m_float = t_float.match(code)
                m_oper = t_oper.match(code)
                mat = [m_int, m_float, m_oper]
                mat = max(map(lambda x: x != None, mat)) == 1
                lis = t_paren + t_curly + t_list + t_comma + t_newline + t_ignore
                imat = code[0] in lis
                # print(imat,code[0],lis)
                if mat or imat:
                    break
            tokens.append({
                'type': 'name',
                'data': r,
                'line': line,
            })
            #code = code[1:]
