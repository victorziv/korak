#!/usr/bin/env python

import os
import pytest
import argparse
from webapp import create_app
from dba import DBAdmin
# __________________________________


def migratedb(app, version=None):
    DBAdmin.resetdb(app.config)
    DBAdmin.create_table_changelog(app.config)
    DBAdmin.upgradedb(app.config, version)
    DBAdmin.insert_initial_data(app)
# __________________________________


def parseargs():
    d = "Trigger one or more unittests"
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument(
        '-k', '--configkey', dest='configkey', default='testing',
        help="""Application type: testing, development, production. Default: testing""")

    parser.add_argument(
        '-t', '--testcase', dest='testcase', default='',
        help="""A module or a testcase""")

    return parser.parse_args()
# __________________________________


def main():
    """
    Example for literal string interpolation (f-string)
    """
    opts = parseargs()
    print("Configuration key: {}".format(opts.configkey))
    app = create_app(opts.configkey)
    migratedb(app)
    casepath = os.path.join(app.confg['BASEDIR'], 'tests', opts.testcase)
    pytest.main(['-x', '-v', casepath])

# __________________________________


if __name__ == '__main__':
    main()
