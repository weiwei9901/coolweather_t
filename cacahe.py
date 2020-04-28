import time
from datetime import datetime
from dis import dis
from inspect import signature, Signature
from functools import wraps


def cache(timeset=5):
    def cacahe_inner(fn):
        res_dict = {}

        @wraps(fn)
        def wrapper(*arg, **kwargs):
            for key, (_, settime) in list(res_dict.items()):
                if datetime.now().timestamp() - settime > timeset:
                    res_dict.pop(key)

            param_list = []
            param_dict = {}

            fn_sig = signature(fn).parameters
            param_list.extend(fn_sig.keys())
            for idx, val in enumerate(arg):
                param_dict[param_list[idx]] = val
            param_dict.update(kwargs)
            # 添加默认
            for name in param_list:
                if name not in param_dict.keys():
                    param_dict[name] = fn_sig.get(name).default

            tuple_param = tuple(sorted(param_dict.items()))
            fn_hash = hash(tuple_param)

            if fn_hash not in res_dict.keys():
                res_dict[fn_hash] = fn(*arg, **kwargs), datetime.now().timestamp()
            return res_dict[fn_hash][0]

        return wrapper

    return cacahe_inner


def print_time(fn):
    def wrapper(*args, **kwargs):
        st_time = datetime.now()
        res = fn(*args, **kwargs)
        print(datetime.now()-st_time)
        return res
    return wrapper

@print_time
@cache(6)
def n(a, x=1):
    time.sleep(5)
    """this is n"""
    return 'hello'


print(n(3))
print((n(3, x=1)))
time.sleep(5)
print(n(3))
