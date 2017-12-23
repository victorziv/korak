#!/usr/bin/env python

TASKS = [

    {
        'name': 'hwconfig',
        'display_name': 'HW Config',
        'description': 'Apply HW configuration fetched from Infinilab',
    },
    {
        'name': 'platform_install',
        'display_name': 'Platform Istallation',
        'description': 'Register in Infinilab and install OS and environment',
    },
    {
        'name': 'post_install_test',
        'display_name': 'Post Install Test',
        'description': '',
    },
    {
        'name': 'swinstall',
        'display_name': 'Infinibox Version Installation',
        'description': '',
    },
    {
        'name': 'hw_wizard',
        'display_name': 'HW Wizard',
        'description': '',
    },
    {
        'name': 'checkall',
        'display_name': 'Check All',
        'description': 'Checks all aspects',
    },
    {
        'name': 'fcloopback',
        'display_name': 'FC Loopback Test',
        'description': 'QLogic FC card diagnostic and verification',
    },
    {
        'name': 'test_system_drives',
        'display_name': 'System Drives Verification',
        'description': '',
    },
    {
        'name': 'eth_test',
        'display_name': 'Ethernet Cards Verification',
        'description': '',
    },
    {
        'name': 'mfg_test_suite',
        'display_name': 'MFG Test Suite',
        'description': 'Automatic tests on InfraDev infrastructure',
    },
    {
        'name': 'shipment',
        'display_name': 'Shipment Procedure',
        'description': 'Final verifications before shipment'
    },

]

# =================================


def insert_verification_tasks(conn):

    cursor = conn.cursor()
    task_keys = ['name', 'display_name', 'description']

    query = """
        INSERT INTO task
        ({}, {}, {})
        VALUES ( %s, %s, %s)
    """.format(*task_keys)

    for task in TASKS:
        params = [task[k] for k in task_keys]
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
# _____________________________


def create_table_task(conn):
    cursor = conn.cursor()

    query = """
        CREATE TABLE IF NOT EXISTS task (
            id serial PRIMARY KEY,
            name VARCHAR(64) UNIQUE,
            display_name VARCHAR(128),
            description TEXT
        );
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def drop_table_task(conn):
    cursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS task;
    """
    params = {}

    cursor.execute(query, params)
    conn.commit()
# _____________________________


def upgrade(conn, **kwargs):
    create_table_task(conn)
    insert_verification_tasks(conn)
# _______________________________


def downgrade(conn):
    drop_table_task(conn)
