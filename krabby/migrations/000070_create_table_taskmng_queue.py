#!/usr/bin/env python


def create_table_taskmng_queue(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS taskmng_queue (
            sessionuid VARCHAR(128) UNIQUE,
            sessiontaskid INTEGER REFERENCES session_task(id),
            taskname VARCHAR(128),
            action VARCHAR(16),
            scheduled_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_taskmng_queue(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS taskmng_queue;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_taskmng_queue(conn)
# _______________________________


def downgrade(conn):
    drop_table_taskmng_queue(conn)
