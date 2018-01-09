def create_table_posts(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS posts (
            id BIGSERIAL PRIMARY KEY,
            body TEXT,
            created TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
            userid INTEGER REFERENCES users(id)
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_posts(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS posts;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_posts(conn)
# _______________________________


def downgrade(conn):
    drop_table_posts(conn)
