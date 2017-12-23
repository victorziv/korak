from flask_script import Manager
import os
CONFIG_KEY = os.getenv('KRABBY_CONFIG') or 'default'

from config import Configurator  # noqa
Configurator.configure()
Configurator.set_logging(name=CONFIG_KEY, console_logging=True)

from config import logger  # noqa

from webapp import create_app  # noqa
app = create_app(CONFIG_KEY)
app_ctx = app.app_context()
app_ctx.push()
manager = Manager(app)
# ___________________________________________


@manager.option(
    '-v', '--version', dest='version', default=None,
    help="""
    Version: if provided upgrade/downgrade up/down to the version.
    Default: None, up to the last version, down - to the previous version.
    """
)
@manager.option(
    '--configkey',
    choices=['develop', 'testing', 'production'],
    default='develop',
    help="Configuration key: testing, develop or production"
)
def dbdowngrade(configkey, version=None):
    """
    Resets / upgrades / downgrades DB (up / down to some version).
    """
    dbapp = create_app(configkey)
    logger.debug("Going to downgrade %s", dbapp.config.__class__)
    dbapp.db.downgradedb(dbapp.config, version)
# ___________________________________________


@manager.option(
    '-v', '--version', dest='version', default=None,
    help="""
    Version: if provided upgrade/downgrade up/down to the version.
    Default: None, up to the last version, down - to the previous version.
    """
)
@manager.option(
    '--configkey',
    choices=['develop', 'testing', 'production'],
    default='develop',
    help="Configuration key: testing, develop or production. Default: develop"
)
def dbupgrade(configkey, version=None):
    """
    Resets / upgrades / downgrades DB (up / down to some version).
    """
    dbapp = create_app(configkey)
    dbapp.db.upgradedb(dbapp.config, version)

# ___________________________________________


@manager.option(
    '--configkey',
    choices=['testing', 'develop', 'production'],
    default='testing',
    help="Configuration key: testing, develop or production. Default: develop"
)
def dbreset(configkey):
    """
    Resets / upgrades / downgrades DB (up / down to some version).
    There is no need in application context - we just want to re-create the DB.
    """
    from config import cnf

    if configkey == 'production':
        logger.error("You cannot reset the production DB - aborting")
        return

    import inspect
    from dba import DBAdmin
    confcls = cnf[configkey]
    conf = {}
    for attr in inspect.getmembers(confcls):
        if attr[0].isupper() and not attr[0].startswith('__'):
            conf[attr[0]] = attr[1]

    dba = DBAdmin()
    dba.resetdb(conf)
    dba.create_table_changelog(conf)
# ___________________________________________


if __name__ == '__main__':
    manager.run()
