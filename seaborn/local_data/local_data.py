""" This module is to store local data that shouldn't be added to a repository like passwords

    It does this by creating a class that will look in a local_data.json file for any attribute requested
    if the data is not there it will prompt the user for the data through standard io.

    Example:
    >>> from seaborn import LocalData
    >>> local_data = LocalData()
    >>> username = local_data['username']
    Please provide the 'username' for the local data:
    >>> 'bchristenson'
    >>> username
    'bchristenson'
"""
__author__ = 'Ben Christenson'
__date__ = "10/7/15"
import json
import os

from seaborn import function_info


class LocalData(object):
    def __init__(self, filename=None, no_question=False):
        """
        :param filename: str of the file name; defaults to local_data.json in the directory of the calling function
        """
        try:
            self._data = {}
            self._filename = ''
            if not filename:
                self._filename = os.path.abspath(os.path.join(
                    os.path.split(function_info(2)['file'])[0], '_local_data.json'))
            elif filename and filename.startswith('..'):
                self._filename = os.path.abspath(os.path.join(
                    os.path.split(function_info(2)['file'])[0], filename))
            else:
                self._filename = filename

            if no_question:
                assert (os.path.exists(self._filename)), 'File does not exist'

            self._data = os.path.exists(self._filename) and json.load(open(self._filename, 'r')) or {}
        except Exception as e:
            if self._filename == '' or no_question or open(self._filename, 'r').read():
                raise Exception('Failed to load local data from json file %s ' \
                         'with error message \n%s'%(self._filename,e.args))
        self._no_question = no_question
        pass

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if not item in self._data:
            assert not self._no_question, "Local data was missing '%s'" % item
            self._data[item] = raw_input("\n\nPlease provide the '%s' for the local data:" % item)
            json.dump(self._data, open(self._filename, 'w'), indent=2)
        return self._data[item]

    def __setattr__(self, item, value):
        if item in ['_filename', '_data', '_no_question']:
            self.__dict__[item] = value
            return
        if value != self._data.get(item, '__NOT_FOUND__'):
            self._data[item] = value
            json.dump(self._data, open(self._filename, 'w'), indent=2)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setitem__(self, item, value):
        return self.__setattr__(item, value)

    def keys(self):
        return self._data.keys()

    def __len__(self):
        return len(self._data)

    def clear(self):
        return self._data.clear()

    def has_key(self, k):
        return k in self.keys()

    def items(self):
        return self._data.items()

    def pop(self, index):
        return self._data.pop(index)

    def values(self):
        return self._data.values()

    def popitem(self, item):
        return self._data.popitem(item)

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)


def smoke_test():
    path = '%s/local_data.json' % os.path.split(__file__)[0]
    if os.path.exists(path):
        os.remove(path)
    local_data = LocalData()
    local_data['username'] = 'hello'
    local_data.password = 'world'
    assert dict(username=local_data.username, password=local_data['password']) == json.load(open(path, 'r'))


if __name__ == '__main__':
    smoke_test()
