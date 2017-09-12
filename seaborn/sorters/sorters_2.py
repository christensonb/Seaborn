""" This just contains some standard functions to do sorting by
"""
__author__ = 'Ben Christenson'
__date__ = "8/25/15"
from random import random, seed

class by_key(object):
    def __init__(self, keys):
        self.keys = isinstance(keys, list) and keys or [keys]

    def __call__(self, obj1, obj2):
        for key in self.keys:
            if obj1[key] > obj2[key]:
                return 1
            if obj1[key] < obj2[key]:
                return -1
        return 0


class by_index(object):
    def __init__(self, indexes):
        self.indexes = isinstance(indexes, list) and indexes or [indexes]

    def __call__(self, obj1, obj2):
        for index in self.indexes:
            if obj1[index] > obj2[index]:
                return 1
            if obj1[index] < obj2[index]:
                return -1
        return 0


class by_attribute(object):
    def __init__(self, keys, comp=None):
        self.keys = isinstance(keys, list) and keys or [keys]
        self.comp = comp or (lambda x: x)

    def __call__(self, obj):
        ret = [self.comp(getattr(obj, k)) for k in self.keys]
        return ret


def sort_dict_by_value(dict_obj):
    """ This will return a list of keys that are sorted by value then keys
    :param dict_obj: dict object to sort
    :return: list of keys
    """

    def by_status(obj):
        return dict_obj[obj]

    return sorted(dict_obj.keys(), by_key=by_status)


def by_longest(obj):
    return -1 * len(obj)


def by_shortest(obj):
    return len(obj)


def by_shortest_then_by_abc(obj):
    return len(obj), obj


def by_longest_then_by_abc(obj):
    return -1 * len(obj), obj


def by_random_order(*args):
    return 1 if random() > .5 else -1


def smoke_test():
    seed(1)

    class test(object):
        def __init__(self, name):
            self.name = name

        def __repr__(self): return self.name

    _list = [test('bbbb'), test('a'), test('cccc'), test('ddddd')]

    _list.sort(key=by_attribute('name', comp=by_shortest_then_by_abc))
    print([repr(l) for l in _list])
    assert _list[0].name == 'a' and _list[2].name == 'cccc' and _list[3].name == 'ddddd'

    _list.sort(key=by_attribute('name', comp=by_longest_then_by_abc), reverse=True)
    print([repr(l) for l in _list])
    assert _list[0].name == 'a' and _list[1].name == 'cccc' and _list[3].name == 'ddddd'

    _list = [dict(name='bbbb'), dict(name='a'), dict(name='cccc'), dict(name='ddddd')]

    a = sorted(range(10),key=by_random_order)
    print(a)
    assert a == [0, 3, 4, 5, 8, 9, 1, 2, 6, 7]

if __name__ == '__main__':
    smoke_test()
