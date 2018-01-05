from config import logger
from models import db, Basemod
# =============================


class Testcasemod(Basemod):

    table = 'testcase'
    # ____________________________

    def add(self, attrs):
        rowid = self.create(table=self.table, attrs=attrs)
        return rowid
    # ____________________________

    @classmethod
    def clear_table(cls):
        status = cls.query.remove_all_records()
        return status
    # ____________________________

    @classmethod
    def get_checksum(cls, name):
        return cls.query.read_checksum(name)
    # ____________________________

    @classmethod
    def get_all(cls, args):
        testcases = cls.query.read(**args)
        logger.debug("Get all return: {}".format(testcases))
        return testcases
    # ____________________________

    @classmethod
    def get_one_by_id(cls, caseid):
        testcases = cls.query.read_one_by_field()
        logger.debug("Get one by ID return: {}".format(testcases))
        return testcases
    # ____________________________

    @classmethod
    def get_total(cls):
        return cls.query.read_total()
    # ____________________________

    @classmethod
    def remove(cls, name):
        attrs = {'name': name}
        rowid = cls.query.delete(table=cls.table, attrs=attrs)
        return rowid
    # ____________________________

    def update(self, case):
        self.query.update(key_name='name', key_value=case['name'], args=case)
