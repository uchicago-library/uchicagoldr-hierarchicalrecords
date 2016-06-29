from json import dumps, load
from re import search

"""
HierarchicalRecord is a class meant to contain complex nested data structures
with values situated at the leaves of nested fields, all of which can
potentially be repeatable.

The structure of the internal data structure is meant to facilitate easily
testing for existence and cardinality of fields, in order to make testing
records against pre-built specifications easy.

The internal data type is well suited to being addressed in a combination
key style which mixes field names and index, which I refer to as "dotted
key syntax."
Eg: Top_Level0.One_Level_Down0

It is meant to function as similarly to a standard dictionary as possible.
"""

class HierarchicalRecord(object):
    def __init__(self, from_file=None):
        """
        Initializes a new HierarchicalRecord instance. If a JSON file is
        provided it is used to seed the data structure.

        __KWArgs__

        * from_file: the path to a json file to be used to seed the data
        """
        if from_file is not None:
            self.fromJSON(from_file)
        else:
            self.data = {}

    def __repr__(self):
        """return the str of the internal dict"""
        return str(self.data)

    def __str__(self):
        """pretty print the internal dict to json"""
        return dumps(self.data, indent=4)

    def __eq__(self, other):
        """
        Test equality with another object.

        __Args__

        1. other: the object to be compared to the instance
        """
        return isinstance(other, HierarchicalRecord) and \
            self.get_data() == other.get_data()

    def __iter__(self):
        """yield each key in the internal dict"""
        for x in self.get_data():
            yield x

    def __getitem__(self, key):
        """
        returns a value if the final char in the key is a number. Otherwise
        returns a field as a list.

        __Args__

        1. key (str): A dotted syntax key specifying a location in the record
        """
        if key[-1].isnumeric():
            return self.get_value(key)
        else:
            return self.get_field(key)

    def __setitem__(self, key, value):
        """
        sets a value if the final char in the key is a number. Otherwise
        sets a field to a list.

        __Args__

        1. key (str): a dotted syntax key specifying a location in the record
        2. value (any): a value to insert into a value if the final char
        of the key is a number, or a list to insert into a field if it
        is not.
        """
        if key[-1].isnumeric():
            self.set_value(key, value)
        else:
            self.set_field(key, value)

    def __delitem__(self, key):
        """
        deletes a value if the final char in the key is a number. Otherwise
        deletes a whole field list.

        __Args__

        1. key (str): a dotted syntax key specifying a location in the record
        """
        if key[-1].isnumeric():
            self.remove_value(key)
        else:
            self.remove_field(key)

    def _dotted_to_list(self, dotted_string):
        """
        converts dotted strings to lists

        __Args__

        1. dotted_string (str): A string in dotted key syntax
        """
        return dotted_string.split(".")

    def _list_to_dotted(self, in_list):
        """
        merges together lists into dotted key syntax

        __Args__

        1. in_list (list): A list of addresses to be assembled into
        a dotted key syntax string.
        """
        for x in in_list:
            if "." in x:
                raise ValueError("'.' is a protected character in " +
                                 "record configuration key names.")
        return ".".join(in_list)

    def _no_leaf_index(self, keyList):
        """
        Necessitates the last char in a key is not a number. Correlates
        to situations where it only makes sense to reference a whole field.
        If not raise a ValueError

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string
        """
        for x in keyList[:-1]:
            if not x[-1].isnumeric():
                raise ValueError("A portion of your path ({}) lacks an index".format(x))
        if keyList[len(keyList)-1][-1].isnumeric():
            raise ValueError('Operations on fields can not ' +
                             'accept an index at the leaf')

    def _reqs_indices(self, keyList):
        """
        Necessitates the last char in a key is a number. correlates to
        situations where it only makes sense to reference a value in a field.
        If not raise a ValueError

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string
        """
        for x in keyList:
            if not x[-1].isnumeric():
                raise ValueError("A portion of your path ({}) lacks an index".format(x))

    def _split_path_strings(self, in_str):
        """
        Split the components of a dotted key syntax entry into its
        field name componenet and its index component

        __Args__

        1. in_str (str): A string representative of a key segment in dotted
        key syntax
        """
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
        """
        retrieves a value from a data structure at the location specified
        by the key list.

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        retrieves a field from a data structure at the location specified
        by the key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            if not isinstance(start, dict):
                raise KeyError(".".join(keyList))
            return start[new_key_str]
        else:
            return self._get_field_from_key_list(keyList[1:],
                                                 start=start[new_key_str][new_key_index])

    def _del_value_from_key_list(self, keyList, start=None):
        """
        Deletes a value from a data structure at the location specified by the
        key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        Deletes a field from a data structure at the location specified
        by the key list.

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        Sets a value in a data structure at the location specified
        by the key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string
        2. new_value (any): the value to set at the location specified by
        [keyList].

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        Sets a field in a data structure at the location specified
        by the key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string
        2. new_value (list): the value to set at the location specified by
        [keyList].

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
        if not isinstance(new_value, list):
            raise ValueError("Fields can only be initialized to lists")
        if start is None:
            start = self.get_data()
        self._no_leaf_index(keyList)
        new_key_str, new_key_index = self._split_path_strings(keyList[0])
        if len(keyList) == 1:
            start[new_key_str] = new_value
        else:
            self._set_field_from_key_list(keyList[1:], new_value,
                                          start=start[new_key_str][new_key_index])

    def _init_field_from_key_list(self, keyList, start=None):
        """
        inits a field or a value in a data structure at the location
        specified by the key list. Default value is None

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        Appends a value to a field in a data structure at the location
        specified by the key list.

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string
        2. new_value (any): the value to set at the location specified by
        [keyList].

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        checks to see if a value exists in a data structure at the location
        specified by the key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        checks to see if a field exists in a data structure at the location
        specified by the key list

        __Args__

        1. keyList (list): A list of key segments from a split dotted key syntax
        string

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        """
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
        """
        sets the internal dictionary attribute

        __Args__

        1. data (dict): A dictionary to insert as the internal data model
        """
        if not isinstance(data, dict):
            raise ValueError
        self.data = data

    def get_data(self):
        """returns the internal dictionary attribute"""
        return self.data

    def set_value(self, key, value):
        """
        sets a [value] at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        data structure
        2. value (any): the value to be inserted into the data structure
        at the location specified by [key]
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        if not self._check_if_value_exists(key):
            self._init_field_from_key_list(key)
        self._set_value_from_key_list(key, value)

    def get_value(self, key):
        """
        returns a value at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        data structure
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        return self._get_value_from_key_list(key)

    def set_field(self, key, value):
        """
        sets the field at the location specified by [key] to [value]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        data structure
        2. value (list): the value to be inserted into the data structure
        at the location specified by [key]
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        if not isinstance(value, list):
            raise ValueError("Fields can only be initialized to lists")
        if not self._check_if_field_exists(key):
            self._init_field_from_key_list(key)
        self._set_field_from_key_list(key, value)

    def get_field(self, key):
        """
        returns the field at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        return self._get_field_from_key_list(key)

    def add_to_field(self, key, value, create_if_necessary=True):
        """
        adds [value] to the field at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        2. value (any): the value to be inserted into the data structure
        at the location specified by [key]

        __KWArgs__

        * create_if_necessary (bool): a boolean that, if set to False, will cause
        a ValueError to be thrown if the field does not already exist when
        it should be appended to. Default behavior is to init the field
        and set the value as the first value
        """
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
        """
        removes the value at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._reqs_indices(key)
        if self._check_if_value_exists(key):
            self._del_value_from_key_list(key)

    def remove_field(self, key):
        """
        removes the field at the location specified by [key]

        __Args__

        1. key (str or list): a key either in dotted key syntax as a string
        or split into its parts in a list, designating a location in the
        """
        if isinstance(key, str):
            key = self._dotted_to_list(key)
        if not isinstance(key, list):
            raise ValueError()
        self._no_leaf_index(key)
        if self._check_if_field_exists(key):
            self._del_field_from_key_list(key)

    def leaves(self, start=None, init_path=None):
        """
        returns a list of tuples of all the leaf values in the data structure
        in the format (key, value)

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        * init_path (str): the path to the current dictionary being searched
        """
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
        """
        returns a list of all the keys in the tree.

        __KWArgs__

        * start (dict): a reference to the dictionary to start traversing
        following the [keyList]. Defaults to self.data
        * init_path (str): the path to the current dictionary being searched
        """
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
        """
        returns a list of all the values in the tree.
        """
        result = []
        for x in self.keys():
            result.append(self[x])
        return result

    def toJSON(self, **kwargs):
        """
        returns a JSON formatted string representation of the data

        __KWArgs__

        * \*\*kwargs: see json.dumps()
        """
        return dumps(self.data, **kwargs)

    def fromJSON(self, json_file, **kwargs):
        """
        sets the internal dictionary attribute to the contents of a JSON file.

        __KWArgs__

        * \*\*kwargs: see json.load()
        """
        with open(json_file, 'r') as f:
            self.data = load(f, **kwargs)
