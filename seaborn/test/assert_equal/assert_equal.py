""" This module will perform an assert_equal with the capability to exclude keys and
    it will attempt to report a better difference of the objects
    """
import time
import os
import filecmp
import logging as log
from seaborn.python_2_to_3 import *
from pprint import pprint

import json

FOLDER = ''  # set this to the scratch folder

_index_count = 0


def assert_equal(obj1, obj2, save_if_different=False, msg='', name1='value1', name2='value2', ignore_keys=None,
                 **kwargs):
    """
    This will assert obj1 and obj2 are the same and it will attempt to report the difference.

    NOTE*** If this is different and the objects are complicated then use the save_if_different and use beyond compare
                The files will be saved in the _scratch folder
                Use exclusive_list to add the keys that you don't want to compare
    :param msg:
    :param obj1: obj of comparison 1
    :param obj2: obj of comparison 2
    :param save_if_different: bool if to save to a file the differences
    :param name1: str name of the first object,
    :param name2: str name of the second object,
    :param ignore_keys: list of parameters to exclude from the comparison
    :param kwargs: dict of args for diff obj
    :return: None
    """
    global _index_count
    diff = diff_obj(obj1, obj2, ignore_keys=ignore_keys, **kwargs)
    if diff:
        report = '\n\n'.join(
            ['obj%s\n    %s = %s\n    %s = %s' % (key, name1, repr(value1), name2, repr(value2))
             for key, value1, value2 in diff])
        if save_if_different:
            try:
                assert os.path.exists(FOLDER), 'Scratch Folder %s does not exist' % FOLDER
                with open('%s/%s-%s.json' % (FOLDER, _index_count, name1), 'w') as fn:
                    pprint(obj1, stream=fn, indent=2, depth=10, width=80)
                with open('%s/%s-%s.json' % (FOLDER, _index_count, name2), 'w') as fn:
                    pprint(obj2, stream=fn, indent=2, depth=10, width=80)
                _index_count += 1
            except Exception as e:
                log.error('assert_equal exception in save different %s' % e)
        if msg:
            msg += '\n'
        raise Exception(msg + 'Data different\n' + report)


def diff_obj(obj1, obj2, format_='[%s]', use_keys=True, compare_private=False, missing='MISSING', ignore_keys=None,
             recursive_dict=True):
    """
    This will return a list of differences in the two objects.
    If the objects have keys then those will be used else dir(obj) will be used
    :param obj1: python object with getattr
    :param obj2: python object with getattr
    :param format_: the variable name will be placed in the format string
    :param use_keys: to attempt to use the keys
    :param compare_private: to compare member variables that start with _
    :param missing: label to use for missing variables
    :param ignore_keys: list of parameters to exclude from the comparison
    :param recursive_dict: bool to recursively search through dictionaries
    :return: [[key,obj1.key,obj2.key]]
    """
    try:
        ret = []
        offset = 0
        is_list = False
        assert (type(obj1) == type(obj2) and
                not isinstance(obj1, unicode) and
                not isinstance(obj2, unicode)), 'object types differ %s != %s' % (type(obj1), type(obj2))

        if isinstance(obj1, (str, int, float)) or isinstance(obj2, (str, int, float)):
            if obj1 != obj2:
                ret.append(['', obj1, obj2])
            return ret

        if isinstance(obj1, (list, tuple)) and isinstance(obj2, (list, tuple)):
            params = range(max(len(obj1), len(obj2)))
            is_list = True
        elif use_keys and getattr(obj1, 'keys', None) and getattr(obj2, 'keys', None):
            params = list(set(obj1.keys() + obj2.keys()))
        else:
            params = list(set(dir(obj1) + dir(obj2)))
        ignore_keys = ignore_keys or []

        for param in params:
            if param not in ignore_keys and (compare_private or not str(param).startswith('_')):
                if is_list:
                    value1 = param < len(obj1) and obj1[param] or missing
                    value2 = param + offset < len(obj2) and obj2[param + offset] or missing
                else:
                    try:
                        value1 = getattr(obj1, param, obj1.get(param, missing))
                        value2 = getattr(obj2, param, obj2.get(param, missing))
                    except:
                        value1 = obj1[param]
                        value2 = obj2[param]

                if value1 != value2:
                    if is_list and len(obj1) != len(obj2) and value1 != missing and value2 != missing:
                        if len(obj1) > len(obj2) and value2 == obj1[param + 1]:
                            offset -= 1
                            value2 = missing
                        if len(obj2) > len(obj1) and value1 == obj2[param + 1]:
                            offset += 1
                            value1 = missing

                    if value1 == missing or value2 == missing:
                        ret.append([format_ % str(param), value1, value2])
                    elif recursive_dict and getattr(value1, 'keys', None) and getattr(value2, 'keys', None):
                        ret += diff_obj(value1, value2, format_=format_ % param + "['%s']", missing=missing,
                                        ignore_keys=ignore_keys)
                    elif isinstance(value1, list):
                        ret += diff_obj(value1, value2, format_=format_ % param + "[%s]", missing=missing,
                                        ignore_keys=ignore_keys)
                    elif not isinstance(value1, classmethod):
                        ret.append([format_ % str(param), value1, value2])

        return ret
    except Exception as e:
        log.error("Exception in assert_equal implementation %s" % e, exc_info=True)
        raise e


