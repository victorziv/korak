def create_table_suite_testcase(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS suite_testcase (
            suiteid INTEGER REFERENCES suite(id),
            testcaseid INTEGER REFERENCES testcase(id),
            PRIMARY KEY (suiteid, testcaseid)
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_suite_testcase(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS suite_testcase;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_suite_testcase(conn)
# _______________________________


def downgrade(conn):
    drop_table_suite_testcase(conn)
