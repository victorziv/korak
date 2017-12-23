import pprint
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs
from config import logger, conf
from models import (  # noqa
    db, Basemod, Jirahelper,
    Sessiontaskmod, Usermod, Customermod
)
from lib.exceptions import (
    JiraIVTTicketNotFound,
    JiraShipmentTicketNotFound
)
from lib.helpers import (
    calculate_date_range,
    convert_to_utc,
    generate_uid,
)

jira = Jirahelper()
sessiontaskmod = Sessiontaskmod()
usermod = Usermod(db)
customermod = Customermod(db)
# =============================


class Sessionmod(Basemod):

    table = 'session'
    # ____________________________

    def calculate_session_result(self, sessionid):
        task_results = self.fetch_task_results(sessionid)
        logger.debug("Session %r task results: %r", sessionid, task_results)
        if not len(task_results):
            return None
        return all([r for r in task_results])
    # ____________________________

    def create_session(self, sn, duedate_include_weekends):
        # Save machine to machine table if not already there
        session = self.parse_jira_shipment_ticket(sn)
        session.update(self.parse_jira_ivt_ticket(sn))

        logger.debug("SESSION FROM SHIPMENT & IVT TICKETs: %r", session)

        session['uid'] = "%s-%s" % (sn, generate_uid())
        session['state'] = 'pending'
        session['weekend_included'] = duedate_include_weekends
        session['start'], session['due'] = calculate_date_range(
            session['verification_type']['rundays'], duedate_include_weekends)

        sessionid = self.save_session(session)
        logger.debug("New verification session ID: %s", sessionid)

        sessiontaskmod.populate_session_tasks(sessionid)
        return sessionid
    # ____________________________

    def save_session(self, session):

        query = sql.SQL("""
            INSERT INTO {}
            (
                uid, sn, system_name, model, shipment_ticket,
                customerid,  typeid, slot, ownerid, ticket,
                created, state, start, due, weekend_included
            )
            VALUES (
                %(uid)s,
                %(sn)s,
                %(system_name)s,
                %(model)s,
                %(shipment_ticket)s,
                %(customerid)s,
                %(typeid)s,
                %(slot)s,
                %(ownerid)s,
                %(ticket)s,
                %(created)s,
                %(state)s,
                %(start)s,
                %(due)s,
                %(weekend_included)s
            )
            RETURNING id
        """).format(sql.Identifier(self.table))

        logger.info("Mogrify: {}".format(db.cursor.mogrify(query, session)))

        try:
            db.cursor.execute(query, session)
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

    def delete(self, machineid):
        sessionuid = self.get_uid_by_id(machineid)
        self.remove_session_queue(sessionuid)
        self.remove_session_tasks(machineid)
        self.remove_session(machineid)
    # ____________________________

    def get_uid_by_id(self, machineid):
        query = sql.SQL("""
            SELECT uid FROM session
            WHERE id = %s
        """)
        params = (machineid,)

        try:
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return
            return fetch['uid']
        except Exception:
            logger.exception('!ERROR')
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_page(self, params):
        sort_field = params['sort_field']
        sort_order = params['sort_order']
        limit = params.get('limit', None)
        offset = params.get('offset', 0)

        query = """
            SELECT
               s.id,
               s.uid,
               s.sn,
               s.system_name,
               s.ticket,
               s.model,
               s.slot,
               c.name AS customer,
               u.username AS owner_username,
               u.name AS owner_name,
               u.email AS owner_email,
               u.social_id AS owner_socialid,
               t.name as verification_type,
               s.state,
               s.result,
               s.start,
               s.due,
               s.weekend_included,
               s.created
            FROM session s, customer c, verification_type t, users u
            WHERE s.customerid = c.id
            AND s.typeid = t.id
            AND s.ownerid = u.id
            ORDER BY %s %s
            LIMIT %s
            OFFSET %s
        """
        params = (AsIs(sort_field), AsIs(sort_order), AsIs(limit), AsIs(offset))

        try:
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchall()
            logger.info("Fetch page type: {}".format(type(fetch)))
            return fetch
        except Exception:
            logger.exception('!ERROR')
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_session(self, sessionid):
        query = sql.SQL("""
            SELECT
               s.id,
               s.uid,
               s.sn,
               s.system_name,
               s.ticket,
               s.model,
               s.slot,
               c.name AS customer,
               u.username AS owner_username,
               u.name AS owner_name,
               u.email AS owner_email,
               u.social_id AS owner_socialid,
               t.name as verification_type,
               s.state,
               s.result,
               s.start,
               s.due,
               s.weekend_included,
               s.created
            FROM session s, customer c, verification_type t, users u
            WHERE s.customerid = c.id
            AND s.typeid = t.id
            AND s.ownerid = u.id
            AND s.id = %s
        """)
        params = (sessionid,)

        try:
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return {}
            return dict(fetch)
        except Exception:
            logger.exception('!ERROR')
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_task_results(self, sessionid):
        try:
            query = sql.SQL("""
                SELECT result FROM session_task WHERE sessionid = %s
            """)

            params = (sessionid, )

            db.cursor.execute(query, params)
            fetch = db.cursor.fetchall()
            if fetch is None:
                return []
            return [f['result'] for f in fetch]
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_session_task_states(self, sessionid):
        try:
            query = sql.SQL("""
                SELECT state FROM session_task WHERE sessionid = %s
            """)

            params = (sessionid, )

            db.cursor.execute(query, params)
            fetch = db.cursor.fetchall()
            return [f['state'] for f in fetch]
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_running_by_sn(self, sn):
        try:
            query = sql.SQL("""
                SELECT id
                FROM {}
                WHERE sn = %s
                AND state NOT IN ('finished', 'aborted')
            """).format(sql.Identifier(self.table))

            params = (sn, )

            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return 0
            return fetch['id']
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_sn_by_id(self, sessionid):
        try:
            query = sql.SQL("""
                SELECT sn FROM session WHERE id = %s
            """)

            params = (sessionid, )

            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return 0
            return fetch['sn']
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_verification_type_names(self):
        query = """
            SELECT name
            FROM verification_type
            ORDER BY priority ASC
        """
        params = ()

        logger.info("QUERY: {}".format(db.cursor.mogrify(query, params)))
        db.cursor.execute(query, params)
        fetch = db.cursor.fetchall()
        return [f['name'] for f in fetch]
    # ____________________________

    def fetch_verification_type_by_name(self, name):
        query = """
            SELECT id, name, rundays
            FROM verification_type
            WHERE name = %s
        """
        params = (name,)

        logger.info("QUERY: {}".format(db.cursor.mogrify(query, params)))
        db.cursor.execute(query, params)
        fetch = db.cursor.fetchone()
        return dict(fetch)
    # ____________________________

    def figure_verification_type(self, labels):
        types = self.fetch_verification_type_names()
        logger.info("Fetched types: %r", types)
        logger.info("Got labels: %r", labels)

        found = 'NONRPQ'
        for t in types:
            if t in labels:
                found = t
        logger.info("Type found: %r", found)

        return self.fetch_verification_type_by_name(found)
    # ____________________________

    def parse_jira_ivt_ticket(self, sn):

        ticket, issue = jira.get_manufacturing_ticket(sn=sn, issue_type="IVT")
        if ticket is None:
            raise JiraIVTTicketNotFound("JIRA IVT ticket not found for machine S/N {}".format(self.serial_number))

        logger.debug("Jira ticket: %r", ticket)
        logger.debug("Jira issue: {}".format(pprint.pformat(issue.__dict__)))

        machine = {}
        machine['ticket'] = ticket

        ownerid = usermod.save_from_jira_assignee(issue.fields.assignee)
        machine['ownerid'] = ownerid

        machine['slot'] = issue.fields.environment
        machine['verification_type'] = self.figure_verification_type(issue.fields.labels)
        machine['typeid'] = machine['verification_type']['id']
        machine['created'] = convert_to_utc(issue.fields.created)
        machine['due'] = issue.fields.duedate
        logger.debug("MACHINE FETCHED FROM JIRA TICKET: %r", machine)
        return machine

    # ____________________________

    def parse_jira_shipment_ticket(self, sn):

        ticket, issue = jira.get_manufacturing_ticket(sn=sn, issue_type="Shipment")
        if ticket is None:
            raise JiraShipmentTicketNotFound(
                "JIRA Shipment ticket not found for machine S/N {}".format(sn))

        machine = {}
        machine['sn'] = int(sn)
        machine['system_name'] = "%s%s" % (conf['MACHINE_NAME_PREFIX'], sn)
        machine['shipment_ticket'] = ticket
        machine['model'] = issue.fields.customfield_12904.value

        customer_name = issue.fields.customfield_12725.value
        customermod = Customermod()
        machine['customerid'] = customermod.create(attrs={'name': customer_name})
        return machine
    # ____________________________

    def remove_session(self, sessionid):
        query = sql.SQL("""
            DELETE FROM {0}
            WHERE id = %s
        """).format(sql.Identifier(self.table))

        params = (sessionid, )
        try:
            db.cursor.execute(query, params)
            db.conn.commit()
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
    # ____________________________

    def remove_session_queue(self, sessionuid):

        query = """
            DELETE FROM task_queue
            WHERE sessionuid = %s
        """

        params = (sessionuid,)
        try:
            db.cursor.execute(query, params)
            db.conn.commit()
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
    # ____________________________

    def remove_session_tasks(self, sessionid):

        query = """
            DELETE FROM session_task
            WHERE sessionid = %s
        """

        params = (sessionid,)
        try:
            db.cursor.execute(query, params)
            db.conn.commit()
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
    # ____________________________

    def update_session_from_jira(self, sessionid):
        sn = self.fetch_sn_by_id(sessionid)
        logger.debug("UPDATE SN in session %s: %r", sn, sessionid)
        session = self.parse_jira_shipment_ticket(sn)
        session.update(self.parse_jira_ivt_ticket(sn))
        self.update_session(sessionid, session)
        return sessionid
    # ____________________________

    def update_session(self, sessionid, session):

        query = sql.SQL("""
            UPDATE {}
            SET
                slot = %(slot)s,
                ownerid = %(ownerid)s,
                model = %(model)s,
                customerid = %(customerid)s,
                due = %(due)s
            RETURNING id
        """).format(sql.Identifier(self.table))

        logger.info("Mogrify: {}".format(db.cursor.mogrify(query, session)))

        try:
            db.cursor.execute(query, session)
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

    def update_session_state(self, sessionid, state):
        query = """
            UPDATE session
            SET state = %s
            WHERE id = %s
        """
        params = (state, sessionid)
        try:
            db.cursor.execute(query, params)
            db.conn.commit()
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
