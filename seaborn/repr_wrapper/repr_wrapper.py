"""" This contains decorators for making returns nicer to work with in and IDLE or Ipython """
import pprint
from seaborn import *

PPRINT_INDENT = 2
PPRINT_WIDTH = 80
PPRINT_DEPTH = 5
REPR_UNICODE_U = False

PPRINT_FORMAT = {'indent': PPRINT_INDENT,
                 'width': PPRINT_WIDTH,
                 'depth': PPRINT_DEPTH}


def str_name_value(name, value, tab=4, ljust=25):
    """
    This will return a str of name and value with uniform spacing
    :param name:    str of the name
    :param value:   str of the value
    :param tab:     int of the number of spaces before the name
    :param ljust:   int of the name ljust to apply to name
    :return:        str of the formatted string
    """
    rep_name = (name.startswith('_') and name[1:]) or name  # todo test this
    try:
        return ' ' * tab + str(rep_name).ljust(ljust) + str(value).replace('\n', '\n' + ' ' * (ljust + tab))
    except:
        rep_name = "Exception in serializing %s value" % name
        return ' ' * tab + str(rep_name).ljust(ljust) + str(value).replace('\n', '\n' + ' ' * (ljust + tab))


def set_pprint_format(indent=None, width=None, depth=None):
    """
    This will set the constants for the pprint
    :param indent: number of spaces to indent
    :param width: max width of the line
    :param depth: mas depth of the objects
    :return: current settings
    """
    if indent is not None:
        PPRINT_FORMAT['indent'] = indent
    if width is not None:
        PPRINT_FORMAT['width'] = width
    if depth is not None:
        PPRINT_FORMAT['depth'] = depth
    return PPRINT_FORMAT


def _repr(r, digits=None, convert_unicode=False, quotes=True):
    if digits is not None and isinstance(r, float):
        r = str(round(r, digits))
        r += '0' * (digits - len(r.split('.')[-1]))

    if convert_unicode and isinstance(r, unicode):
        r = r.encode('ascii', errors='replace')

    if quotes:
        return repr(r)
    else:
        return str(r)


def repr_return(func):
    """
    This is a decorator to give the return value a pretty print repr
    """

    def repr_return_decorator(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, basestring):
            return ret

        if type(ret) in repr_map:
            return repr_map[type(ret)](ret)

        print('=' * 80 + '\n' + ' FAILED TO GET REPR RETURN for type (' + str(type(ret)) + '\n' + '=' * 80)

        return ret

    return repr_return_decorator


