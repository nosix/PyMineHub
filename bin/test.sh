#!/usr/bin/env bash

BASEDIR=$(dirname "$0")/..

${BASEDIR}/bin/checkver.sh || exit 1

export PYTHONPATH=${PYTHONPATH}:${BASEDIR}/src:${BASEDIR}/tool:${BASEDIR}/test

python3 ${BASEDIR}/test/all.py

exit 0
