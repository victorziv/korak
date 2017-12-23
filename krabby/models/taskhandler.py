from psycopg2 import sql
import datetime
from models import Basemod
from config import logger
# =============================


class Taskhandler(Basemod):

    def fetch_task_worker(self, sessionuid):

        query = sql.SQL("""
            SELECT worker FROM task_queue
            WHERE sessionuid = %s
        """)

        params = (sessionuid, )

        try:
            self.db.cursor.execute(query, params)
            fetch = self.db.cursor.fetchone()
            logger.debug("FETCH: {}".format(fetch))
            if fetch is None:
                return ''
            return fetch['worker']
        except Exception:
            self.db.conn.rollback()
            raise
    # ____________________________

    def fetch_queued_task(self):
        """
        TRANSACTION: select one task from queue,
        then update fetched_on field of the selected task
        This is for not fetching the same task more than once
        """
        query_select = """
            SELECT
               tq.sessiontaskid,
               st.taskuid,
               tq.sessionuid,
               tq.scheduled_on,
               tq.taskname,
               m.system_name
            FROM task_queue tq, session s, machine m, session_task st
            WHERE fetched_on is NULL
            AND tq.sessiontaskid = st.id
            AND tq.sessionuid = s.uid
            AND s.machineid = m.id
            ORDER BY scheduled_on ASC
            LIMIT 1
            FOR UPDATE
        """

        query_update = sql.SQL("""
            UPDATE task_queue
            SET fetched_on = %s
            WHERE sessionuid = %s
        """)

        try:
            self.db.cursor.execute(query_select, [])
            fetch = self.db.cursor.fetchone()
            if not fetch:
                return {}

            update_params = (datetime.datetime.utcnow(), fetch['sessionuid'])
            logger.debug("Mogrify update: {}".format(self.db.cursor.mogrify(query_update, update_params)))
            self.db.cursor.execute(query_update, update_params)
            self.db.conn.commit()
            return dict(fetch)
        except Exception:
            self.db.conn.rollback()
            logger.exception("Fetch task EXCEPTION!")
    # ____________________________

    def fetch_taskmng(self):
        """
        TRANSACTION: select one mng from queue,
        then update fetched_on field of the selected task
        This is for not fetching the same task more than once
        """
        query_select = """
            SELECT
               st.taskuid,
               tmng.sessionuid,
               tmng.scheduled_on,
               tmng.taskname,
               tmng.action,
               m.system_name
            FROM taskmng_queue tmng, session s, machine m, session_task st
            WHERE tmng.sessionuid = s.uid
            AND tmng.sessiontaskid = st.id
            AND s.machineid = m.id
            ORDER BY scheduled_on ASC
            LIMIT 1
            FOR UPDATE
        """

        query_update = sql.SQL("""
            DELETE FROM taskmng_queue
            WHERE sessionuid = %s
        """)

        try:
            self.db.cursor.execute(query_select, [])
            fetch = self.db.cursor.fetchone()
            if not fetch:
                return {}

            delete_params = (fetch['sessionuid'],)
            logger.debug("Mogrify delete: {}".format(self.db.cursor.mogrify(query_update, delete_params)))
            self.db.cursor.execute(query_update, delete_params)
            self.db.conn.commit()
            return dict(fetch)
        except Exception:
            self.db.conn.rollback()
            logger.exception("Fetch mng EXCEPTION!")
    # ____________________________

    def register_worker(self, task):
        try:
            query = sql.SQL("""
                UPDATE task_queue
                SET
                    worker = %s
                WHERE sessionuid = %s
            """)

            params = (task['worker'], task['sessionuid'])

            logger.debug("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
        except Exception:
            self.db.conn.rollback()
            logger.exception("!UPDATE TASK STATE ERROR")
            raise

    # ____________________________

    def remove_from_queue(self, task_item):
        try:

            query = sql.SQL("""
                DELETE FROM task_queue
                WHERE sessionuid = %s
            """)

            params = (task_item['sessionuid'],)

            logger.debug("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
        except Exception:
            self.db.conn.rollback()
            logger.exception("!ERROR")
            raise

    # ____________________________

    def reset_task_fetch(self, sessionuid):
        try:

            query = sql.SQL("""
                UPDATE task_queue
                SET fetched_on = NULL
                WHERE sessionuid = %s
            """)

            params = (sessionuid,)

            logger.debug("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
        except Exception:
            self.db.conn.rollback()
            logger.exception("!ERROR")
            raise
    # ____________________________

    def reset_taskmng_fetch(self, mng):
        return self.insert('taskmng_queue', mng)
    # ____________________________

    def update_session_task(self, taskid, task):
        """
        Fields to update:
         """
        fields = ['state', 'result', 'start', 'finish', 'total_elapsed_seconds', 'message', 'log']
        params = {k: task.get(k, None) for k in task if k in fields}
        logger.debug("XXX PARAMS: %r", params)
        try:
            query_template = "UPDATE session_task SET ({}) = %s WHERE id = {}"
            query = query_template.format(', '.join(params.keys()), taskid)
            params = (tuple(params.values()),)

            logger.debug("Mogrify: {}".format(self.db.cursor.mogrify(query, params)))
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
        except Exception:
            self.db.conn.rollback()
            logger.exception("!UPDATE SESSION TASK ERROR")
            raise
    # ____________________________
