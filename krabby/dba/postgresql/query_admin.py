import sys
import os
import datetime
import glob
import importlib
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs
from flask import current_app
# ========================================


class DBAdmin(object):

    def __init__(self, conn=None, conf=None):
        self.conn = conn
        self.conf = conf
    # __________________________________________

    def createdb(self, newdb, newdb_owner=None):
        """
        Creates a new DB.

        To successfully create a new DB
        2 pre-requisites should be fullfilled.

        * A connection to a default DB should be established
        * The connected user should have at least CREATEDB authorization

        Parameters
        ----------

        conn : DB connection object
            Pre-constructed connection.
            I.e. conn object is already connected to a "default" DB
            existing on the DB engine.

        newdb : str
            The new DB name.

        newdb_owner : str
            (Optional). The owner of the newly created DB.
            The required user has to exist on the DB engine.

        Returns
        -------
        None

        """
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            query = """CREATE DATABASE %(dbname)s WITH OWNER %(user)s"""
            params = {'dbname': AsIs(newdb), 'user': AsIs(newdb_owner)}
            self.cursor.execute(query, params)
        except psycopg2.ProgrammingError as pe:
            if 'already exists' in repr(pe):
                pass
            else:
                raise
    # ___________________________________________

    def dropdb(self, dbtodrop):
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        query = """DROP DATABASE IF EXISTS %(dbname)s"""
        params = {'dbname': AsIs(dbtodrop)}
        self.cursor.execute(query, params)
    # ___________________________

    @staticmethod
    def connectdb(dburi):
        try:
            conn = psycopg2.connect(dburi)
            print("Connected: {}".format(conn))
            cursor = conn.cursor(cursor_factory=DictCursor)
            print("Connected: {} {}".format(conn, cursor))
            return conn, cursor

        except psycopg2.OperationalError as e:
            print("ERROR!: {}".format(e))
            if 'does not exist' in str(e):
                return
            else:
                raise
    # ___________________________

    def already_applied(self, name):

        print("Checking if already applied check name: {}".format(name))

        query = """
            SELECT EXISTS(
                SELECT 1 FROM changelog WHERE name = %s
            )

        """
        params = (name,)

        self.cursor.execute(query, params)
        fetch = self.cursor.fetchone()
        print("Exists fetch: {}".format(fetch))
        return fetch[0]

    # ___________________________

    def apply_versions(self, versions):
        for ver in versions:
            if self.already_applied(ver['name']):
                continue

            try:
                module_name = ver['module']
                mod = importlib.import_module('migrations.versions.%s' % module_name)
                mod.upgrade(self.conn)
            except Exception as e:
                print('ERROR: {}'.format(e))
                self.conn.rollback()
            else:
                version = ver['version']
                name = ver['name']
                recordid = self.insert_changelog_record(version, name)
                print("Changelog record ID for version {}: {}".format(recordid, ver))

    # _____________________________

    def db_upgrade(self, upto_version):
        print("Up to version: {}".format(upto_version))
        versions = self.get_upgrade_versions(upto_version)

        self.apply_versions(versions)
    # _____________________________

    def create_table_roles(self):
        query = """
            CREATE TABLE IF NOT EXISTS roles (
                id serial PRIMARY KEY,
                name VARCHAR(64) UNIQUE,
                isdefault BOOLEAN DEFAULT FALSE,
                permissions INTEGER
            );
        """
        params = {}

        self.cursor.execute(query, params)
        self.conn.commit()
    # _____________________________

    def create_table_changelog(self):

        query = """
           CREATE TABLE IF NOT EXISTS changelog (
               id serial PRIMARY KEY,
               version VARCHAR(4),
               name VARCHAR(100) UNIQUE,
               applied TIMESTAMP
           );
        """
        params = {}

        self.cursor.execute(query, params)
        self.conn.commit()
    # _____________________________

    def create_table_installationstep(self):
        """
        class models.InstallationStep
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True)
        display_name = db.Column(db.String(64), unique=True)
        priority = INTEGER
        """

        table = 'installationstep'

        query = """
            CREATE TABLE IF NOT EXISTS %(table)s (
                id serial PRIMARY KEY,
                name VARCHAR(32) UNIQUE,
                display_name VARCHAR(64),
                priority INTEGER
            );
        """
        params = {'table': AsIs(table)}

        self.cursor.execute(query, params)
        self.conn.commit()

        # Create an index on priority column
        query = """ CREATE INDEX priority_ind ON %(table)s (priority); """
        params = {'table': AsIs(table)}

        self.cursor.execute(query, params)
        self.conn.commit()
    # _____________________________

    def create_table_users(self):

        query = """
            CREATE TABLE IF NOT EXISTS users (
                id serial PRIMARY KEY,
                social_id VARCHAR(64) UNIQUE,
                username VARCHAR(128),
                email VARCHAR(64) UNIQUE,
                password_hash VARCHAR(128),
                role_id INTEGER REFERENCES roles(id),
                location VARCHAR(64),
                about_me TEXT,
                member_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                avatar_hash VARCHAR(32)
            );
        """
        params = {}

        self.cursor.execute(query, params)
        self.conn.commit()
    # _____________________________

    def grant_access_to_table(self, table):
        query = """GRANT ALL ON TABLE %(table)s TO %(user)s"""
        params = {'table': AsIs(table), 'user': AsIs('ivt')}

        self.cursor.execute(query, params)
        self.conn.commit()

    # ___________________________

    def drop_table(self, table):
        print("DB: %r" % self.__dict__)
        print("Table to drop: %r" % table)

        self.cursor.execute("""
            DROP TABLE IF EXISTS %s CASCADE
        """ % table)

        self.conn.commit()

    # _____________________________

    def create_tables(self):
        tables = current_app.config['DB_TABLES_BASELINE']
        for table in tables:
            self.drop_table(table)
            getattr(self, "create_table_%s" % table)()
            self.grant_access_to_table(table)
    # ____________________________

    def drop_all(self):
        for table in self.all_tables:
            self.drop_table(table)
    # _____________________________

    def init_app(self, app):
        self.conn, self.cursor = DBAdmin.connectdb(app.config['DB_CONN_URI'])
        app.db = self
        app.db.conn = self.conn
        app.db.cursor = self.cursor
        return app
    # _____________________________

    def db_downgrade(db):
        migrationdir = './migrations'
        migration_file = '0001.create_table-installationstep.sql'
        f = open(os.path.join(migrationdir, migration_file))
        try:
            db.cursor.execute(f.read())
            db.conn.commit()
        except Exception:
            db.conn.rollback()
            return
        finally:
            f.close()
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
            print('ERROR: %s' % e)
            self.conn.rollback()
            return
    # ____________________________

    def get_upgrade_versions(self, upto_version):
        # --------------------------
        def _compose_version(vfile):
            module = os.path.splitext(os.path.basename(vfile))[0]
            version, name = module.split('_', 1)
            return dict(name=name, module=module, version=version)
        # --------------------------

        versions_path = os.path.join(self.conf.BASEDIR, 'migrations/versions')
        vfiles = glob.iglob(os.path.join(versions_path, '[0-9]*.py'))
        print("Versions files: {}".format(vfiles))
        versions = sorted(
            [_compose_version(vfile) for vfile in vfiles],
            key=lambda x: int(x['version'])
        )
        print("Versions: {}".format(versions))
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
