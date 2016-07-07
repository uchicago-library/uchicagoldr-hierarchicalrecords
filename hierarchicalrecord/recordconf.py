from csv import DictReader, DictWriter
from json import loads, dumps

class RecordConf(object):
    def __init__(self):
        self._data = []

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def from_csv(self, csv_filepath):
        rows = []
        with open(csv_filepath, 'r') as f:
            reader = DictReader(f)
            rows = [row for row in reader]
        for x in rows:
            self.data.append(x)

    def to_csv(self, csv_filepath):
       field_names = ["Field Name", "Value Type", "Obligation", "Cardinality",
                      "Validation", "Children Required"]
       w = DictWriter(csv_filepath, fieldnames=field_names)
       w.writeheader()
       for x in self.data:
           w.writerow(x)

    def from_json(self, json_filepath):
        with open(json_filepath, 'r') as f:
            for line in f.readlines():
                self.data.append(loads(line.rstrip("\n")))

    def to_json(self, json_filepath):
        with open(json_filepath, 'w') as f:
            for x in self.data:
                f.write(dumps(x)+"\n")

    data = property(get_data, set_data)
