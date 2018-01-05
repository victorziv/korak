import pytest
from app import create_app
from app.models import Permission
from app.models import User


class TestUserCreate(object):

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.password = 'gorgona'
        User().clear_table()
    # ______________________________

    @classmethod
    def teardown_class(cls):
        cls.app_context.pop()

    # ______________________________

    def test_user_queries_object(self):
        user = User()
        assert hasattr(user, 'query')
        assert hasattr(user.query, 'db')
        assert hasattr(user.query.db, 'cur')
        assert type(user.query.db.cur).__name__ == 'DictCursor'

    # ______________________________

    def test_password_setter(self):
        u = User().save_user(
            email='test3@nowhere.com',
            username='test3',
            password=self.password)
        u = User().get_by_field(name='username', value='test3')
        print("User test3: %r" % u)
        assert u['password_hash'] is not None

    # ______________________________

    def test_no_password_getter(self):
        username = 'test5'
        User().save_user(
            email='test5@nowhere.com',
            username=username,
            password=self.password
        )
        u = User().get_by_field(name='username', value=username)
        with pytest.raises(KeyError):
            u['password']
    # ______________________________

    def test_password_salts_are_random(self):
        u1 = User().save_user(
            email='test1@nowhere.com',
            username='test1',
            password=self.password
        )

        u2 = User().save_user(
            email='test2@nowhere.com',
            username='test2',
            password=self.password
        )

        assert u1['password_hash'] != u2['password_hash']
    # ______________________________

    def test_roles_and_permissions(self):
        u = User()
        u.save_user(
            email='test4@nowhere.com', username='test4', password='test44')
        assert u.can(Permission.VIEW_REPORT)
        assert not u.can(Permission.ADMINISTER_EXTERNAL)
    # ______________________________
