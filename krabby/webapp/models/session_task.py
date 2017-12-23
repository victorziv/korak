import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs
from config import logger
from models import db, Basemod
# =============================


class Sessiontaskmod(Basemod):

    def __init__(self):
        self.table = 'session_task'

    # ____________________________

    def fetch_page(self, params):

        sessionid = params['sessionid']
        sort_field = params['sort_field']
        sort_order = params['sort_order']
        limit = params['limit']
        offset = params['offset']

        query = """
            SELECT
               st.id,
               st.sessionid,
               t.name AS taskname,
               st.state,
               st.result,
               st.start,
               st.finish,
               st.message,
               st.log
            FROM
                task t,
                session_task st,
                type_task_map tm
            WHERE st.sessionid = %s
            AND st.taskmapid = tm.id
            AND tm.taskid = t.id

            ORDER BY %s %s
            LIMIT %s
            OFFSET %s
        """

        params = (sessionid, AsIs(sort_field), AsIs(sort_order), AsIs(limit), AsIs(offset))

        try:
            logger.debug("Mogrify: {}".format(db.cursor.mogrify(query, params)))
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchall()
            return fetch
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            return []
    # ____________________________

    def fetch_session_task(self, taskid):

        query = """
            SELECT
               st.id,
               st.sessionid,
               s.uid AS sessionuid,
               t.name AS taskname,
               st.state,
               st.result,
               st.start,
               st.finish,
               st.log
            FROM
                task t,
                session_task st,
                type_task_map tm,
                session s
            WHERE st.id = %s
            AND st.taskmapid = tm.id
            AND tm.taskid = t.id
            AND st.sessionid = s.id
        """

        params = (taskid,)

        try:
            logger.debug("Mogrify: {}".format(db.cursor.mogrify(query, params)))
            db.cursor.execute(query, params)
            fetch = db.cursor.fetchone()
            if fetch is None:
                return {}
            return dict(fetch)
        except Exception:
            logger.exception("!ERROR")
            db.conn.rollback()
            raise
    # ____________________________

    def fetch_total(self, sessionid):
        query = sql.SQL("""
            SELECT COUNT(*) AS total FROM {0}
            WHERE sessionid = %s
        """).format(sql.Identifier(self.table))

        params = (sessionid,)

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
    # ____________________________

    def fetch_taskids_by_verification_type(self, sessionid):
        query = """
            SELECT id
            FROM type_task_map
            WHERE typeid  = ( SELECT typeid FROM session WHERE ID = %s )
        """
        params = (sessionid,)

        db.cursor.execute(query, params)
        fetch = db.cursor.fetchall()
        return [f['id'] for f in fetch]
    # ____________________________

    def populate_session_tasks(self, sessionid):
        task_map_ids = self.fetch_taskids_by_verification_type(sessionid)
        self.insert_session_tasks(sessionid, task_map_ids)
    # ____________________________

    def insert_session_tasks(self, sessionid, task_map_ids):

        for mapid in task_map_ids:
            query = sql.SQL("""
                INSERT INTO {0}
                (sessionid, taskmapid, state)
                VALUES ( %s, %s, %s )
            """.format(self.table))

            params = (sessionid, mapid, 'pending')
            logger.debug("Mogrify: {}".format(db.cursor.mogrify(query, params)))

            try:
                db.cursor.execute(query, params)
                db.conn.commit()
            except psycopg2.IntegrityError as e:
                logger.warning(e)
                db.conn.rollback()
            except Exception:
                logger.exception("!ERROR")
                db.conn.rollback()
    # ____________________________

    def put_session_task_in_queue(self, task):

        query = sql.SQL("""
            INSERT INTO task_queue
            (sessionuid, sessiontaskid, taskname, scheduled_on)
            VALUES( %s, %s, %s, %s)
            RETURNING sessiontaskid
        """)

        params = (
            task['sessionuid'],
            task['session_taskid'],
            task['session_task_name'],
            datetime.datetime.utcnow()
        )

        try:
            db.cursor.execute(query, params)
            db.conn.commit()
            fetch = db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            return fetch['sessiontaskid']
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

    def put_taskmng_in_queue(self, task):
        query = sql.SQL("""
            INSERT INTO taskmng_queue
            (sessionuid, sessiontaskid, taskname, action, scheduled_on)
            VALUES( %s, %s, %s, %s, %s)
            RETURNING sessiontaskid
        """)

        params = (
            task['sessionuid'],
            task['session_taskid'],
            task['session_task_name'],
            task['action'],
            datetime.datetime.utcnow()
        )

        try:
            db.cursor.execute(query, params)
            db.conn.commit()
            fetch = db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            return fetch['sessiontaskid']
        except psycopg2.IntegrityError as e:
            logger.warning(e)
            db.conn.rollback()
        except psycopg2.ProgrammingError:
            logger.exception("!ERROR")
            db.conn.rollback()
        except Exception:
            db.conn.rollback()
            raise
    # ____________________________

#     def stop_task(self, task):
#         logger.debug("Stop task")
#         query = sql.SQL("""
#             UPDATE {0}
#             SET state = 'aborted'
#             WHERE id = %s
#         """).format(sql.Identifier(self.table))

#         try:
#             params = (task['session_taskid'])
#             db.cursor.execute(query, params)
#             db.conn.commit()
#             fetch = db.cursor.fetchone()
#             logger.debug("FETCH: {}".format(fetch))
#             return fetch['sessiontaskid']
#         except Exception:
#             db.conn.rollback()
#             raise
    # ____________________________

#     def update_task_state(self, taskid, state):
#         try:

#             query = sql.SQL("""
#                 UPDATE {0}
#                 SET
#                     state = %s
#                 WHERE id = %s
#             """).format(sql.Identifier(self.table))

#             params = (state, taskid)

#             logger.debug("Mogrify: {}".format(db.cursor.mogrify(query, params)))
#             db.cursor.execute(query, params)
#             db.conn.commit()
#         except Exception:
#             db.conn.rollback()
#             logger.exception("!UPDATE TASK STATE ERROR")
#             raise
    # ____________________________
