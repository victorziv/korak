from psycopg2.extensions import AsIs
from .query_base import QueryBase
from config import logger
# ============================================


class QueryTestcase(QueryBase):

    def read_one_by_field(self, **kwargs):

        if len(kwargs) != 1:
            raise RuntimeError("Accepts exactly one parameter for a field name")

        field = next(kwargs.__iter__())
        query = """
            SELECT
                id as caseid,
                name,
                description,
                author,
                owner,
                category,
                created
            FROM testcase
            WHERE %s = %s
        """

        params = (AsIs(field), kwargs[field])

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch
    # ____________________________

    def read(self, **kwargs):

        sort_field = kwargs.get('sort_field', 'created')
        sort_order = kwargs.get('sort_order', 'asc')
        limit = kwargs.get('limit', None)
        offset = kwargs.get('offset', 0)

        query = """
            SELECT
                id AS caseid,
                name,
                description,
                author,
                owner,
                category,
                TO_CHAR(created, 'yyyy-mm-dd') AS created
            FROM testcase
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

    def read_checksum(self, case_name):

        query = """
            SELECT checksum
            FROM testcase
            WHERE name=%s
        """
        params = (case_name,)

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        logger.debug("Fetch: {}".format(type(fetch)))
        return fetch['checksum']
    # ____________________________

    def read_total(self, **kwargs):
        query = """
            SELECT COUNT(*) AS total FROM testcase
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch['total']
    # ____________________________

    def update(self, key_name, key_value, args):
        set_str = ','.join(["%s=%s" % (k, '%s') for k in args.keys()])
        sql_template = "UPDATE testcase SET {} WHERE {} = %s"
        query = sql_template.format(set_str, key_name)
        params = list(args.values())
        params.append(key_value)
        logger.info("Params: %r", params)

        logger.info("Query: {}".format(self.db.cursor.mogrify(query, params)))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
