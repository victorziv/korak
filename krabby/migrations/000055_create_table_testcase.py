def create_table_testcase(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS testcase (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            category VARCHAR(64),
            author VARCHAR(64),
            owner VARCHAR(64),
            created TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
            checksum CHAR(32),
            description TEXT
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_testcase(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS testcase;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_testcase(conn)
# _______________________________


def downgrade(conn):
    drop_table_testcase(conn)
