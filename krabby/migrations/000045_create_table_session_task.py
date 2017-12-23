def create_table_session_task(conn):
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS session_task (
            id serial PRIMARY KEY,
            taskuid VARCHAR(128) UNIQUE,
            sessionid INTEGER REFERENCES session(id),
            taskmapid INTEGER REFERENCES type_task_map(id),
            state VARCHAR(16),
            result BOOLEAN DEFAULT NULL,
            start TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
            finish TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
            total_elapsed_seconds BIGINT,
            message VARCHAR(256) DEFAULT NULL,
            log VARCHAR(256) DEFAULT NULL
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_session_task(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS session_task;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_session_task(conn)
# _______________________________


def downgrade(conn):
    drop_table_session_task(conn)
