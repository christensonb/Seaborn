# this is untested

class DictList(list):
    """
        This object acts as a list and a dict by assuming an int index is for a list
        and any other index is for the dict
    """

    def __init__(self, columns, values):
        """
        :param columns: list of str of the column names
        :param values: list of the values
        :return:
        """
        assert len(columns) <= len(values), 'There are more columns than values'
        assert isinstance(values, list)
        assert isinstance(columns, list)
        self._columns = columns
        list.__init__(self, values[:len(columns)])

    def __getitem__(self, item):
        """
        :param item: if item is an int it will return the column by index else it will look up the value
        :return: obj
        """
        if isinstance(item, int):
            return self._values[item]
        else:
            return self._values[self._columns.index(item)]

    def __setitem__(self, item, value):
        """
        :param item: if item is an int it will perform a list setitem else dictionary
        :return: obj
        """
        if isinstance(item, int):
            list.__setitem__(self, item, value)
        else:
            if item in self._columns:
                list.__setitem__(self, self._columns.index(item), value)
            else:
                self._columns.append(item)
                list.append(self, value)

    def insert(self, index, value, column=''):
        """
        :param index:
        :param column:
        :param value:
        :return:
        """
        list.insert(self, index, value)
        if len(self._columns) < len(self):
            self._columns.insert(index, column)

    def pop(self, index):
        """
        :param index:
        :return:
        """
        if len(self._columns) >= len(self):
            self._columns.pop(index)
        return list.pop(self, index)

    @property
    def columns(self):
        return self._columns
