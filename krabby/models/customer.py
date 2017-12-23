import psycopg2
from config import logger
from models import db, Basemod
# =============================


class Customermod(Basemod):

    table = 'customer'

    # ____________________________

    def create(self, attrs):

        query_template = """
            INSERT INTO %s
            ({})
            VALUES ({})
            RETURNING id
        """ % self.table

        fields = ', '.join(attrs.keys())
        logger.info("Fields: {}".format(fields))
        values_placeholders = ', '.join(['%s' for v in attrs.values()])

        query = query_template.format(fields, values_placeholders)
        params = tuple(attrs.values())

        logger.info("Mogrify: {}".format(db.cursor.mogrify(query, params)))

        try:
            db.cursor.execute(query, params)
            db.conn.commit()
            fetch = db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            return fetch['id']
        except psycopg2.IntegrityError as e:
            logger.info("!!!!ERROR: %s", e)
            db.conn.rollback()
            return self.get_id_by_name(attrs['name'])
        except psycopg2.ProgrammingError:
            logger.exception("!ERROR")
            db.conn.rollback()
        except Exception:
            db.conn.rollback()
            raise
    # ____________________________

    def get_id_by_name(self, name):
        query = """
            SELECT id
            FROM customer
            WHERE name = %s
        """
        params = (name,)

        logger.info("QUERY: {}".format(db.cursor.mogrify(query, params)))
        db.cursor.execute(query, params)
        fetch = db.cursor.fetchone()
        return fetch['id']
    # ____________________________
