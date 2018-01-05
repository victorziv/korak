def create_table_role(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS role (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            isdefault BOOLEAN DEFAULT FALSE,
            permissions INTEGER
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def create_table_user(conn):

    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            social_id VARCHAR(64),
            username VARCHAR(32) NOT NULL UNIQUE,
            name VARCHAR(64),
            given_name VARCHAR(32),
            family_name VARCHAR(32),
            picture VARCHAR(128),
            role_id INTEGER REFERENCES role(id),
            email VARCHAR(64) CONSTRAINT infinidat_email CHECK (email ~* '^[A-Za-z0-9._%%-]+@infinidat.com$')
        );
    """

    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_role(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS role;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_user(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS users;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_role(conn)
    create_table_user(conn)
# _______________________________


def downgrade(conn):
    drop_table_user(conn)
    drop_table_role(conn)
