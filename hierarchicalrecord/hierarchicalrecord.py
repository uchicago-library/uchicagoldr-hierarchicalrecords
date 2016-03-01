from json import dumps, load
from re import search


class HierarchicalRecord(object):
    def __init__(self, from_file=None):
        if from_file is not None:
            self.fromJSON(from_file)
        else:
            self.data = {}

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return dumps(self.data, indent=4)

    def __eq__(self, other):
        return isinstance(other, HierarchicalRecord) and \
            self.get_data() == other.get_data()

    def __iter__(self):
        for x in self.get_data():
            yield x

    def __getitem__(self, key):
        if key[-1].isnumeric():
            return self.get_value(key)
        else:
            return self.get_field(key)

    def __setitem__(self, key, value):
        if key[-1].isnumeric():
            self.set_value(key, value)
        else:
            self.set_field(key, value)

    def __delitem__(self, key):
        if key[-1].isnumeric():
            self.remove_value(key)
        else:
            self.remove_field(key)

    def _dotted_to_list(self, dotted_string):
        return dotted_string.split(".")

    def _list_to_dotted(self, in_list):
        for x in in_list:
            if "." in x:
                raise ValueError("'.' is a protected character in " +
                                 "record configuration key names.")
        return ".".join(in_list)

    def _no_leaf_index(self, keyList):
        for x in keyList[:-1]:
            if not x[-1].isnumeric():
                raise ValueError("A portion of your path ({}) lacks an index".format(x))
        if keyList[len(keyList)-1][-1].isnumeric():
            raise ValueError('Operations on fields can not ' +
                             'accept an index at the leaf')

    def _reqs_indices(self, keyList):
        for x in keyList:
            if not x[-1].isnumeric():
                raise ValueError("A portion of your path ({}) lacks an index".format(x))

    def _split_path_strings(self, in_str):
        new_key_index = None
        new_key_index_str = search(r'\d+$', in_str)
        if new_key_index_str:
            new_key_index = new_key_index_str.group()
        if new_key_index:
            new_key_str = in_str.rstrip(new_key_index)
            new_key_index = int(new_key_index)
        else:
            new_key_str = in_str
            new_key_index = None
        return new_key_str, new_key_index

    def _get_value_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._reqs_indices(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            return start[new_key_str][new_key_index]
        else:
            return self._get_value_from_key_list(keyList[1:],
                                                 start=start[new_key_str][new_key_index])

    def _get_field_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            return start[new_key_str]
        else:
            return self._get_field_from_key_list(keyList[1:],
                                                 start=start[new_key_str][new_key_index])

    def _del_value_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._reqs_indices(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            del start[new_key_str][new_key_index]
        else:
            self._del_value_from_key_list(keyList[1:],
                                          start=start[new_key_str][new_key_index])

    def _del_field_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            del start[new_key_str]
        else:
            self._del_field_from_key_list(keyList[1:],
                                          start=start[new_key_str][new_key_index])

    def _set_value_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_data()
        self._reqs_indices(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str][new_key_index] = new_value
        else:
            self._set_value_from_key_list(keyList[1:], new_value,
                                          start=start[new_key_str][new_key_index])

    def _set_field_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str] = new_value
        else:
            self._set_field_from_key_list(keyList[1:], new_value,
                                          start=start[new_key_str][new_key_index])

    def _edit_value_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_data()
        self._reqs_indices(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str][new_key_index] = new_value
        else:
            self._edit_value_from_key_list(keyList[1:], new_value,
                                           start=start[new_key_str][new_key_index])

    def _init_field_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if new_key_str not in start:
            start[new_key_str] = [None]
        if new_key_index:
            while len(start[new_key_str]) < new_key_index+1:
                start[new_key_str].append(None)
        if len(keyList) > 1:
            if start[new_key_str][new_key_index] == None:
                start[new_key_str][new_key_index] = {}
            self._init_field_from_key_list(keyList[1:],
                                           start=start[new_key_str][new_key_index])

    def _add_to_field_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str].append(new_value)
        else:
            self._add_to_field_from_key_list(keyList[1:], new_value,
                                             start=start[new_key_str][new_key_index])

    def _check_if_value_exists(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._reqs_indices(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if new_key_str not in start:
            return False
        if new_key_index > len(start[new_key_str])-1:
            return False
        if len(keyList) == 1:
            return True
        else:
            return self._check_if_value_exists(keyList[1:],
                                               start=start[new_key_str][new_key_index])

    def _check_if_field_exists(self, keyList, start=None):
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if new_key_str not in start:
            return False
        if len(keyList) > 1:
            if new_key_index > len(start[new_key_str])-1:
                return False
        if len(keyList) == 1:
            return True
        else:
            return self._check_if_field_exists(keyList[1:],
                                               start=start[new_key_str][new_key_index])

    def set_data(self, data):
        if not isinstance(data, dict):
            raise ValueError
        self.data = data

    def get_data(self):
        return self.data

    def set_value(self, key, value):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        if not self._check_if_value_exists(key):
            self._init_field_from_key_list(key)
        self._set_value_from_key_list(key, value)

    def get_value(self, key):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        return self._get_value_from_key_list(key)

    def set_field(self, key, value):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        if not self._check_if_field_exists(key):
            self._init_field_from_key_list(key)
        self._set_field_from_key_list(key, value)

    def get_field(self, key):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        return self._get_field_from_key_list(key)

    def add_to_field(self, key, value, create_if_necessary=True):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        if self._check_if_field_exists(key):
            self._add_to_field_from_key_list(key, value)
        else:
            if not create_if_necessary:
                raise ValueError('field does not exist')
            else:
                key[-1] = key[-1]+"0"
                self.set_value(key, value)

    def remove_value(self, key):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        if self._check_if_value_exists(key):
            self._del_value_from_key_list(key)

    def remove_field(self, key):
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        if self._check_if_field_exists(key):
            self._del_field_from_key_list(key)

    def leaves(self, start=None, init_path=None):
        result = []
        if start is None:
            start = self.get_data()
        for x in start:
            for i, y in enumerate(start[x]):
                if init_path is None:
                    path = x + str(i)
                else:
                    path = ".".join([init_path, x + str(i)])
                if not isinstance(y, dict):
                    result.append((path, y))
                else:
                    result = result + self.leaves(start=y, init_path=path)
        return result

    def keys(self, start=None, init_path=None):
        result = []
        if start is None:
            start = self.get_data()
        for x in start:
            for i, y in enumerate(start[x]):
                if init_path is None:
                    path = x + str(i)
                else:
                    path = ".".join([init_path, x + str(i)])
                result.append(path)
                if isinstance(y, dict):
                    result = result + self.keys(start=y, init_path=path)
        return result

    def values(self):
        result = []
        for x in self.keys():
            result.append(self[x])
        return result

    def toJSON(self, **kwargs):
        return dumps(self.data, **kwargs)

    def fromJSON(self, json_file, **kwargs):
        with open(json_file, 'r') as f:
            self.data = load(f, **kwargs)
