def view(v, di=None, dep=0):
    depth = dep
    w = ' ' * depth
    print(w, end='')
    if di is not None:
        print(str(di) + ' : ', end='')
        w += ' ' * (len(str(di)) + 3)
    if isinstance(v, list) or isinstance(v, tuple):
        print('[')
        for i in v:
            view(i, dep=depth + 1)
        print(w + ']')
        return
    if isinstance(v, dict):
        print('{')
        for i in v:
            view(v[i], di=i, dep=depth + 1)
        print(w + '}')
        return
    print(w + str(v))
