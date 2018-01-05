#!/bin/bash

PROJECT=korak
curdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=$(dirname ${curdir})

python ${ROOTDIR}/${PROJECT}/manage.py runserver
