import inspect
from psycopg2 import DatabaseError, ProgrammingError
from psycopg2.extensions import AsIs
from config import logger

# ============================================


class QueryRole:
    def __init__(self, db):
        self.db = db
    # ____________________________

    def read_one_by_field(self, **kwargs):
        fname = inspect.currentframe().f_code.co_name

        if len(kwargs) != 1:
            raise RuntimeError(
                "%s accepts exactly one parameter for a field name" % fname)
        field = next(iter(kwargs.keys()))

        query = """
            SELECT
                id,
                name,
                isdefault,
                permissions
            FROM roles
            WHERE %s = %s
        """
        params = (AsIs(field), kwargs[field])

        try:
            self.db.cursor.execute(query, params)

        except ProgrammingError as pe:
            logger.debug('ERROR: {}'.format(pe))
            return
        except DatabaseError as e:
            logger.error('ERROR: %s' % e)
            self.db.conn.rollback()

        fetch = self.db.cursor.fetchone()
        logger.debug("Fetch: {}".format(fetch))
        return fetch
    # ____________________________

    def read(self, **kwargs):
        query = """
            SELECT
                id,
                name,
                isdefault,
                permissions
            FROM roles
        """
        params = []
        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        logger.debug("Fetch: {}".format(fetch))
        ret = [dict(f) for f in fetch]
        logger.debug("Return: {}".format(ret))
        return ret
    # ____________________________

    def create(self, record):
        """
        name = db.Column(db.String(64), unique=True)
        isdefault = db.Column(db.Boolean, default=False, index=True)
        permissions = db.Column(db.Integer)
        """

        query = """
            INSERT INTO roles (name, isdefault, permissions)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        params = (record['name'], record['isdefault'], record['permissions'])

        try:
            logger.debug("Query: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
            fetch = self.db.cursor.fetchone()
            return fetch['id']
        except DatabaseError as e:
            logger.error('ERROR: %s' % e)
            self.db.conn.rollback()
            return
    # ____________________________

    def update(self, record):
        """
        name = db.Column(db.String(64), unique=True)
        isdefault = db.Column(db.Boolean, default=False, index=True)
        permissions = db.Column(db.Integer)
        """

        query = """
            UPDATE  roles
            SET
                isdefault = %s,
                permissions = %s
            WHERE name = %s
        """

        params = (record['isdefault'], record['permissions'], record['name'])

        try:
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
        except DatabaseError as e:
            logger.error('ERROR: %s' % e)
            self.db.conn.rollback()
            return
    # ____________________________
