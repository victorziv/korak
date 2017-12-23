def create_table_suite(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS suite (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            description TEXT
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_suite(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS suite;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_suite(conn)
# _______________________________


def downgrade(conn):
    drop_table_suite(conn)
