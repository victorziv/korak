import os
import sys
import logging
import importlib

logger = None
conf = None
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ==============================================


class Config:
    PROJECT = 'krabby'
    PROJECT_USER = 'krabs'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    LOGPATH = os.path.join(os.path.dirname(BASEDIR), 'logs')

    API_URL_PREFIX = '/api/v1.0'
    SECRET_KEY = os.environ.get('SECRET_KEY') \
        or 'si ca ne vous derange pas'
    ADMIN_USER = os.environ.get('ADMIN_USER') \
        or '%s@infinidat.com' % PROJECT_USER

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_SUBJECT_PREFIX = '[%s]' % PROJECT.capitalize()
    MAIL_SENDER = 'Admin %s' % ADMIN_USER
    TEST_OWNER_DEFAULT = '%s@nowhere.com' % PROJECT_USER

    DBHOST = 'localhost'
    DBPORT = 5432
    DBUSER = PROJECT_USER
    DBPASSWORD = PROJECT_USER

    DB_CONNECTION_PARAMS = dict(
        dbhost=DBHOST,
        dbport=DBPORT,
        dbuser=DBUSER,
        dbpassword=DBPASSWORD
    )

    DB_URI_FORMAT = 'postgresql://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}'
    DBNAME_ADMIN = 'postgres'
    DB_CONN_URI_ADMIN = DB_URI_FORMAT.format(
        dbname=DBNAME_ADMIN,
        **DB_CONNECTION_PARAMS
    )

    AUTH_TOKEN_EXPIRATION = 3600
    OAUTH_CREDENTIALS = {

        "google": {
            "id": "261888576370-pn751o1qrqbcu662nmr3a24nr9cf3eku.apps.googleusercontent.com",
            "secret": "TDwCUl-WzhOjGw6x_P5bYxtH"
        }
    }

    MIGRATIONS_DIR = "migrations"
    MIGRATIONS_MODULE = "migrations"

    NODE_USER = 'root'

    JIRA_USER = 'ivt'
    JIRA_PASS = 'f30QWDKq'
    JIRA_OPTIONS = {
        'server': 'https://jira.infinidat.com',
        'verify': False
    }

    MACHINE_NAME_PREFIX = 'ibox'

# =========================================

    @classmethod
    def init_app(cls, app, logging_name):
        pass
# ===================================


class DevelopmentConfig(Config):
    DEBUG = True
    DBNAME = "%sdev" % Config.PROJECT
    DB_CONN_URI = Config.DB_URI_FORMAT.format(
        dbname=DBNAME,
        **Config.DB_CONNECTION_PARAMS
    )

    # ________________________________

    @classmethod
    def init_app(cls, app, logging_name):
        pass
# ===================================


class TestingConfig(Config):
    SERVER_NAME = 'ivtsrv-staging.telad.il.infinidat.com'
    APPTYPE = 'testing'
    TESTING = True
    SERVER_NAME = 'localhost'
    DBNAME = "%stest" % Config.PROJECT
    DB_CONN_URI = Config.DB_URI_FORMAT.format(
        dbname=DBNAME,
        **Config.DB_CONNECTION_PARAMS
    )

    @classmethod
    def init_app(cls, app, logging_name):
        pass

# ===================================


class ProductionConfig(Config):

    SERVER_NAME = 'ivtsrv.telad.il.infinidat.com'
    DBNAME = Config.PROJECT
    DB_CONN_URI = Config.DB_URI_FORMAT.format(
        dbname=DBNAME,
        **Config.DB_CONNECTION_PARAMS
    )
    # _____________________________

    @classmethod
    def init_app(cls, app):

        # email errors to the administrator
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)

        if getattr(cls, 'MAIL_USE_TLS', None):
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.IVT_MAIL_SENDER,
            toaddrs=[cls.IVT_ADMIN],
            subject='%s Application Error' % cls.IVT_MAIL_SUBJECT_PREFIX,
            credentials=credentials, secure=secure
        )

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

# ===================================


