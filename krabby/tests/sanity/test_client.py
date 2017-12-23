from flask import url_for
from webapp import create_app
from models import Role


class TestFlaskWebClient:

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        Role.insert_roles()

    def setup(self):
        self.client = self.app.test_client(use_cookies=True)

    @classmethod
    def teardown_class(cls):
        cls.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        assert('momo' in data)