class ReprDict(dict):
    __class__ = {}.__class__

    def __init__(self, original_dict, col_names=None, col_types=None):
        dict.__init__(self, original_dict)
        self._original = original_dict
        self._name = None
        # self._col_names = col_names or self.keys()
        # self._col_types = col_types or []

    def __repr__(self, _repr_running=None):
        return self.repr(self._original)

    @staticmethod
    def repr(data):
        string_io = StringIO()
        pprint.pprint(data, stream=string_io, **PPRINT_FORMAT)
        return string_io.getvalue()

        # def _repr_pretty_(self):
        # return str(self) # todo fill this out
        #
        # def _repr_html_(self):
        # return str(self) # todo fill this out

    def repr_setup(self, name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        self._name = name or self._name
        # self._col_types = col_types or self._col_names
        # for col in col_names or []:
        # self.setdefault(col, None)
        # self._col_names = col_names or self.keys()


class ReprList(list):
    __class__ = [].__class__

    def __init__(self, original_list, col_names=None, col_types=None):
        list.__init__(self, original_list)
        self._original = original_list
        self._name = None
        self._col_names = col_names or len(self._original) and self._original[0] or []
        self._col_types = col_types or []

    def __repr__(self, _repr_running=None):
        return self.repr(self._original)

    @staticmethod
    def repr(data):
        string_io = StringIO()
        pprint.pprint(data, stream=string_io, **PPRINT_FORMAT)
        return string_io.getvalue()

    def repr_setup(self, name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        self._name = name or self._name
        self._col_names = col_names or self._col_names
        self._col_types = col_types or self._col_types
        if self._original:
            self._col_names = self._col_names[:len(self._original[0])]


class ReprListList(list):  # todo make a base class
    __class__ = [].__class__

    def __init__(self, original_list=None, col_names=None, col_types=None, digits=None, width_limit=None,
                 convert_unicode=True):
        list.__init__(self, original_list)
        self._original = original_list or []
        self._name = None
        self._col_names = col_names or len(self._original) and self._original[0] or []
        if original_list:
            self._col_names = self._col_names[:len(original_list[0])]
        self._col_types = col_types or []
        self._digits = digits
        self._width_limit = width_limit
        self._convert_unicode = convert_unicode

    def __repr__(self, _repr_running=None):
        return self.repr(self, self._col_names, self._digits, self._convert_unicode)

    @staticmethod
    def repr(data, col_names, digits, convert_unicode):
        if len(data) == 0: return '[]'

        size = len(col_names)
        rep_data = [[repr(h) for h in col_names]]
        start = col_names is data[0] and 1 or 0
        if len(rep_data) == 0: return rep_data

        for row in data[start:]:
            rep_data.append([_repr(r, digits, convert_unicode) for r in row])

        widths = []
        for col in range(size):
            widths.append(max([len(row[col]) for row in rep_data]))

        ret = [','.join([rep_data[r][c].rjust(widths[c] + 1) for c in range(size)]) for r in range(len(rep_data))]
        if start == 1:
            return '[[' + ' ]\n ['.join(ret) + ' ]]'
        else:
            return '#[' + ret[0] + ' ]\n[[' + ' ],\n ['.join(ret[1:]) + ' ]]'

    def __str__(self):
        return self.str(self, self._col_names, self._digits)

    @staticmethod
    def str(data, col_names, digits, width_limit=None):
        if len(data) == 0: return '[]'
        buffer_ = 4

        size = len(col_names)
        rep_data = [[str(h) for h in col_names]]
        start = col_names == data[0] and 1 or 0
        if len(rep_data) == 0: return rep_data

        for row in data[start:]:
            rep_data.append([_repr(r, digits, True, False) for r in row])

        widths = []
        for col in range(size):
            width = max([len(row[col]) for row in rep_data])
            width = width_limit and min(width_limit, width) or width
            widths.append(width)

        rep_data.insert(1, ['_' * w for w in widths])
        ret = [''.join([rep_data[r][c][:widths[c]].rjust(widths[c] + buffer_) for c in range(size)]) for r in
               range(len(rep_data))]
        return '\n'.join(ret)

    def repr_setup(self, name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        self._name = name or self._name
        self._col_names = col_names or self._col_names
        self._col_types = col_types or self._col_types
        if self._original:
            self._col_names = self._col_names[:len(self._original[0])]

    def list_of_dict(self):
        """
        This will convert the data from a list of list to a list of dictionary
        :return: list of dict
        """
        ret = []
        for row in self:
            ret.append(dict([(self._col_names[i], row[i]) for i in xrange(len(self._col_names))]))
        return ReprListDict(ret, col_names=self._col_names, col_types=self._col_types, width_limit=self._width_limit,
                            digits=self._digits, convert_unicode=self._convert_unicode)

    def append(self, obj):
        """
        If it is a list it will append the obj, if it is a dictionary it will convert it to a list and append
        :param obj: dict or list of the object to append
        :return: None
        """
        if isinstance(obj, dict) and self._col_names:
            obj = [obj.get(col, None) for col in self._col_names]
        assert isinstance(obj, list), "Obj appended to ReprListList needs to be a list or dict"
        self._original.append(obj)

    @staticmethod
    def static():
        """
        This will return the data that should not change over time, for use in regression testing
        :return: dict of the data
        """
        raise NotImplemented
        # ret = []
        # for row in self:
        #     ret.append([static_str(self._col_names[i], row[i]) for i in xrange(len(row))])
        # return self.repr(ret)


class ReprListDict(list):
    __class__ = {}.__class__

    def __init__(self, original_list, name=None, col_names=None, col_types=None, digits=None, width_limit=None,
                 convert_unicode=True):
        list.__init__(self, original_list)
        self._original = original_list
        self._name = name or ''
        self._col_names = col_names or len(self._original) and self._original[0].keys() or []
        self._col_types = col_types or []
        self._width_limit = width_limit
        self._digits = digits
        self._convert_unicode = convert_unicode

    def __repr__(self, _repr_running=None):
        return self.repr(self._original)

    def repr(self, data):
        string_io = StringIO()
        pprint.pprint(data, stream=string_io, **PPRINT_FORMAT)
        ret = string_io.getvalue()
        if self._convert_unicode:
            ret = ret.replace("u'", "'")
        return ret

    def list_of_list(self):
        """
        This will convert the data from a list of dict to a list of list
        :return: list of dict
        """
        ret = [[row.get(key, '') for key in self._col_names] for row in self]
        return ReprListList(ret, col_names=self._col_names, col_types=self._col_types, width_limit=self._width_limit,
                            digits=self._digits, convert_unicode=self._convert_unicode)

    def append(self, obj):
        if isinstance(obj, list) and self._col_names:
            obj = dict([(self._col_names[i], obj[i]) for i in range(len(obj))])
        assert isinstance(obj, dict), "Obj appended to ReprListList needs to be a list or dict"
        self._original.append(obj)

    def repr_setup(self, name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        self._name = name or self._name
        # self._col_types = col_types or self._col_types
        # if self._col_names != col_names:
        # for row in self:
        # for col in self._col_names:
        # row.setdefault(col,None)
        # self._col_names = col_names or self._col_names


class ReprTuple(str):
    __class__ = ().__class__

    def __init__(self, original_tuple):
        tuple.__init__(self, original_tuple)
        self._original = original_tuple
        self._name = ''
        self._col_types = []

    def __repr__(self, repr_running=None):
        return self.repr(self._original)

    def repr(self, data):
        string_io = StringIO()
        pprint.pprint(self._original, stream=string_io, **PPRINT_FORMAT)
        return string_io.getvalue()

    def repr_setup(self, name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        self._name = name or self._name
        self._col_types = col_types or self._col_types


class ReprStr(str):
    __class__ = ''.__class__

    def __init__(self, original_str):
        str.__init__(self, original_str)

    def __repr__(self, _repr_running=None):
        return str(self)

    @staticmethod
    def repr_setup(name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        pass


class ReprUnicode(unicode):
    __class__ = u''.__class__

    def __init__(self, original_unicode):
        self = unicode(original_unicode)

    def __repr__(self, _repr_running=None):
        return str(self)

    @staticmethod
    def repr_setup(name=None, col_names=None, col_types=None):
        """
        This wasn't safe to pass into init because of the inheritance
        :param name: name of the api return type (ex. CAMERA_DATA_LIST)
        :param col_names:
        :param col_types:
        :return None:
        """
        pass


repr_map = {type([]): ReprList,
            type({}): ReprDict,
            type(()): ReprTuple,
            # type(u''): ReprUnicode,
            #type(''): ReprStr,
            'list_list': ReprListList,
            'list_dict': ReprListDict,
            }


def rep(obj, _type=None, name=None, col_names=None, col_types=None):
    _type = _type or type(obj)
    try:
        if _type in repr_map:
            ret = repr_map[_type](obj)
            ret.repr_setup(name, col_names, col_types)
            return ret
    except:
        try:
            _type = type(obj)
            if _type in repr_map:
                ret = repr_map[_type](obj)
                ret.repr_setup(name, col_names, col_types)
                return ret
        except:
            pass

    return obj


def smoke_test():
    print(str(ReprListList([['a', 'b', 'c', 'd', 'e', 'f', 'g'], ['a', 1, 0.0, 1.0, 2.12, 3.123, 4.1234]], digits=3)))

    test_str = "[(0, {'a': 'A', 'c': 'C', 'b': 'B'}), \n (1, {'a': 'A', 'c': 'C', 'b': 'B'}), \n (2, {'a': 'A', 'c': 'C', 'b': 'B'})]"
    ans_str = rep(test_str)
    print(repr(ans_str) + '\n')

    test_dict = {'key': [(0, {'a': 'A', 'c': 'C', 'b': 'B'}), (1, {'a': 'A', 'c': 'C', 'b': 'B'}),
                         (2, {'a': 'A', 'c': 'C', 'b': 'B'})]}
    ans_dict = rep(test_dict)
    print(repr(ans_dict) + '\n')

    test_list = [(0, {'a': 'A', 'c': 'C', 'b': 'B'}), (1, {'a': 'A', 'c': 'C', 'b': 'B'}),
                 (2, {'a': 'A', 'c': 'C', 'b': 'B'})]
    ans_list = rep(test_list)
    print(repr(ans_list) + '\n')

    test_unicode = u"[(0, {'a': 'A', 'c': 'C', 'b': 'B'}), \n (1, {'a': 'A', 'c': 'C', 'b': 'B'}), \n (2, {'a': 'A', 'c': 'C', 'b': 'B'})]"
    ans_unicode = rep(test_unicode)
    print(repr(ans_unicode) + '\n')

    test_tuple = (
        (0, {'a': 'A', 'c': 'C', 'b': 'B'}), (1, {'a': 'A', 'c': 'C', 'b': 'B'}), (2, {'a': 'A', 'c': 'C', 'b': 'B'}))
    ans_tuple = rep(test_tuple)
    print(repr(ans_tuple) + '\n')

    test_list_list = [range(i, i + 10) for i in range(10)]
    ans_list_list = rep(test_list_list, _type='list_list')
    print(repr(ans_list_list) + '\n')

    col_names = [l for l in 'abcdefghi'] + ['hello']
    ans_list_list.repr_setup(col_names=col_names)
    print(repr(ans_list_list))


if __name__ == '__main__':
    smoke_test()
