#!/usr/bin/env python


def create_table_task_params(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS task_params (
            taskqueueid INTEGER REFERENCES task_queue(id),
            params jsonb,
            PRIMARY KEY (taskqueueid)
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_task_params(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS task_params;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_task_params(conn)
# _______________________________


def downgrade(conn):
    drop_table_task_params(conn)
