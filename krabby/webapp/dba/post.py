from flask import current_app
from psycopg2.extensions import AsIs

# ============================================


class QueryPost(object):
    def __init__(self, db):
        self.db = db
    # ____________________________

    def read(self, sort_by, sort_order, offset, limit):
        query = """
            SELECT
                p.id,
                p.body,
                p.body_html,
                p.postdate,
                p.authorid,
                u.username,
                u.email,
                u.avatar_hash
            FROM posts AS p, users AS u
            WHERE p.authorid = u.id
            ORDER BY %s %s
            OFFSET %s
        """
        params = [AsIs(sort_by), AsIs(sort_order), AsIs(offset)]

        if limit is not None:
            query += 'LIMIT %s'
            params.append(AsIs(limit))

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        if fetch is None:
            return fetch

        current_app.logger.debug("Fetch: {}".format(fetch))
        return fetch
    # ____________________________

    def read_by_field(self, field_name, field_value):
        query = """
            SELECT
                p.id,
                p.body,
                p.body_html,
                p.postdate,
                p.authorid,
                u.username,
                u.email,
                u.avatar_hash
            FROM posts AS p, users AS u
            WHERE p.authorid = u.id
            AND p.%s = %s
        """
        params = (AsIs(field_name), field_value)

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        if fetch is None:
            return fetch

        current_app.logger.debug("Fetch: {}".format(fetch))
        return fetch
    # ____________________________

    def create(self, attrs):
        query_template = """
            INSERT INTO posts ({})
            VALUES ({})
            RETURNING id
        """
        fields = ', '.join(attrs.keys())
        current_app.logger.debug("Fields: {}".format(fields))

        values_placeholders = ', '.join(['%s' for v in attrs.values()])
        query = query_template.format(fields, values_placeholders)
        current_app.logger.debug("query: {}".format(query))
        current_app.logger.debug("values: {}".format(attrs.values()))

        params = tuple(attrs.values())

        current_app.logger.debug(self.db.cursor.mogrify(query, params))

        self.db.cursor.execute(query, params)
        self.db.conn.commit()
        fetch = self.db.cursor.fetchone()
        current_app.logger.debug("FETCH: {}".format(fetch))
        return fetch['id']

    # ____________________________

    def remove_all_records(self):
        query = """
            DELETE FROM posts
        """
        params = ()
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________

    def update(self, update_key_name, update_key_value, update_params):
        sql_template = "UPDATE posts SET ({}) = %s WHERE {} = %s"
        query = sql_template.format(', '.join(update_params.keys()), update_key_name)
        params = (tuple(update_params.values()), update_key_value)
        print(self.db.cursor.mogrify(query, params))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________
