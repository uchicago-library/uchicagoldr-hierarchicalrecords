from re import compile as regex_compile

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord


class RecordValidator(object):

    _conf = None

    def __init__(self, conf):
        self.conf = conf

    def _generalize_key(self, key):
        nums = [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
        ]

        splits = key.split(".")
        generalized_splits = []
        for split in splits:
            stop_dropping = False
            generalized_split = ""
            for i in range(1, len(split)+1):
                char = split[-i]
                if stop_dropping:
                    generalized_split = char + generalized_split
                else:
                    if char not in nums:
                        generalized_split = char + generalized_split
                        stop_dropping = True
            generalized_splits.append(generalized_split)
        return ".".join(generalized_splits)

    def _remove_last_index(self, key):
        splits = key.split(".")
        splits[-1] = self._generalize_key(splits[-1])
        return ".".join(splits)

    def _gather_applicable_values(self, generalized_key, record):
        applicable_values = []
        for x in record.keys():
            if self._generalize_key(x) == generalized_key:
                applicable_values.append(record[x])
        return applicable_values

    def _get_key_from_value(self, record, value):
        for x in record.keys():
            if record[x] == value:
                return x

    def _read_value_type(self, valueTypeStr):
        allowed_types = [
            ('str', str),
            ('dict', dict),
            ('int', int),
            ('bool', bool),
            ('float', float)
        ]
        if valueTypeStr not in [x[0] for x in allowed_types]:
            raise ValueError()
        tup = None
        for x in allowed_types:
            if valueTypeStr == x[0]:
                tup = x
        return tup[1]

    def get_conf(self):
        return self._conf

    def set_conf(self, conf):
        self._conf = conf

    def validate(self, record, strict=True, missing_is_error=True):

        errors = []

        if not isinstance(record, HierarchicalRecord):
            raise ValueError('Not a HierarchicalRecord')

        if strict is True:
            field_names = [x['Field Name'] for x in self.conf.data]
            for key in record.keys():
                if self._generalize_key(key) not in field_names:
                    errors.append("Bad key: {}".format(key))

        for field_data in self.conf.data:

            nested = "." in field_data['Field Name']
            matching_keys = [key for key in record.keys() if self._generalize_key(key) == field_data['Field Name']]

            if field_data['Obligation'] == "r":
                if not nested:
                    if len(matching_keys) < 1:
                        if missing_is_error is True:
                            errors.append("Missing required key: {}".format(field_data['Field Name']))
                else:
                    parent_keys = [key for key in record.keys() if self._generalize_key(key) == ".".join(field_data['Field Name'].split(".")[0:-1])]
                    for key in parent_keys:
                        values = record[key]
                        leaf_key = field_data['Field Name'].split(".")[-1]
                        if leaf_key not in values:
                            if missing_is_error is True:
                                errors.append("Missing required key: {} from {}".format(leaf_key, key))

            applicable_values = self._gather_applicable_values(field_data['Field Name'], record)
            if len(applicable_values) == 0:
                continue

            if field_data['Cardinality'] != "n":
                if not nested:
                    if len(matching_keys) != int(field_data['Cardinality']):
                        errors.append("Key cardinality error: {}".format(field_data['Field Name']))
                else:
                    parent_keys = [key for key in record.keys() if self._generalize_key(key) == ".".join(field_data['Field Name'].split(".")[0:-1])]
                    leaf_key = field_data['Field Name'].split(".")[-1]
                    for key in parent_keys:
                        values = record[key]
                        for value in values:
                            try:
                                if len(values[leaf_key]) != int(field_data['Cardinality']):
                                    errors.append("Key cardinality error: {} in {} ({} != {})".format(leaf_key, key, str(len(values[leaf_key])), str(int(field_data['Cardinality']))))
                            except Exception as e:
                                print(record.keys())
                                print(values)
                                print(leaf_key)
                                raise

            if field_data['Value Type'] != "":
                comp_type = self._read_value_type(field_data['Value Type'])
                for x in matching_keys:
                    if not isinstance(record[x], comp_type):
                        errors.append("{} contains the wrong value type. Type should be {}, is {}".format(x, field_data['Value Type'], str(type(record[x]))))

            if field_data['Children Required'] != "":
                req_children = int(field_data['Children Required'])
                for key in matching_keys:
                    children = 0
                    sub_fields = [x['Field Name'] for x in self.conf.data if
                                    field_data['Field Name']+"." in x['Field Name'] and
                                    "." not in x['Field Name'].lstrip(field_data['Field Name']+".")]
                    suffixes = [x.split(".")[-1] for x in sub_fields]
                    for x in suffixes:
                        try:
                            record[key+"."+x]
                            children += 1
                        except KeyError:
                            pass
                    if children < req_children:
                        errors.append("Fewer than the required number of children in {}. Include at least {} of {}".format(key, str(req_children), " or ".join([key+"."+x for x in suffixes])))

            if field_data['Validation'] != "":
                matcher = regex_compile(field_data['Validation'])
                for key in matching_keys:
                    if not matcher.match(str(record[key])):
                        errors.append("Value for {} does not match its validation".format(key))

        if len(errors) == 0:
            return (True, None)
        else:
            return (False, errors)

    conf = property(get_conf, set_conf)