cnf = {
    'develop': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
# ===================================


class ConfiguratorDict(dict):

    def from_cls(self, cls):
        for key in dir(cls):

            if key.startswith('__'):
                continue

            if key.isupper():
                self[key] = getattr(cls, key)
# ===================================


class ColorFileHandler(logging.FileHandler):

#     def emit(self, record):
#         try:
#             if hasattr(record, 'color'):
#                 color = getattr(record, 'color')

#                 if hasattr(record, 'bold') and record.bold:
#                     cmsg = "%s[%s;%sm%s%s\n" % (
#                         Config.CODES['start'],
#                         Config.CODES[color],
#                         Config.CODES['bold'],
#                         record.msg,
#                         Config.CODES['reset']
#                     )
#                 else:
#                     cmsg = "%s[%sm%s%s\n" % (
#                         Config.CODES['start'],
#                         Config.CODES[color],
#                         record.msg,
#                         Config.CODES['reset']
#                     )

#                 record.msg = cmsg

#             logging.FileHandler.emit(self, record)

#         except Exception:
#             self.handleError(record)
    # __________________________________

    def compose_colorized_msg(self, record):

        color = getattr(record, 'color')

        cmsg = '&emsp;<span style="color:{};font-family:"Times, serif;">'.format(color)

        if hasattr(record, 'strong') and record.strong:
            cmsg += '<strong>{}</strong></span><br>\n'.format(record.msg)
        elif hasattr(record, 'italic') and record.italic:
            cmsg += '<em>{}</em></span><br>\n'.format(record.msg)
        elif hasattr(record, 'underline') and record.underline:
            cmsg += '<u>{}</u></span><br>\n'.format(record.msg)
        else:
            cmsg += '{}</span><br>\n'.format(record.msg)

        return cmsg
    # __________________________________

    def emit(self, record):
        try:
            if hasattr(record, 'color'):
                record.msg = self.compose_colorized_msg(record)
            else:
                record.msg = '''
                &emsp;
                <span style="font-family:"Times, serif;">
                {}
                </span>
                <br>\n'''.format(record.msg.strip())

            logging.FileHandler.emit(self, record)

        except Exception:
            self.handleError(record)
# ==============================================


class Configurator:

    @classmethod
    def configure(cls):
        config_name = os.getenv('IVT_CONFIG') or 'default'
        cnfcls = cnf[config_name]
        global conf
        conf = ConfiguratorDict()
        conf.from_cls(cnfcls)
    # _________________________________

    @classmethod
    def create_directory(cls, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno == 17:
                    pass
    # _________________________________

    @classmethod
    def set_logging_level(cls, logging_level):
        for h in cls.logger.handlers:
            h.setLevel(getattr(logging, logging_level.upper()))
    # _________________________________

    @classmethod
    def set_logging(cls, name, loglevel='DEBUG', console_logging=False, console_loglevel='INFO'):

        global logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, loglevel.upper()))
        logger.propogate = False
        logfile = os.path.join(Config.LOGPATH, '%s.log' % name)
        logger.addHandler(cls.log_to_file(name, logfile, loglevel))

        if console_logging:
            logger.addHandler(cls.log_to_console(console_loglevel))
            logger.info("Log path: %s", logfile)
    # ________________________________________

    @classmethod
    def set_task_logging(cls, loggername, taskname, logdir):

        logger = logging.getLogger(loggername)
        logger.setLevel(logging.DEBUG)
        logger.propogate = False

        # DEBUG logging
        logfile = os.path.join(logdir, "%s-debug.log" % taskname)
        logger.addHandler(cls.log_to_file(loggername, logfile, 'DEBUG'))
        logger.pathdebug = logfile

        # INFO logging
        logfile = os.path.join(logdir, "%s-info.log" % taskname)
        info_format = '%(asctime)s %(levelname)-10s %(message)s'
        cls.create_directory(os.path.dirname(logfile))
        info_handler = ColorFileHandler(logfile)

        info_handler.setLevel(getattr(logging, 'INFO'))
        info_handler.setFormatter(logging.Formatter(info_format))
        logger.addHandler(info_handler)
        logger.pathinfo = logfile

        return logger
    # ________________________________________

    @classmethod
    def log_to_console(cls, logging_level, out_to='stderr'):
        logformat = '%(asctime)s - %(levelname)-10s %(message)s'
        handler = logging.StreamHandler(getattr(sys, out_to))
        handler.setLevel(getattr(logging, logging_level.upper()))
        handler.setFormatter(logging.Formatter(logformat))
        return handler
    # ___________________________________________

    @classmethod
    def log_to_file(cls, name, logfile, loglevel, logformat=None):
        if logformat is None:
            logformat = '%(asctime)s %(process)d %(levelname)-10s %(module)s %(funcName)-4s %(message)s'
        cls.create_directory(os.path.dirname(logfile))

        handler = logging.FileHandler(logfile)

        handler.setLevel(getattr(logging, loglevel.upper()))
        handler.setFormatter(logging.Formatter(logformat))

        return handler

# ===============================================


def clean_tasklogger(lg):
    lgr = logging.getLogger("tasksrv")
    lgr.debug("TASKLOGGER CLEANUP: %r" % id(lg))
    for h in lg.handlers[:]:
        lgr.debug("CLEANUP: Task logger handler object: %r" % h)
        h.close()
        lg.removeHandler(h)

    lg = None
# ________________________________________


def set_tasklogger(sessionuid, taskuid, taskname):
    logdir = os.path.join(Config.TASK_LOG_ROOT, sessionuid, taskname, taskuid)
    return Configurator.set_task_logging(loggername=taskuid, taskname=taskname, logdir=logdir)
# ________________________________________


def get_taskconf(taskname):
    try:
        taskconfmod = importlib.import_module('%s.%s.taskconfig' % (Config.TASK_PKG_ROOT, taskname))
        taskconf = getattr(taskconfmod, 'configuration')
        return taskconf
    except ImportError:
        return {}
# ___________________________________________________
