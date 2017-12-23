def create_table_machine(conn):

    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS machine (
            id serial PRIMARY KEY,
            sn BIGINT UNIQUE, -- machine serial number
            system_name VARCHAR(256) UNIQUE,
            model VARCHAR(16),
            enclosure_drives VARCHAR(128),
            ssd_count VARCHAR(32),
            pdu_conf VARCHAR(64),
            power_cable VARCHAR(64),
            socket_location VARCHAR(256),
            daughter_card VARCHAR(64),
            infinibox_ga_version VARCHAR(16),
            ticket VARCHAR(32) UNIQUE,
            opened_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
            approved_by_ivt BOOLEAN DEFAULT NULL,
            approved_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
            customerid BIGINT REFERENCES customer(id) ON DELETE CASCADE
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
