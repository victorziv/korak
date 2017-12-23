import pytest
from flask import current_app
from app import create_app


class TestAppcontext:

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
    # ______________________________

    @classmethod
    def teardown_class(cls):
        pass

    # ______________________________

    def test_app_context_with(self):
        with self.app.app_context():
            assert current_app.name == 'app'
            assert current_app.config['POSTGRES_CONNECTION_PARAMS']['dbname'] == 'ivttest'

    # ______________________________
