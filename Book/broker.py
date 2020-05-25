from collections import defaultdict

route_table = defaultdict(list)


class Broker:
    def sub(self, topic, callback):
        if callback in route_table[topic]:
            return
        route_table[topic].append(callback)

    def pub(self, topic, *a, **k):
        for func in route_table[topic]:
            func(*a, **k)
