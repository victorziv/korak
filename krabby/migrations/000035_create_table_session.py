
def create_table_session(conn):

    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS session (
            id serial PRIMARY KEY,
            uid VARCHAR(128) UNIQUE,
            sn BIGINT,
            system_name VARCHAR(256),
            model VARCHAR(32),
            shipment_ticket VARCHAR(32),
            customerid BIGINT REFERENCES customer(id),
            typeid INTEGER REFERENCES verification_type(id),
            ivtcycle INTEGER,
            slot INTEGER,
            ownerid INTEGER REFERENCES users(id),
            ticket VARCHAR(32),
            start TIMESTAMP WITHOUT TIME ZONE,
            finish TIMESTAMP WITHOUT TIME ZONE,
            due TIMESTAMP WITHOUT TIME ZONE,
            weekend_included BOOLEAN,
            created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            state VARCHAR(16),
            result BOOLEAN,
            approved_by_ivt BOOLEAN DEFAULT NULL,
            approved_on TIMESTAMP WITHOUT TIME ZONE
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_session(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS session;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_session(conn)
# _______________________________


def downgrade(conn):
    drop_table_session(conn)
