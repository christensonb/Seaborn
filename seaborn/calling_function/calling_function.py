"""
    This module is used to get the calling class, function, file, line_number, and locals

    Issues:
        builtin functions like eval, break this
        pycharm will also break this, although it sometimes can recover
"""

import inspect
import os
import sys
from collections import OrderedDict
import traceback
from seaborn import *


def function_arguments(func):
    """
    :param func: callable object
    :return: list of str of the arguments for the function
    """
    if getattr(inspect, 'signature', None) is None:
        return list(inspect.getargspec(func).args)
    else:
        return list(inspect.signature(func).parameters.keys())


def function_defaults(func):
    """
    :param func: callable object
    :return:     list of obj of default parameters
    """
    if getattr(inspect, 'signature',None) is None:
        return inspect.getargspec(func)[-1] or []
    else:
        return [v.default for k,v in inspect.signature(func).parameters.items() if v.default is not inspect._empty]


def function_doc(function_index=1, function_name=None):
    """
        This will return the doc of the calling function
    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name: str of what function to look for (should not be used with function_index
    :return: str of the doc from the target function
    """
    frm = func_frame(function_index + 1, function_name)
    try:
        func = getattr(frm.f_locals['self'], frm.f_code.co_name)
    except:
        func = frm.f_globals[frm.f_code.co_name]
    return func.__doc__


def function_path(func):
    """
    This will return the path to the calling function
    :param func:
    :return:
    """
    if getattr(func, 'func_code', None):
        return func.func_code.co_filename.replace('\\', '/')
    else:
        return func.__code__.co_filename.replace('\\', '/')


def file_code(function_index=1, function_name=None):
    """
    This will return the code of the calling function
    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name: str of what function to look for (should not be used with function_index
    :return: str of the code from the target function
    """
    info = function_info(function_index + 1, function_name)
    with open(info['file'], 'r') as fn:
        return fn.read()


def relevant_kwargs(function, exclude_keys='self', exclude_values=None, extra_values=None):
    """
    This will return a dictionary of local variables that are parameters to the function provided in the arg
        this is to be used like
        function(**relevant_kwargs(function))
    :param function:       function to select parameters for
    :param exclude_keys:   str,list,func if not a function it will be turned into one, defaults to excluding None
    :param exclude_values: obj,list,func if not a function it will be turned into one, defaults to excluding 'self'
    :param extra_values:   dict of other values to include with local
    :return:               dict of local variables for the function
    """
    args = function_args(function)
    locals_values = function_kwargs(function_index=2, exclude_keys=exclude_keys)
    if extra_values:
        locals_values.update(extra_values)
    return {k: v for k, v in locals_values if k in args}


def function_args(function):
    try:
        return function.__code__.co_varnames
    except:
        return function.f_code.co_varnames


def function_kwargs(function_index=1, function_name=None, exclude_keys='self', exclude_values=None):
    """
    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name:  str of the function name (should not be used with function_index)
    :param exclude_keys:   str,list,func if not a function it will be turned into one, defaults to excluding None
    :param exclude_values: obj,list,func if not a function it will be turned into one, defaults to excluding 'self'
    :return:               dict of arguments passed into the function making this call
    """
    if not hasattr(exclude_values, '__call__'):
        _exclude_values = isinstance(exclude_values, list) and exclude_values or [exclude_values]
        exclude_values = lambda x: x in _exclude_values

    if not hasattr(exclude_keys, '__call__'):
        _exclude_keys = isinstance(exclude_keys, list) and exclude_keys or [exclude_keys]
        exclude_keys = lambda x: x in _exclude_keys

    frm = func_frame(function_index + 1, function_name)
    args = frm.f_code.co_varnames[:frm.f_code.co_argcount]
    ret = dict([(k, frm.f_locals[k]) for k in args if not exclude_keys(k) and not exclude_values(frm.f_locals[k])])
    return ret


def function_code(function_index=1, function_name=None):
    """
    This will return the code of the calling function
    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name: str of what function to look for (should not be used with function_index)
    :return: str of the code from the target function
    """
    frm = function_info(function_index + 1, function_name)
    raise NotImplemented


