from flask import current_app as cap
# from psycopg2 import IntegrityError
from psycopg2.extensions import AsIs
from .query_base import QueryBase

# ============================================


class QueryCustomer(QueryBase):
    def __init__(self, db):
        self.db = db
    # ____________________________

    def read_one_by_field(self, **kwargs):

        if len(kwargs) != 1:
            raise RuntimeError("Accepts exactly one parameter for a field name")

        field = next(kwargs.__iter__())
        query = """
            SELECT
                machineid,
                name,
                ticket,
                owner,
                created
            FROM machines
            WHERE %s = %s
        """

        params = (AsIs(field), kwargs[field])

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch
    # ____________________________

    def read(self, **kwargs):
        query = """
            SELECT
                machineid,
                name,
                ticket,
                owner,
                created
            FROM machines
            ORDER BY created DESC
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        return fetch
    # ____________________________

    def read_total(self):
        query = """
            SELECT count(*) FROM machines
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch['count']
    # ____________________________

    def remove_all_records(self):
        print("XXXXXXXX DB: {}".format(self.db.__dict__))
        query = """
            DELETE FROM machines
        """
        params = ()
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________

    def update(self, update_key_name, update_key_value, update_params):
        sql_template = "UPDATE machines SET ({}) = %s WHERE {} = %s"
        query = sql_template.format(', '.join(update_params.keys()), update_key_name)
        params = (tuple(update_params.values()), update_key_value)
        cap.logger.debug(self.db.cursor.mogrify(query, params))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
