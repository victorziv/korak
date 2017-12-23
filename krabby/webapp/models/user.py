import psycopg2
from psycopg2 import sql
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, request
from flask_login import UserMixin
from flask import current_app as cup
from config import logger
from . import (
    db, login_manager, Basemod, Rolemod, Permission
)
rolemod = Rolemod()
# ===========================


class Usermod(UserMixin, Basemod):

    table = 'users'
    # __________________________________

    def fetch_by_social_id(self, social_id):
        try:
            return self.fetch_by_field(field_name='social_id', field_value=social_id)
        except Exception:
            logger.exception('FETCH BY SOCIAL ID')
            return {}
    # __________________________________

    def fetch_by_username(self, username):
        try:
            return dict(self.fetch_by_field(field_name='username', field_value=username))
        except Exception:
            logger.exception('FETCH BY Username')
            db.conn.rollback()
            return {}
    # __________________________________

    def fetch_id_by_username(self, username):
        query = sql.SQL("""
            SELECT id FROM users WHERE username = %s
        """)

        params = (username,)

        db.cursor.execute(query, params)
        fetch = db.cursor.fetchone()
        logger.debug("Fetch: %r", fetch)
        if fetch is None:
            return 0

        return fetch['id']

    # __________________________________

    def fetch_by_field(self, field_name, field_value):
        query = sql.SQL("""
            SELECT
                u.id,
                u.social_id,
                u.email,
                u.username,
                u.name,
                u.given_name,
                u.family_name,
                u.picture
            FROM users u
            WHERE {} = %s
        """).format(sql.Identifier(field_name))

        params = (field_value,)

        db.cursor.execute(query, params)
        fetch = db.cursor.fetchone()
        logger.debug("Fetch: %r", fetch)
        if fetch is None:
            return {}

        return fetch
    # __________________________________

    def fetch_name_by_username(self, username):

        query = sql.SQL("""
            SELECT name FROM {}
            WHERE username = %s
        """).format(sql.Identifier(self.table))

        params = (username, )

        try:
            logger.debug("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            fetch = self.db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            if fetch is None:
                return ''
            return fetch['name']
        except Exception:
            db.conn.rollback()
            raise
    # ____________________________

    def get_by_social_id(self, social_id):
        userd = self.fetch_by_social_id(social_id)
        if not userd:
            return None
        self.__dict__.update(userd)
        return self
    # __________________________________

    def get_all(self):
        """
        Fetches all existent users from the DB.

        :Returns:
            A list of User() objects - an object per fetched user.

        """
        user_dicts = self.fetch_users()
        return [
            self.set_user_attributes(user_dict)
            for user_dict in user_dicts
        ]
    # ____________________________

    def gravatar(self, size=100, default='identicon', rating='g'):

        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'

        logger.debug("Avatar hash: {}".format(self.avatar_hash))
        if self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            Usermod.update_user(params={'email': self.email, 'avatar_hash': self.avatar_hash})

        return '{url}/{checksum}?s={size}&d={default}&r={rating}'.format(
            url=url, checksum=self.avatar_hash, size=size, default=default, rating=rating)
    # ____________________________

    def to_json(self):

        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

        return json_user

    # __________________________________

    def can(self, permissions):
        """
        Figures out whether the current role can do anything
        given a set of permissions to check against.

        :Returns:
            bool : True or False

        """
        logger.info("User {} role: {}".format(self.email, self.role))
        return self.role is not None and (
            self.permissions & permissions) == permissions
    # __________________________________

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    # __________________________________

    def generate_auth_token(self, expiration):
        s = Serializer(cup.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})
    # __________________________________

    def insert(self, profile):

        fields = ['social_id', 'username', 'email', 'name', 'given_name', 'family_name', 'picture']
        user = {k: profile.get(k, None) for k in profile if k in fields}

        query_template = """
            INSERT INTO %s
            ({})
            VALUES ({})
            RETURNING id
        """ % self.table

        fields = ', '.join(user.keys())
        logger.info("Fields: {}".format(fields))
        values_placeholders = ', '.join(['%s' for v in user.values()])

        query = query_template.format(fields, values_placeholders)
        params = tuple(user.values())
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
            return self.fetch_id_by_username(user['username'])
        except Exception:
            db.conn.rollback()
            logger.exception("!INSERT USER EXCEPTION")
            return 0
# ____________________________

    def save(self, profile, role='user'):

        # Set user role
#         if role.lower() == 'admin':
            # user is an administrator
#             role = rolemod.fetch_by_field(name='permissions', value=0xFF)
#         else:
#             role = rolemod.fetch_by_field(name='name', value=role.lower())

#         logger.debug("Role: {}".format(role))

        user = self.fetch_by_username(profile['username'])
        if user:
            self.id = self.update_user_account(profile)
        else:
            self.id = self.insert(profile)

        logger.info("New user ID: %r", self.id)
        self.__dict__.update(profile)
        return self
    # ____________________________

    def save_from_jira_assignee(self, assignee):

        """
        Assignee dictionary fetched from the Jira ticket:

            'assignee': {
                'active': True,
                'displayName': 'Rami Hassan',
                'emailAddress': 'rhassan@infinidat.com',
                'key': 'rhassan',
                'name': 'rhassan',
                'self': 'https://jira.infinidat.com/rest/api/2/user?username=rhassan',
                'timeZone': 'Asia/Jerusalem'
            }

        """
        user = {
            'username': assignee.key,
            'email': assignee.emailAddress,
            'name': assignee.displayName
        }

        return self.insert(user)
    # ____________________________

    def update_user_account(self, profile):

        userid = profile.pop('id')
        fields = ['social_id', 'email', 'name', 'given_name', 'family_name', 'picture']
        user = {k: profile.get(k, None) for k in profile if k in fields}
        self.update(self.table, userid, user)
        return userid
    # ____________________________

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(cup.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None

        return Usermod.get_by_field(name='id', value=data['id'])

# ===========================


@login_manager.user_loader
def load_user(user_id):
    try:
        u = Usermod()
        userd = u.fetch_by_field(field_name='id', field_value=user_id)
        u.__dict__.update(userd)
        return u
    except Exception:
        logger.exception("!! Load user exception")
        u.__dict__.update({})
        return u