def assert_equal_call(old_func, new_func, print_answers=True, repeat_on_error=0, time_comparison=None, **kwargs):
    """
    This will call the old func and new function and compare the results
    It can handle similar exception message.
    This will throw and exception if the function act differently
    :param repeat_on_error:
    :param old_func: func of the comparison one
    :param new_func: func of the comparison two
    :param print_answers: bool to print the answers
    :param time_comparison: float of percent slower the new call can be than the old
    :param kwargs: dict of arguments to pass to the functions
    :return: None
    """
    new_ans = None
    new_duration = None
    old_start = time.time()
    _try = None
    try:
        old_ans = old_func(**kwargs)
    except Exception as e:
        old_ans = str(e)
    old_duration = time.time() - old_start

    e = None
    for _try in range(repeat_on_error + 1):
        try:
            new_start = time.time()
            try:
                new_ans = new_func(**kwargs)
            except Exception as e:
                new_ans = str(e)
            new_duration = time.time() - new_start

            if time_comparison is not None and (new_duration - old_duration) / old_duration > time_comparison:
                time_delta_percentage = (new_duration - old_duration) / old_duration
                raise Exception("The new duration is %" + str(time_delta_percentage) + " % slower than before")
            assert_equal(old_ans, new_ans)
            e = None
            break
        except Exception as e:
            pass

    if print_answers:
        log.debug("Kwargs:\n%s\n\nOld:\n%s\n\nNew:\n%s\n\n\n" % (kwargs, old_ans, new_ans) +
                  "Old Duration (seconds):  %s\n" % round(old_duration, 2) +
                  "New Duration (seconds):  %s\n" % round(new_duration, 2) +
                  "Test Attempt:  %s" % _try)

    if e is not None:
        raise e


def assert_file_equal(filename1, filename2):
    """
    This will compare the files and raise and exception if they are not the same
    :param filename1: str of the first file name
    :param filename2: str of the second file
    :return: None
    """
    assert os.path.exists(filename1), 'File1 %s is missing' % filename1
    assert os.path.exists(filename2), 'File2 %s is missing' % filename2
    if filename1.endswith('webm'):
        with open(filename1, 'r') as fn:
            text1 = fn.read()
        with open(filename2, 'r') as fn:
            text2 = fn.read()
        assert text1[400:] == text2[400:], 'Webm files are relatively different'
    elif filename1.endswith('m3u8'):  # this works, but different archivers can split the files differently
        path1 = os.path.split(filename1)[0]
        path2 = os.path.split(filename2)[0]
        with open(filename1, 'r') as fn:
            text1 = fn.read().split('\n')
        with open(filename2, 'r') as fn:
            text2 = fn.read().split('\n')
        assert len(text1) == len(text2), "M3U8 files are different length"
        for i in range(len(text1)):
            if text1[i].endswith('.ts'):
                assert text1[i] == text2[i]
                # This doesn't work see issue 695
                # assert filecmp.cmp(path1+'/'+text1[i], path2+'/'+text2[i]), "TS files %s are different"%filename1
    else:
        assert filecmp.cmp(filename1, filename2, shallow=False), 'Files are different'


def assert_file_end_equivalent(file1, file2, percent=.10, max_megabyte=1, end_buffer_bytes=1000):
    """

    :param file1: str of the first file name, this will start first and end first
    :param file2: str of the second file name, this will start second and end second
    :param percent: float of the last percentage of file to test
    :param max_megabyte: float this is the max number of mega bytes to test
    :param end_buffer_bytes: int of number of bytes at the end to ignore
    """
    if file1.endswith('m3u8'):
        return assert_m3u8_end_equivalent(file1, file2)

    file1_size = os.stat(file1)[6]
    file2_size = os.stat(file2)[6]

    size = file2_size / 1000000
    test_size = min(max_megabyte, size * percent)

    with open(file1, 'r') as fn:
        if test_size < file1_size:
            fn.seek(os.stat(file1)[6] - test_size)
        bytes1 = fn.read()

    with open(file2, 'r') as fn:
        if test_size < file2_size:
            fn.seek(os.stat(file1)[6] - 2 * test_size)
        bytes2 = fn.read()

    assert bytes1[:end_buffer_bytes] in bytes2


def smoke_test():
    obj1 = [range(s) for s in range(10)]
    obj2 = obj1 + []
    obj2.insert(3, 'Hello World')
    log.debug(diff_obj(obj1, obj2))
    log.debug(diff_obj(obj2, obj1))
    pass


if __name__ == "__main__":
    smoke_test()
