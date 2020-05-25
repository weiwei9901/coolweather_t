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


class Property:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        print('init=============')
        print(fget.__qualname__)
        print(fset.__qualname__ if fset else None)
        print(fdel.__qualname__ if fdel else None)
        print(doc)
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc

    def __get__(self, instance, owner):
        """
        ___get___
        :param instance:
        :param owner:
        :return:
        """
        print('___get__')
        print(instance)
        if instance is None:
            print(self)
            return self
        if self.fget is None:
            raise AttributeError('unreadable attribute')
        return self.fget(instance)

    def __set__(self, instance, value):
        print('set___')
        if self.fset is None:
            raise AttributeError('can not set value')
        return self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError('can not delete attribute')
        self.fdel(instance)

    def getter(self, fget):
        """
        getter
        :param fget:
        :return:
        """
        print('getter set')
        print(dir(fget))
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        """
        setter
        :param fset:
        :return:
        """
        print('setter set')
        print(fset.__qualname__)
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


class New:
    name = 'wang'

    def __init__(self):
        self._age = 0

    @Property
    def age(self):
        """
        abe getter
        :return:
        """
        return self._age

    @age.setter
    def age(self, value):
        """
        age setter
        :param value:
        :return:
        """
        self._age = value

    @age.deleter
    def age(self):
        """
        age deletter
        :return:
        """
        print('def')
        del self._age


if __name__ == '__main__':
    n = New()
    # print(n.name
