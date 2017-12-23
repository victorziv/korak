def create_table_machine(conn):

    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS machine (
            id serial PRIMARY KEY,
            sn BIGINT UNIQUE, -- machine serial number
            system_name VARCHAR(256) UNIQUE,
            model VARCHAR(16),
            approved BOOLEAN DEFAULT FALSE,
            approved_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_machine(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS machine;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_machine(conn)
# _______________________________


def downgrade(conn):
    drop_table_machine(conn)
