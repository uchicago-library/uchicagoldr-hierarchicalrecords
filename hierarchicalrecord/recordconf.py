from csv import DictReader, DictWriter
from json import loads, dumps
from uuid import uuid1


class RecordConf(object):

    _field_names = ["Field Name", "Value Type", "Obligation", "Cardinality",
                    "Validation", "Children Required"]

    def __init__(self):
        self._data = []

    def get_data(self):
        return self._data

    def set_data(self, data):
        for x in data:
            self.add_rule(x)

    def from_csv(self, csv_filepath):
        rows = []
        with open(csv_filepath, 'r') as f:
            reader = DictReader(f)
            rows = [row for row in reader]
        for x in rows:
            self.add_rule(x)

    def to_csv(self, csv_filepath):
        with open(csv_filepath, 'w') as f:
            w = DictWriter(f, fieldnames=self._field_names, extrasaction='ignore')
            w.writeheader()
            for x in self.data:
                w.writerow(x)

    def from_json(self, json_filepath):
        with open(json_filepath, 'r') as f:
            for line in f.readlines():
                self.add_rule(loads(line.rstrip("\n")))

    def to_json(self, json_filepath):
        with open(json_filepath, 'w') as f:
            for x in self.data:
                tmp_dict = {}
                for y in self._field_names:
                    tmp_dict[y] = x[y]
                f.write(dumps(tmp_dict)+"\n")

    def add_rule(self, rule):
        for x in self._field_names:
            if x not in rule:
                raise ValueError("Rule missing a required key ({})".format(x))
        rule_id = uuid1().hex
        rule_dict = {}
        rule_dict['id'] = rule_id
        for x in self._field_names:
            rule_dict[x] = rule[x]
        self.data.append(rule_dict)

    def remove_rule(self, rule_id):
        self.data = [x for x in self.data if x['id'] != rule_id]

    data = property(get_data, set_data)
