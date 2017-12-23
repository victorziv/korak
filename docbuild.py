#!/usr/bin/env python
import os
import sys

CURDIR = os.path.dirname(os.path.abspath(__file__))
ROOTDIR = '/opt/infinidat'
DOCDIR = os.path.join(ROOTDIR, "ivtdoc", "ivt_test")
# _________________________


def build_doc():
    if not os.path.exists(DOCDIR):
        os.makedirs(DOCDIR)
    os.system("sphinx-build -aEv -b html {}/doc {}/".format(CURDIR, DOCDIR))
# _________________________


def check_virtualenv():
    errmsg = "Must be running from within Python 3.5+ virtualenv - aborting"
    try:
        if sys.prefix == sys.base_prefix == '/usr':
            print("sys.base_prefix: {}".format(sys.base_prefix))
            print(errmsg)
            sys.exit(1)
    except AttributeError:
        print(errmsg)
        sys.exit(1)
# _________________________


def set_config():
    from slash.site import load
    load('{}/.slashrc'.format(CURDIR))
# _________________________


def main():
    check_virtualenv()
    os.chdir(CURDIR)
    print("Working directory: {}".format(os.getcwd()))
    set_config()
    build_doc()
# _________________________


if __name__ == '__main__':
    main()