def function_info(function_index=1, function_name=None, line_number=None):
    """
    This will return the class_name and function_name of the
    function traced back two functions.

    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name: str of what function to look for (should not be used with function_index)
    :param line_number: int, some times the user may want to override this for testing purposes
    :return tuple: ('cls_name','func_name',line_number,globals())
    """
    frm = func_frame(function_index + 1, function_name)

    file_ = os.path.abspath(frm.f_code.co_filename)
    class_name = frm.f_locals.get('self', None)
    if class_name is not None: # and not skip_class:
        class_name = str(type(class_name)).split('.',1)[-1].split("'")[0]
        # try:
        #     class_name = str(class_name).split(None, 1)[1].split('.')[-1].replace(')', '')
        # except:
        #     class_name = repr(class_name).split()[0].split('.')[-1]
        # if 'object at' in str(class_name):
        #     class_name = str(class_name).split(' object at')[0].split('.')[-1]

    args, _, _, kwargs = inspect.getargvalues(frm)
    line_number = line_number or frm.f_lineno
    return {'class_name': class_name or '',
            'function_name': frm.f_code.co_name,
            'file': file_,
            'path': os.path.split(file_)[0],
            'basename': os.path.basename(file_).split('.')[0],
            'line_number': line_number or frm.f_lineno,
            'globals': frm.f_globals,
            'locals': frm.f_locals,
            'arguments': args,
            'kwargs': kwargs,
            'frame': frm}


def function_history():
    """
    This will return a list of all function calls going back to the beginning
    :return: list of str of function name
    """
    ret = []
    frm = inspect.currentframe()
    for i in xrange(100):
        try:
            if frm.f_code.co_name != 'run_code':  # this is pycharm debugger inserting middleware
                ret.append(frm.f_code.co_name)
            frm = frm.f_back
        except Exception as e:
            break
    return ret


def func_frame(function_index, function_name):
    """
    This will return the class_name and function_name of the
    function traced back two functions.

    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name: str of what function to look for (should not be used with function_index
    :return frame: this will return the frame of the calling function  """
    frm = inspect.currentframe()
    if function_name is not None:
        function_name = function_name.split('*')[0]  # todo replace this with regex
        for i in xrange(1000):
            if frm.f_code.co_name.startswith(function_name):
                break
            frm = frm.f_back
    else:
        for i in range(function_index):
            frm = frm.f_back
    try:  # this is pycharm debugger inserting middleware
        if frm.f_code.co_name == 'run_code':
            frm = frm.f_back
    except:
        pass
    return frm


def function_linenumber(function_index=1, function_name=None, width=5):
    """
    :param width:
    :param function_index: int of how many frames back the program should look (2 will give the parent of the caller)
    :param function_name:  str of what function to look for (should not be used with function_index
    :return                str of the current linenumber
    """
    frm = func_frame(function_index + 1, function_name)
    if width is None:
        return frm._f_lineno
    return str(frm.f_lineno).ljust(width)

def function_name(function_index=1):
    ret = function_info(function_index=function_index + 1)
    return ret['class_name'], ret['function_name']


def path(function_index=1, function_name=None, deliminator='__'):
    ret = function_info(function_index=function_index + 1, function_name=function_name)
    file_ = os.path.basename(ret['file']).split('.')[0]

    if ret['class_name']:
        return '%s%s%s%s%s' % (file_, deliminator, ret['class_name'], deliminator, ret['function_name'])
    else:
        return '%s%s%s' % (file_, deliminator, ret['function_name'])


def current_folder(function_index=1, function_name=None, deliminator='__'):
    info = function_info(function_index + 1, function_name)
    return os.path.split(info['file'])[0]


def trace_error(function_index=2):
    """
    This will return the line number and line text of the last error
    :param function_index: int to tell what frame to look from
    :return: int, str of the line number and line text
    """
    info = function_info(function_index)
    traces = traceback.format_stack(limit=10)
    for trace in traces:
        file_, line_number, line_text = trace.split(',', 2)
        if file_ == '  File "%s"' % info['file'] and line_number != 'line %s' % info['line_number']:
            return line_number.split()[-1], line_text.strip()
    return None, None


def smoke_test():
    # from seaborn.test.assert_answer import assert_answer
    class TestClass(object):
        def __init__(self, c, d=1):
            self.path = path(d)
            self.args = function_info(d)

        @staticmethod
        def static_test(a, index=1):
            return function_info(function_index=index) # BJC was function but I didn't understand that

    def test_func_path(a, index=1):
        return path(index)

    def test_func_info(a, index=1, function_name=None):
        return function_info(function_name=function_name, function_index=index, line_number='skip for testing')

    def test_func_embed(func, **kwargs):
        return func(**kwargs)

    results = OrderedDict([('class_path', TestClass(c='c').path),
                           ('class_info', TestClass(c='c').args),
                           ('function_path', test_func_path("a")),
                           ('test_info', test_func_info(a="a")),
                           ('embed_func_info', test_func_embed(test_func_info, a="a", index=2)),
                           ('embed_func_path', test_func_embed(test_func_path, a="a", index=2)),
                           ('embed_class_path', test_func_embed(TestClass, c="c", d=2).path),
                           ('embed_class_info', test_func_embed(TestClass, c="c", d=2).args),
                           ('static_args', TestClass.static_test("a")),
                           ('embed_static_args', test_func_embed(TestClass.static_test, a="a", index=2))])


if __name__ == '__main__':
    smoke_test()
