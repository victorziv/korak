import sys
import os
import datetime
import glob
import importlib
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs
from config import logger
# ========================================


class DBAdmin(object):

    def __init__(self, conf=None, conn=None):
        self.conn = conn
        self.conf = conf
    # __________________________________________

    def already_applied(self, name):

        query = """
            SELECT EXISTS(
                SELECT 1 FROM changelog WHERE name = %s
            )

        """
        params = (name,)

        self.cursor.execute(query, params)
        fetch = self.cursor.fetchone()
        logger.debug("Already applied: {}".format(fetch[0]))
        return fetch[0]

    # ___________________________

    def apply_versions(self, conf, versions):
        logger.info("==== FOUND VERSIONS: %r", [v['version'] for v in versions])
        applied = []

        for ver in versions:
            if self.already_applied(ver['name']):
                logger.info("Version %s already applied - skipping", ver['version'])
                continue

            try:
                module_name = ver['module']
                mod = importlib.import_module('%s.%s' % (conf['MIGRATIONS_MODULE'], module_name))
                mod.upgrade(self.conn)
            except Exception as e:
                logger.exception("!! APPLY VERSIONS EXCEPTION")
#                 logger.error('ERROR: {}. Aborting apply version {}'.format(e, ver))
                self.conn.rollback()
                raise
            else:
                version = ver['version']
                name = ver['name']
                recordid = self.insert_changelog_record(version, name)
                applied.append(version)
                logger.info("Version %s applied", version)
                logger.debug("Changelog record ID for version {}: {}".format(recordid, ver))

        if not len(applied):
            logger.info("No changes found for the DB")
    # _____________________________

    @staticmethod
    def createdb(conf, newdb=None, newdb_owner=None):
        """
        """
        if newdb is None:
            newdb = conf['DBNAME']

        if newdb_owner is None:
            newdb_owner = conf['PROJECT_USER']

        logger.info("Creating DB {} with owner {}".format(newdb, newdb_owner))

        try:
            admin_conn, admin_cursor = DBAdmin.connectdb(conf['DB_CONN_URI_ADMIN'])
            admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            query = """CREATE DATABASE %(dbname)s WITH OWNER %(user)s"""
            params = {'dbname': AsIs(newdb), 'user': AsIs(newdb_owner)}
            admin_cursor.execute(query, params)
        except psycopg2.ProgrammingError as pe:
            if 'already exists' in repr(pe):
                pass
            else:
                raise
        except Exception:
            raise
        finally:
            admin_cursor.close()
            admin_conn.close()
    # ___________________________________________

    @classmethod
    def create_table_changelog(cls, config):

        logger.debug("DB_CONN_URI: {}".format(config['DB_CONN_URI']))

        try:
            conn, cursor = DBAdmin.connectdb(config['DB_CONN_URI'])

            query = """
               CREATE TABLE IF NOT EXISTS changelog (
                   id serial PRIMARY KEY,
                   version VARCHAR(32),
                   name VARCHAR(100) UNIQUE,
                   applied TIMESTAMP
               );
            """
            params = {}

            cursor.execute(query, params)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    # _____________________________

    @staticmethod
    def connectdb(dburi):
        try:
            conn = psycopg2.connect(dburi)
            cursor = conn.cursor(cursor_factory=DictCursor)
            return conn, cursor

        except psycopg2.OperationalError as e:
            if 'does not exist' in str(e):
                logger.exception("OOPS: {}".format(e))
                return None, None
            else:
                raise
    # ___________________________

    @staticmethod
    def disconnect_all_from_db(cursor, dbname):
        query = """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
            AND datname = %s
        """
        params = (dbname,)
        cursor.execute(query, params)
    # ___________________________________________

    def drop_table_changelog(self):
        query = """
            DROP TABLE IF EXISTS changelog;
        """
        params = {}

        self.cursor.execute(query, params)
        self.conn.commit()
    # _____________________________

    def downgradedb(self, db):
        try:
            self.conn, self.cursor = self.connectdb(self.conf.DB_CONN_URI)
            migration_file = '0001.create_table-installationstep.sql'
            f = open(os.path.join(self.conf.MIGRATIONS_DIR, migration_file))
            self.cursor.execute(f.read())
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            return
        finally:
            f.close()
            self.cursor.close()
            self.conn.close()
    # _____________________________

    @staticmethod
    def dropdb(conf, dbname=None):
        if dbname is None:
            dbname = conf['DBNAME']

        logger.info("Dropping DB: {}".format(dbname))
        try:
            admin_conn, admin_cursor = DBAdmin.connectdb(conf['DB_CONN_URI_ADMIN'])
            admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            DBAdmin.disconnect_all_from_db(admin_cursor, dbname)

            query = """DROP DATABASE IF EXISTS %(dbname)s"""
            params = {'dbname': AsIs(dbname)}
            admin_cursor.execute(query, params)
        finally:
            admin_cursor.close()
            admin_conn.close()
    # ___________________________

    @staticmethod
    def grant_connect_to_db(conf):
        try:
            conn, cursor = DBAdmin.connectdb(conf['DB_CONN_URI_ADMIN'])
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            query = """
                GRANT CONNECT ON DATABASE %s TO %s
            """
            params = (AsIs(conf['DBNAME']), AsIs(conf['PROJECT_USER']))
            cursor.execute(query, params)
        finally:
            cursor.close()
            conn.close()

    # ___________________________________________

    def grant_access_to_table(self, table):
        query = """GRANT ALL ON TABLE %(table)s TO %(user)s"""
        params = {'table': AsIs(table), 'user': AsIs('ivt')}

        self.cursor.execute(query, params)
        self.conn.commit()

    # ___________________________

    def init_app(self, app):
        self.conn, self.cursor = DBAdmin.connectdb(app.config['DB_CONN_URI'])
        logger.debug("Cursor created in init_app: {}".format(type(self.cursor)))
        app.db = self
        return app
    # _____________________________

    def initdb(self, conf):
        self.conn, self.cursor = DBAdmin.connectdb(conf['DB_CONN_URI'])
        logger.debug("Cursor created in initdbj: {}".format(type(self.cursor)))
    # _____________________________

    @classmethod
    def insert_initial_data(cls, app):
        app_context = app.app_context()
        app_context.push()
        from models import Role
        Role.insert_roles()
