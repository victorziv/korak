import inspect
from flask import current_app as app
from psycopg2 import DatabaseError
from psycopg2.extensions import AsIs

# ============================================


class QueryInstallation(object):
    def __init__(self, db):
        self.db = db
        self.table = 'ibox_installation'
    # ____________________________

    def read_one_by_field(self, **kwargs):
        fname = inspect.currentframe().f_code.co_name

        if len(kwargs) != 1:
            raise RuntimeError("%s accepts exactly one parameter for a field name" % fname)
        field = next(iter(kwargs.keys()))

        query = """
            SELECT id, name
            FROM %(table)s
            WHERE %(field_name)s = %(field_value)s
        """
        params = {
            'table': AsIs(self.table),
            'field_name': AsIs(field),
            'field_value': kwargs[field]
        }

        try:
            self.db.cursor.execute(query, params)

        except DatabaseError as e:
            print('ERROR: %s' % e)
            self.db.conn.rollback()

        fetch = self.db.cursor.fetchone()
        if fetch is None:
            return fetch

        app.logger.debug("Fetch: %r", fetch)
        return fetch
    # ____________________________

    def read(self, **kwargs):
        # TODO: get it from kwargs
        order_by = 'priority'

        query = """
            SELECT name,display_name,priority
            FROM %(table)s
            ORDER BY %(order)s ASC
        """

        params = {
            'table': AsIs(self.table),
            'order': AsIs(order_by)
        }

        self.db.cursor.execute(query, params)

        fetch = self.db.cursor.fetchall()
        if fetch is None:
            return []

        return fetch
    # ____________________________

    def create(self, record):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        query = """
            INSERT INTO %(table)s (
                name,
                display_name,
                priority
            )
            VALUES (%(name)s,%(display_name)s,%(priority)s)
            RETURNING id
        """

        record.update({'table': AsIs(self.table)})

        app.logger.debug("Record: %r", record)
        try:
            self.db.cursor.execute(query, record)
            self.db.conn.commit()
            fetch = self.db.cursor.fetchone()
            return fetch['id']
        except DatabaseError as e:
            app.logger.debug('ERROR: %s', e)
            self.db.conn.rollback()
            return
    # ____________________________
