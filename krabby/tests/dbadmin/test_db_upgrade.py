from webapp import create_app
from dba import DBAdmin


def test_db_upgrade():
    app = create_app('testing')
    DBAdmin.resetdb(app.config)
    DBAdmin.create_table_changelog(app.config)
    DBAdmin.upgradedb(app.config, None)
