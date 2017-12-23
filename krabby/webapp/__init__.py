import os
import codecs
from flask import Flask
from flask_login import LoginManager
from dba import DBAdmin
from config import cnf

login_manager = LoginManager()

db = DBAdmin()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# ____________________________________


def create_app(config_name, logging_name=None):
    dapp = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webapp', 'templates'),
    )

    login_manager.init_app(dapp)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth.login'

    dappconf = cnf[config_name]
    dapp.config.from_object(dappconf)

    dapp._static_folder = os.path.join(dapp.config['BASEDIR'], 'webapp', 'static')
    dapp.static_url_path = os.path.join('/static')

    # Remove default Flask logger handlers
    dapp.logger.handlers = []

    dappconf.init_app(dapp, logging_name)
    db.init_app(dapp)

    from webapp.main import main as main_blueprint
    dapp.register_blueprint(main_blueprint)

    from webapp.auth import auth as auth_blueprint
    dapp.register_blueprint(auth_blueprint, url_prefix='/auth')

    from webapp.api_1_0 import api as api_1_0_blueprint
    dapp.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return dapp
# ____________________________________


def connectdb(conf):
    db = DBAdmin()
    db.initdb(conf)
    return db
# ____________________________________


__version__ = codecs.open(os.path.join(ROOT, 'version.txt'), 'r').read().strip()
