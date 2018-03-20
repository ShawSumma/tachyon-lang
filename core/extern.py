from importlib.machinery import SourceFileLoader
import tach_path
def tach(path):
    ret = path
    for i in tach_path.tachp:
        if path.startswith(i):
            ret = tach_path.tachp[i]+path[len(i):]
            break
    return ret
def imp(f):
    f = tach(f)
    ext = SourceFileLoader("ext", f).load_module()
    return ext
