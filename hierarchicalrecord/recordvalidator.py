from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord


class RecordValidator(object):

    _conf = None

    def __init__(conf):
        self.conf = conf

    def get_conf(self):
        return self._conf

    def set_conf(self, conf):
        self._conf = conf

    def validate(self, record):
        if not isinstance(record, HierarchicalRecord):
            return False

    conf = property(get_conf, set_conf)
