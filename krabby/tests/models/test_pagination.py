import pytest  # noqa
from flask import current_app
from app import create_app
from app.models import Role
from app.dbmodels.paginator import Paginator
from app.dbmodels.query_post import QueryPost
# ====================================


class TestPagination:

    @classmethod
    def setup_class(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.app.db.create_tables()
        cls.password = 'mucho'
        Role.insert_roles()
    # ______________________________

    @classmethod
    def teardown_class(cls):
        cls.app_context.pop()

    # ______________________________

    def test_create_paginator(self):
        params = dict(
            query=QueryPost(db=current_app.db),
            page=1,
            per_page=10,
            items={},
            total=100,
        )
        paginator = Paginator(**params)
        assert type(paginator) is Paginator
    # ______________________________
