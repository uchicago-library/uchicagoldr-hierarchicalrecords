from csv import DictReader

class RecordConf(object):

    _data = None

    def __init__(self):
        pass

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def from_csv(self, csv_filepath):
        rows = []
        with open(csv_filepath, 'r') as f:
            reader = DictReader(f)
            rows = [row for row in reader]
        self.data = rows


    data = property(get_data, set_data)
