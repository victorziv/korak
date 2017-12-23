import pytest  # noqa
from webapp import create_app
from models import Role


class TestRoleModel:

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
    # ______________________________

    @classmethod
    def teardown_class(cls):
        cls.app_context.pop()

    # ______________________________

    def test_role_queries_object(self):
        assert hasattr(Role, 'query')
        assert hasattr(Role.query, 'db')
        assert hasattr(Role.query.db, 'cursor')
        assert type(Role.query.db.cursor).__name__ == 'DictCursor'

    # ______________________________

    def test_insert_roles(self):
        Role.insert_roles()
    # ______________________________

    def test_fetch_role_admin(self):
        admin = Role.get_by_field(name='name', value='admin')
        print("Fetched role: %r" % admin)
        assert admin.name == 'admin'
    # ______________________________

    def test_fetch_role_user(self):
        user = Role.get_by_field(name='name', value='user')
        print("Fetched role: %r" % user)
        assert user.name == 'user'
