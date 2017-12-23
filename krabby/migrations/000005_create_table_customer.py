def create_table_customer(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS customer (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            hq VARCHAR(128),
            web VARCHAR(256)
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_customer(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS customer;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_customer(conn)
# _______________________________


def downgrade(conn):
    drop_table_customer(conn)
