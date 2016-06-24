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

    def _gather_applicable_values(self, generalized_key, record):
        applicable_values = []
        for x in record.keys():
            if self._generalize_key(x) == generalized_key:
                applicable_values.append(record[x])
        return applicable_values

    def _check_values(self, applicable_values, valueTypeStr):
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
        valueType = tup[1]
        for x in applicable_values:
            if not isinstance(x, valueType):
                return False
        return True

    def get_conf(self):
        return self._conf

    def set_conf(self, conf):
        self._conf = conf

    def validate(self, record, strict=True):
        if not isinstance(record, HierarchicalRecord):
            return False

        if strict is True:
            field_names = [x['Field Name'] for x in self.conf.data]
            for key in record.keys():
                if self._generalize_key(key) not in field_names:
                    return (False, "Bad key: {}".format(key))
        for field_data in self.conf.data:
            applicable_values = self._gather_applicable_values(field_data['Field Name'], record)
            nested = False
            if "." in field_data['Field Name']:
                nested = True
            if field_data['Obligation'] == 'r':
                if nested is False:
                    if len(applicable_values) < 1:
                        return (False, "missing field: {}".format(field_data['Field Name']))
                else:
                    parent_key = ".".join(field_data['Field Name'].split(".")[:-1])
                    leaf_key = field_data['Field Name'].split(".")[-1]
                    for parent in self._gather_applicable_values(parent_key, record):
                        if leaf_key not in parent:
                            return (False, "missing field: {}".format(field_data['Field Name']))
            if len(applicable_values) < 1:
                continue

            if field_data['Children Required'] != "":
                child_count = 0
                for x in applicable_values:
                    if isinstance(x, dict):
                        child_count += 1
                if child_count < int(field_data['Children Required']):
                    return (False, "Missing required child element.")
            if field_data['Cardinality'] != 'n':
                if len(applicable_values) != int(field_data['Cardinality']):
                    return (False, "Incorrect field cardinality")
            if field_data['Value Type'] != "":
                if not self._check_values(applicable_values, field_data['Value Type']):
                    return (False, "Bad value type")
            if field_data['Validation'] != "":
                pattern = regex_compile(field_data['Validation'])
                for value in applicable_values:
                    if not pattern.match(str(value)):
                        return (False, "Invalid field data")
        return (True, None)

    conf = property(get_conf, set_conf)
