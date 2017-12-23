def create_table_verification_type(conn):
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS verification_type (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            rundays INTEGER,
            priority INTEGER
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def insert_verification_types(conn):
    cursor = conn.cursor()

    query = """
        INSERT INTO verification_type
        (name, rundays, priority)
        VALUES(%s, %s, %s)
    """
    params = [
        ['BLACK_IVT', 1],
        ['NONRPQ', 13],
        ['RPQ2', 2],
        ['RPQ3', 3],
        ['RPQ4', 4],
        ['RPQ5', 5],
        ['RPQ9', 9],
    ]

    for ind, p in enumerate(params):
        p.append((ind + 1) * 10)
        cursor = conn.cursor()
        cursor.execute(query, p)
        conn.commit()
# ___________________________________


def drop_table_verification_type(conn):

    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS verification_type;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_verification_type(conn)
    insert_verification_types(conn)
# _______________________________


def downgrade(conn):
    drop_table_verification_type(conn)
