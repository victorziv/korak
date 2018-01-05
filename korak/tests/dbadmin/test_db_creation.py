import pytest
from webapp import create_app
# ============================


class TestDBCreate:

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        if cls.app.db.conn is not None:
            cls.app.db.conn.close()

        cls.app.db.createdb(cls.app.config)
    # ______________________________

    @classmethod
    def teardown_class(cls):
        cls.app_context.pop()
        cls.app.db.dropdb(cls.app.config)
    # ______________________________

    def test_reset_app_db(self):
        try:
            self.app.db.dropdb(self.app.config)
            self.app.db.createdb(self.app.config)
        except Exception as e:
            pytest.fail("Unexpected exception: {}".format(e))
