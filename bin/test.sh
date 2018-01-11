#!/usr/bin/env bash

usage ()
{
  CMD_NAME=`basename $0`
  echo "Usage: $CMD_NAME [-p]"
  exit 1
}

PROFILER=

while getopts ph OPT
do
    case ${OPT} in
        p)  PROFILER="-m cProfile -o run.pstat"
            ;;
        h)  usage
            ;;
    esac
done

BASEDIR=$(dirname "$0")/..

${BASEDIR}/bin/checkver.sh || exit 1

export PYTHONPATH=${PYTHONPATH}:${BASEDIR}/src:${BASEDIR}/tool:${BASEDIR}/test

python3 ${PROFILER} ${BASEDIR}/test/all.py

exit 0
