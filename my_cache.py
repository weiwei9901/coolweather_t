"""

模仿写的一个缓存，不能在字典元素遍历时删除，否则会引起报错

"""

import datetime
import time
from inspect import signature


def cachetime(time_=5):

    def mycache(fn):
        res_cache = {}
        params = []
        sig = signature(fn).parameters

        def wrapper(*args, **kwargs):
            cache_dict = {}

            def get_dict():
                delete_list = []
                params.extend(sig.keys())
                for key, (_, t) in res_cache.items():
                    if datetime.datetime.now().timestamp() - t > time_:
                        delete_list.append(key)
                for v in delete_list:
                    res_cache.pop(v)
                for k, v in enumerate(args):
                    key = params[k]
                    cache_dict[key] = v
                cache_dict.update(kwargs)
            get_dict()

            def get_value():
                for key in params:
                    if key not in cache_dict.keys():
                        cache_dict[key] = sig[key].default

                keys = tuple(sorted(cache_dict.items()))
                keys_hash = hash(keys)
                if keys_hash not in res_cache.keys():
                    fn_res = fn(*args, **kwargs)
                    res_cache[keys_hash] = fn_res, datetime.datetime.now().timestamp()
                # print(res_cache)
                return res_cache[keys_hash][0]

            res = get_value()
            return res

        return wrapper
    return mycache


def timesl(fn):
    def wrapper(*args, **kwargs):
        st = datetime.datetime.now().timestamp()
        res = fn(*args, **kwargs)
        print('it cost {} seconds'.format(datetime.datetime.now().timestamp()-st))
        return res
    return wrapper

@timesl
@cachetime(10)

def test(x,y):
    time.sleep(5)
    return x+y

print(test(3,4))
time.sleep(2)  # 模仿延时操作
print(test(x=3,y=4))
time.sleep(3)
print(test(3,y=4))
time.sleep(4)  # 此时已经有了九秒了
print(test(3,y=4))


# 运行结果如下
# it cost 5.003422021865845 seconds
# 7
# it cost 7.581710815429688e-05 seconds
# 7
# it cost 6.198883056640625e-05 seconds
# 7
# it cost 8.606910705566406e-05 seconds
# 7