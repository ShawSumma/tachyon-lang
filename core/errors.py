class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def c_err():
    print(colors.FAIL,end='')
def e_token():
    c_err()
    print('no valid token could be found!')
    gone()
def e_pair_close(chs):
    c_err()
    print('extranious "{}", could not pair it with a "{}"'.format(chs[1],chs[0]))
    gone()
def e_pair_open(chs):
    c_err()
    print('unclosed "{}", could not pair it with a "{}"'.format(chs[1],chs[0]))
    gone()
def e_unk_oper(opers):
    c_err()
    print('unkown operaror "{}"'.format(opers))
    gone()
    exit()
def e_var_miss(var,vs):
    c_err()
    print('not found {}'.format(var))
    gone()
def gone():
    print('aborting due to error')
    print(colors.ENDC,end='')
    if err_exit:
        exit()
err_exit = True
