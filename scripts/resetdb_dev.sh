#!/bin/bash
PROJECT = ${PROJECT_NAME:-krabby}
CONFIG_KEY = ${PROJECT_CONFIG:-development}
curdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=$(dirname ${curdir})

python ${ROOTDIR}/${PROJECT}/manage.py dbreset --configkey=${CONFIG_KEY}
python ${ROOTDIR}/${PROJECT}/manage.py dbupgrade --configkey=${CONFIG_KEY}
