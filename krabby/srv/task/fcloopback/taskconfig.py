import os
BASEDIR = os.path.dirname(os.path.abspath(__file__))

configuration = {

    "BASEDIR": BASEDIR,
    "LOGPATH": os.path.join(BASEDIR, 'logs'),

    "dr_hostnames": ["infiniconf", "centos7-mini", "infiniconf2"],
    "ibox_services": ["core", "mgmt2", "quotad", "drivemon", "dsm_sa_datamgrd", "dsm_sa_eventmgrd"],
    "timeout_node_state": 10 * 60,
    "timeout_node_start": 10 * 60,
    "timeout_services_start": 5 * 60,

    "loopback_ports": [
        'N1FC1', 'N1FC2', 'N1FC3', 'N1FC4', 'N1FC5', 'N1FC6', 'N1FC7',
        'N2FC1', 'N2FC2', 'N2FC3', 'N2FC4', 'N2FC5', 'N2FC6', 'N2FC7',
        'N3FC1', 'N3FC2', 'N3FC3', 'N3FC4', 'N3FC5', 'N3FC6', 'N3FC7'
    ],

    "tools_path": os.path.join(BASEDIR, 'tools'),

    "tools": {
        "qlogic_converge_console_cli": "QConvergeConsoleCLI-1.1.04-65.x86_64.rpm",
    },

    "loopback_test": {

        "long": {
            'data_patterns': ['\t00', '\t55', '\t5A', '\tA5', '\tAA', '\tFF', 'RANDOM', ' CRPAT', ' CSPAT', 'CJTPAT'],
            'data_sizes': [8, 16, 32, 64, 128, 256, 512, 1024, 2048],
            'test_count': 1024,
        },
        "medium": {
            'data_patterns': ['\t00', '\t5A', '\tAA', 'RANDOM', ' CRPAT', 'CJTPAT'],
            'data_sizes': [8, 32, 128, 512, 2048],
            'test_count': 512,
        },

        "short": {
            'data_patterns': ['\t00'],
            'data_sizes': [8],
            'test_count': 128,
        }
    },

    "external_loopback": {
        'type': 2,
    },

    "internal_loopback_bit1": {
        'type': 1,
    },

    "isp": {
        "supported": {

            "part_number": "PX4810402-01",
            "pci_key": "1077:2532",
            "revisions": ['J', 'K', 'L', 'M']
        },
        "pci_locations": {
            "R720": {
                frozenset(['44:00.0', '44:00.1', '45:00.0', '45:00.1']): "Slot 4 (Upper)",
                frozenset(['05:00.0', '05:00.1', '06:00.0', '06:00.1']): "Slot 5 (Lower)"
            },

            "R730": {
                frozenset(['84:00.0', '84:00.1', '85:00.0', '85:00.1']): "Slot 4 (Upper)",
                frozenset(['06:00.0', '06:00.1', '07:00.0', '07:00.1']): "Slot 5 (Lower)",

            }
        }

    },

    "sfp": {

        "supported": {
            'FTLF8528P3BCV-QL': ['A'],
            'FTLF8528P3BCV': ['A']
        },
    },

    # defaults - might be overriden via web interface

    "test_length": "short",
    "run_hwstatus": True,
    "cleanup": True,
    "verbose": False,
    "system_up_check": True,
    "nodes_filter": None
}
