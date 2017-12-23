mapping = {

    'BLACK_IVT': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'shipment',
    ],

    'RPQ2': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'shipment',
    ],
    'RPQ3': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'eth-test',
        'shipment',
    ],

    'RPQ4': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'eth-test',
        'checkall',
        'shipment',
    ],
    'RPQ5': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'test_system_drives',
        'eth-test',
        'mfg_test_suite',
        'checkall',
        'shipment',
    ],

    'RPQ9': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'test_system_drives',
        'eth-test',
        ('mfg_test_suite', 3),
        'checkall',
        'shipment',
    ],

    'NONRPQ': [
        'hwconfig',
        'platform_install',
        'post_install_test',
        'swinstall',
        'hw_wizard',
        'checkall',
        'fcloopback',
        'test_system_drives',
        'eth-test',
        ('mfg_test_suite', 5),
        'checkall',
        'shipment',
    ]
}
# =========================================


def insert_mapping(conn):
    cursor = conn.cursor()

    query = """
        INSERT INTO type_task_map
        (typeid, taskid, loop, execution_order)
        VALUES(
            ( SELECT id from verification_type WHERE name = %s),
            ( SELECT id from task WHERE name = %s),
            %s,
            %s
        )
    """

    for vertype, arr in mapping.items():
        for ind, val in enumerate(arr):
            params = [vertype]

            if type(val).__name__ == 'tuple':
                params.extend(val)
            else:
                params.extend([val, 1])

            params.append(ind + 1)
            cursor.execute(query, params)
            conn.commit()
# ___________________________________


def create_table_type_task_map(conn):
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS type_task_map (
            id serial PRIMARY KEY,
            typeid INTEGER REFERENCES verification_type(id),
            taskid INTEGER REFERENCES task(id),
            loop INTEGER DEFAULT 1,
            execution_order INTEGER
        );
    """
    params = []

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_type_task_map(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS type_task_map;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_type_task_map(conn)
    insert_mapping(conn)
# _______________________________


def downgrade(conn):
    drop_table_type_task_map(conn)
