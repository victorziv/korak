import psycopg2
from psycopg2 import sql
from webapp.models import db
from config import logger
# =========================================


class Permission:
    FOLLOW = 0x01               # 0b00000001
    COMMENT = 0x02              # 0b00000010
    WRITE_ARTICLES = 0x04       # 0b00000100
    MODERATE_COMMENTS = 0x08    # 0b00001000
    ADMINISTER = 0x80           # 0b10000000
# =========================================


class Basemod:

    def __init__(self, db=None):
        self.db = db
    # ___________________________________

    def fetch_total(self):
        query = sql.SQL("SELECT COUNT(*) AS total FROM {0}").format(sql.Identifier(self.table))

        params = ()

        try:
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return 0
            logger.debug("%s total: %r", self.table, fetch['total'])
            return fetch['total']
        except Exception:
            logger.exception('!ERROR')
            db.conn.rollback()
            return
    # ____________________________________________

    def insert(self, table, attrs):

        query_template = """
            INSERT INTO %s
            ({})
            VALUES ({})
            RETURNING id
        """ % table

        fields = ', '.join(attrs.keys())
        logger.info("Fields: {}".format(fields))
        values_placeholders = ', '.join(['%s' for v in attrs.values()])

        query = query_template.format(fields, values_placeholders)
        params = tuple(attrs.values())
        logger.info("Query: {}".format(query))
        logger.info("Params: {}".format(params))

        logger.info("Mogrify: {}".format(db.cursor.mogrify(query, params)))

        try:
            db.cursor.execute(query, params)
            db.conn.commit()
            fetch = db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            return fetch['id']
        except psycopg2.IntegrityError as e:
            logger.warning(e)
            db.conn.rollback()
            raise
        except psycopg2.ProgrammingError:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
        except Exception:
            db.conn.rollback()
            raise
    # ____________________________

    def update(self, table, rowid, row):
        try:
            query_template = "UPDATE {} SET ({}) = %s WHERE id = {}"
            query = query_template.format(table, ', '.join(row.keys()), rowid)
            params = (tuple(row.values()),)

            logger.debug("Mogrify: {}".format(db.cursor.mogrify(query, params)))
            db.cursor.execute(query, params)
            db.conn.commit()
        except Exception:
            db.conn.rollback()
            logger.exception("!UPDATE SESSION TASK ERROR")
            raise
    # ____________________________
