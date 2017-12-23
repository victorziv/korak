def create_table_comment(conn):

    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS comment (
            id serial PRIMARY KEY,
            sessionid INTEGER REFERENCES session(id),
            commented_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
            comment TEXT
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_comments(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS comment;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_comment(conn)
# _______________________________


def downgrade(conn):
    drop_table_comments(conn)