#         from models import User
#         User.insert_initial_users()
    # __________________________________

    @staticmethod
    def resetdb(conf, dbname=None):
        if dbname is None:
            dbname = conf['DBNAME']

        logger.info("Resetting DB: {}".format(dbname))

        DBAdmin.revoke_connect_from_db(conf)
        DBAdmin.dropdb(conf)
        DBAdmin.createdb(conf)
        DBAdmin.grant_connect_to_db(conf)
    # ___________________________

    @staticmethod
    def revoke_connect_from_db(conf):
        try:
            conn, cursor = DBAdmin.connectdb(conf['DB_CONN_URI_ADMIN'])
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            query = """
                REVOKE CONNECT ON DATABASE %s FROM %s
            """
            params = (AsIs(conf['DBNAME']), AsIs(conf['PROJECT_USER']))
            cursor.execute(query, params)
        except psycopg2.ProgrammingError as e:
            if 'does not exist' in str(e):
                pass
            else:
                raise
        finally:
            cursor.close()
            conn.close()
    # ___________________________________________

    @staticmethod
    def upgradedb(conf, upto_version):
        try:
            dba = DBAdmin()
            dba.conn, dba.cursor = DBAdmin.connectdb(conf['DB_CONN_URI'])
            logger.info("DB upgrade up to version: {}".format(upto_version))
            versions = dba.get_upgrade_versions(conf, upto_version)
            dba.apply_versions(conf, versions)
        except Exception as e:
            logger.error('ERROR: %s; rolling back' % e)
            dba.conn.rollback()
        finally:
            dba.cursor.close()
            dba.conn.close()
    # _____________________________

    def insert_changelog_record(self, version_number, name):

        try:

            query = """
                INSERT INTO changelog
                (version, name, applied)
                VALUES (%s, %s, %s)
                RETURNING id
            """
            params = (version_number, name, datetime.datetime.utcnow())

            self.cursor.execute(query, params)
            self.conn.commit()
            fetch = self.cursor.fetchone()
            return fetch['id']

        except Exception as e:
            logger.exception('ERROR: %s; rolling back' % e)
            self.conn.rollback()
            return
    # ____________________________

    def get_upgrade_versions(self, conf, upto_version):
        # --------------------------
        def _compose_version(vfile):
            module = os.path.splitext(os.path.basename(vfile))[0]
            version, name = module.split('_', 1)
            return dict(name=name, module=module, version=version)
        # --------------------------

        versions_path = os.path.join(conf['BASEDIR'], conf['MIGRATIONS_DIR'])
        logger.debug("Versions path: {}".format(versions_path))
        vfiles = glob.iglob(os.path.join(versions_path, '[0-9]*.py'))
        versions = sorted(
            [_compose_version(vfile) for vfile in vfiles],
            key=lambda x: int(x['version'])
        )
        logger.debug("Versions: {}".format(versions))
        return versions

    # ___________________________

    def prompt(self, question):
        from distutils.util import strtobool

        sys.stdout.write('{} [y/n]: '.format(question))
        val = input()
        try:
            ret = strtobool(val)
        except ValueError:
            sys.stdout.write('Please answer with a y/n\n')
            return self.prompt(question)

        return ret
