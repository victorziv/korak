#!/usr/bin/env python


def create_table_task_queue(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS task_queue (
            id serial PRIMARY KEY,
            sessionuid VARCHAR(128) UNIQUE,
            sessiontaskid INTEGER REFERENCES session_task(id),
            taskname VARCHAR(128),
            worker VARCHAR(32),
            scheduled_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
            fetched_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_task_queue(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS task_queue;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_task_queue(conn)
# _______________________________


def downgrade(conn):
    drop_table_task_queue(conn)
