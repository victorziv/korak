from flask import current_app as cap
from psycopg2.extensions import AsIs

# ============================================


class QueryFollow(object):
    def __init__(self, db):
        self.db = db
    # ____________________________

    def create(self, attrs):

        query_template = """
            INSERT INTO follow ({})
            VALUES ({})
        """
        fields = ', '.join(attrs.keys())
        cap.logger.debug("Fields: {}".format(fields))
        values_placeholders = ', '.join(['%s' for v in attrs.values()])
        query = query_template.format(fields, values_placeholders)
        cap.logger.debug("query: {}".format(query))
        cap.logger.debug("values: {}".format(attrs.values()))
        params = tuple(attrs.values())

        cap.logger.debug(self.db.cursor.mogrify(query, params))

        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________

    def read_by_fields(self, fields):

        query = """
            SELECT
                following_id,
                followed_by_id,
                started_following
            FROM follow
            WHERE %s = %s
        """

        if len(fields) > 1:
            for f in fields[1:]:
                query += " AND %s = %s"

        params = []
        for f in fields:
            params.extend((AsIs(f['name']), f['value']))

        self.db.cursor.execute(query, params)
        print(self.db.cursor.mogrify(query, params))
        fetch = self.db.cursor.fetchone()
        cap.logger.debug("Fetch: {}".format(fetch))
        return fetch
    # ____________________________

    def read_one_by_field(self, **kwargs):

        field = next(iter(kwargs.keys()))

        query = """
            SELECT
                following_id,
                followed_by_id,
                started_following
            FROM follow
            WHERE %s = %s
        """
        params = (AsIs(field), kwargs[field])
        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        cap.logger.debug("Fetch: {}".format(fetch))
        return fetch
    # ____________________________

    def delete(self, following_id, followed_by_id):
        query = """
            DELETE FROM follow
            WHERE following_id = %s
            AND followed_by_id = %s
        """
        params = (following_id, followed_by_id)

        self.db.cursor.execute(query, params)
        self.db.conn.commit()
