#!/bin/bash
PROJECT=${PROJECT_NAME:-korak}
CONFIG_KEY=${PROJECT_CONFIG:-develop}
curdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=$(dirname ${curdir})

python ${ROOTDIR}/${PROJECT}/manage.py dbreset --configkey=${CONFIG_KEY}
python ${ROOTDIR}/${PROJECT}/manage.py dbupgrade --configkey=${CONFIG_KEY}
