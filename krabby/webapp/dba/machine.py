from psycopg2.extensions import AsIs
from .base import QueryBase
from config import logger

# ============================================


class QueryMachines(QueryBase):

    def read_one_by_field(self, **kwargs):

        if len(kwargs) != 1:
            raise RuntimeError("Accepts exactly one parameter for a field name")

        field = next(kwargs.__iter__())
        query = """
            SELECT
                id,
                name,
                ticket,
                owner,
                opened_on
            FROM machines
            WHERE %s = %s
        """

        params = (AsIs(field), kwargs[field])

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch
    # ____________________________

    def read(self, **kwargs):

        sort_field = kwargs.get('sort_field', 'opened_on')
        sort_order = kwargs.get('sort_order', 'asc')
        limit = kwargs.get('limit', None)
        offset = kwargs.get('offset', 0)

        query = """
            SELECT
                id AS machineid,
                name,
                model,
                ticket
            FROM machines
            ORDER BY %s %s
            LIMIT %s
            OFFSET %s
        """
        params = (AsIs(sort_field), AsIs(sort_order), AsIs(limit), AsIs(offset))

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        logger.debug("Fetch type: {}".format(type(fetch)))
        return fetch
    # ____________________________

    def read_total(self, **kwargs):
        query = """
            SELECT COUNT(*) AS total FROM machines
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch['total']
    # ____________________________

    def update_customer(self, machineid, customer_name):
        query = """
            UPDATE machines
            SET customerid = (
                SELECT id FROM customers
                WHERE name = %s
            )
            WHERE machineid = %s
        """

        params = (customer_name, machineid)
        print(self.db.cursor.mogrify(query, params))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
