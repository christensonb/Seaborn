""" This just contains some standard functions to do sorting by """
import sys
from random import random, seed

__author__ = 'Ben Christenson'
__date__ = "8/25/15"


class by_key(object):
    def __init__(self, keys, comp=None):
        self.keys = isinstance(keys, list) and keys or [keys]
        self.comp = comp or (lambda x: x)

    def __call__(self, obj):
        return [self.comp(obj[k]) for k in self.keys]


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


def by_random_order(obj):
    return random()


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
    _list.sort(key=by_key('name', comp=by_shortest_then_by_abc))
    print([repr(l) for l in _list])
    assert _list[0]['name'] == 'a' and _list[2]['name'] == 'cccc' and _list[3]['name'] == 'ddddd'
    print(list(range(10)).sort(key=by_random_order))

    if sys.version_info[0] == 2:
        a = sorted(range(10), key=by_random_order)
    else:
        a = sorted(range(10), key=by_random_order)
    print(a)
    assert a == [3, 9, 6, 1, 4, 5, 2, 0, 8, 7]


if __name__ == '__main__':
    smoke_test()
