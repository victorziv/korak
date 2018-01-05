from flask import current_app
from flask import current_app as cap
from psycopg2 import DatabaseError, IntegrityError
from psycopg2.extensions import AsIs

# ============================================


class QueryUser(object):
    def __init__(self, db):
        self.db = db
    # ____________________________

    def read_one_by_field(self, **kwargs):

        if len(kwargs) != 1:
            raise RuntimeError("Accepts exactly one parameter for a field name")

        field = next(kwargs.__iter__())
        query = """
            SELECT
                u.id,
                u.email,
                u.username,
                u.password_hash,
                u.location,
                u.about_me,
                u.member_since,
                u.last_seen,
                u.avatar_hash,
                r.name AS role,
                r.permissions
            FROM users AS u, roles AS r
            WHERE u.role_id = r.id
            AND u.%s = %s
        """

        params = (AsIs(field), kwargs[field])

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch
    # ____________________________

    def read_following_count(self, followed_by_id):

        query = """
            SELECT COUNT(*) AS count
            FROM follow
            WHERE followed_by_id = %s
        """

        params = (followed_by_id,)

        self.db.cursor.execute(query, params)
        cap.logger.debug("Query: {}".format(self.db.cursor.mogrify(query, params)))
        fetch = self.db.cursor.fetchone()
        cap.logger.debug("Fetch: {}".format(fetch))
        return int(fetch['count'])
    # ____________________________

    def read_followed_by_count(self, following_id):

        query = """
            SELECT COUNT(*) AS count
            FROM follow
            WHERE following_id = %s
        """

        params = (following_id,)

        self.db.cursor.execute(query, params)
        cap.logger.debug("Query: {}".format(self.db.cursor.mogrify(query, params)))
        fetch = self.db.cursor.fetchone()
        cap.logger.debug("Fetch: {}".format(fetch))
        return int(fetch['count'])
    # ____________________________

    def read_one_with_offset(self, offset):

        query = """
            SELECT
                u.id,
                u.email,
                u.username,
                u.password_hash,
                u.location,
                u.about_me,
                u.member_since,
                u.last_seen,
                u.avatar_hash,
                r.name AS role,
                r.permissions
            FROM users u, roles r
            WHERE u.role_id = r.id
            ORDER BY id ASC
            LIMIT 1
            OFFSET %s
        """

        params = (offset,)

        self.db.cursor.mogrify(query, params)
        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch
    # ____________________________

    def read(self, **kwargs):
        query = """
            SELECT
                u.id,
                u.email,
                u.username,
                r.name AS role,
                r.permissions
            FROM users AS u, roles AS r
            WHERE u.role_id = r.id
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchall()
        return fetch
    # ____________________________

    def read_total(self):
        query = """
            SELECT count(*) FROM users
        """
        params = ()

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()
        return fetch['count']
    # ____________________________

    def fetch_id_by_field(self, field_name, field_value):
        query_template = """
            SELECT id
            FROM users
            WHERE {} = %s
        """

        query = query_template.format(field_name)

        params = (field_value,)
        current_app.logger.debug(self.db.cursor.mogrify(query, params))

        self.db.cursor.execute(query, params)
        fetch = self.db.cursor.fetchone()

        return fetch['id']
    # ____________________________

    def create(self, attrs):

        query_template = """
            INSERT INTO users ({})
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

        try:
            self.db.cursor.execute(query, params)
            fetch = self.db.cursor.fetchone()
            current_app.logger.debug("FETCH: {}".format(fetch))
            return fetch['id']
        except IntegrityError:
            self.db.conn.rollback()
            return self.fetch_id_by_field('email', attrs['email'])
        except Exception:
            raise
        else:
            self.db.conn.commit()
    # ____________________________

    def create_oauth(self, email, username, social_id, role_id):
        """
        id = SERIAL primary_key=True)
        email = String(64), unique=True, index=True
        username String(64), unique=True, index=True
        password = String(128), salted SHA1 hash
        role_id = ObjectId, db.ForeignKey('roles.id'))
        """

        query = """
            INSERT INTO users (email, username, social_id, role_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """

        params = (email, username, social_id, role_id)

        try:
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
            fetch = self.db.cursor.fetchone()
            print("XXXXX==> FETCH: {}".format(fetch))
            return fetch['id']

        except IntegrityError as ie:
            print('ERROR: %s' % ie)
            self.db.conn.rollback()
            return
        except DatabaseError as dbe:
            print('ERROR: %s' % dbe)
            self.db.conn.rollback()
            return
    # ____________________________

    def remove_all_records(self):
        query = """
            DELETE FROM users
        """
        params = ()
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________

    def update(self, update_key_name, update_key_value, update_params):
        sql_template = "UPDATE users SET ({}) = %s WHERE {} = %s"
        query = sql_template.format(', '.join(update_params.keys()), update_key_name)
        params = (tuple(update_params.values()), update_key_value)
        print(self.db.cursor.mogrify(query, params))
        self.db.cursor.execute(query, params)
        self.db.conn.commit()
    # ____________________________
