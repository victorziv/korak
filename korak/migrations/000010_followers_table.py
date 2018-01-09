def create_table_followers(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS followers (
            followerid BIGINT REFERENCES users(id),
            followedid BIGINT REFERENCES users(id)
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_followers(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS followers;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_followers(conn)
# _______________________________


def downgrade(conn):
    drop_table_followers(conn)
