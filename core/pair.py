import errors
def pair(x,chs,depth=0):
    hold = {}
    dep = 0
    pl = 0
    ret = {}
    for i in x:
        if i == chs[0]:
            dep += 1
            hold[dep] = pl
        elif i == chs[1]:
            if depth == 0 or dep <= depth:
                if dep <= 0:
                    errors.e_pair_open(chs)
                ret[hold[dep]] = pl
            dep -= 1
        pl += 1
    if dep > 0:
        errors.e_pair_close(chs)
    return ret
