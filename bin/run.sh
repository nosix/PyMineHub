#!/usr/bin/env bash

BASEDIR=$(dirname "$0")/..

${BASEDIR}/bin/checkver.sh || exit 1

export PYTHONPATH=${PYTHONPATH}:${BASEDIR}/src

python3 ${BASEDIR}/src/pyminehub/mcpe/main/server.py

exit 0
