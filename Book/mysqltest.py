from abc import abstractmethod


class Field:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return '<{}  {}>'.format(self.name, self.type)

    @abstractmethod
    def valid(self):
        raise NotImplementedError()

    @abstractmethod
    def __get__(self, instance, owner):
        pass

    @abstractmethod
    def __set__(self, instance, value):
        pass

    __repr__ = __str__


class InterField(Field):
    def __init__(self, name):
        super().__init__(name, 'int')

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.valid(value)
        instance.__dict__[self.name] = value

    def valid(self, value):
        if not isinstance(value, int):
            raise TypeError('must be int')


class StringField(Field):
    def __init__(self, name):
        super().__init__(name, 'str')

    def valid(self, value):
        if not isinstance(value, str):
            raise TypeError('must be str')

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.valid(value)
        instance.__dict__[self.name] = value


class Mymeta(type):
    def __new__(cls, name, bases, attrs: dict):
        if not attrs.get('__tablename__'):
            attrs['__tablename__'] = name.lower()

        mapping = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                mapping[k] = v

        attrs['__mappings__'] = mapping
        return super().__new__(cls, name, bases, attrs)


class Middle(Mymeta):
    pass


class Model(metaclass=Mymeta):

    def save(self):
        name = []
        value = []
        tablename = type(self).__dict__['__tablename__']
        for k, v in type(self).__dict__.items():
            if isinstance(v, Field):
                name.append(k)
                value.append(self.__dict__[k])
        str_sql = 'insert into {}({}) values ({})'
        a = str_sql.format(tablename, ','.join(name), ','.join(['%s'] * len(value)))
        print(a, value)


class User(Model):
    __tablename__ = 'Myuser'
    id = InterField('id')
    name = StringField('name')

    def __init__(self, id, name):
        self.id = id
        self.name = name


class U2(Model):
    __tablename__ = 'ppp'
    ids = InterField('ids')
    money = InterField('money')
    desc = StringField('desc')

    def __init__(self, ids, m, desc):
        self.ids = ids
        self.money = m
        self.desc = desc


if __name__ == '__main__':
    user = User(12, 'wang')
    us2 = User(2, 'duan')
    # user.save()

    u = U2(7, 50002, 'wang')
    u.save()
    print(u.__mappings__)
    print(u.ids)