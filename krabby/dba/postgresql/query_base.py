from psycopg2 import IntegrityError
from psycopg2.extensions import AsIs
from config import logger

# ============================================


class QueryBase(object):
    def __init__(self, db):
        self.db = db
    # ____________________________

    def create(self, table, attrs):

        query_template = """
            INSERT INTO %s ({})
            VALUES ({})
            RETURNING id
        """
        fields = ', '.join(attrs.keys())
        logger.info("Fields: {}".format(fields))
        values_placeholders = ', '.join(['%s' for v in attrs.values()])
        query = query_template.format(fields, values_placeholders)
        logger.info("query: {}".format(query))
        logger.info("values: {}".format(attrs.values()))
        values = [AsIs(table)]
        values.extend(attrs.values())
        params = tuple(values)
        logger.info("Params: {}".format(params))

        logger.info("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))

        try:
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
            fetch = self.db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            return fetch['id']
        except IntegrityError:
            self.db.conn.rollback()
        except Exception:
            raise
    # ____________________________

    def read_total(self, table):
        query = """
            SELECT count(*) FROM %(table)s
        """
        params = {'table': table}

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch['count']
    # ____________________________

    def remove_all_records(self, table):
        logger.info("DB: {}".format(self.db.__dict__))
        query = """
            DELETE FROM %(table)s
        """
        params = ()
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________

    def update(self, table, key_name, key_value, items):
        sql_template = "UPDATE {} SET ({}) = %s WHERE {} = %s"
        query = sql_template.format(table, ', '.join(items.keys()), key_name)
        params = list(items.values())
        params.append(key_value)
        logger.info("Params: %r", params)

        logger.info("Query: {}".format(self.db.cursor.mogrify(query, params)))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
