import pytest
from webapp import create_app
from dba import DBAdmin
# _____________________________


@pytest.fixture(scope='session')
def db():
    app = create_app('testing')
    DBAdmin.resetdb(app.config)
    DBAdmin.create_table_changelog(app.config)
    DBAdmin.upgradedb(app.config, None)
    DBAdmin.insert_initial_data(app)
    return app.db
