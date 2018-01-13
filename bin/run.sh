#!/usr/bin/env bash

usage ()
{
  CMD_NAME=`basename $0`
  echo "Usage: $CMD_NAME [-p] [-d]"
  exit 1
}

PROFILER=

while getopts dhp OPT
do
    case ${OPT} in
        p)  PROFILER="-m cProfile -o run.pstat"
            ;;
        d)  export PMH_PLUGIN_ROOT=""
            ;;
        h)  usage
            ;;
    esac
done

BASEDIR=$(dirname "$0")/..

${BASEDIR}/bin/checkver.sh || exit 1

export PYTHONPATH=${PYTHONPATH}:${BASEDIR}/src

python3 ${PROFILER} ${BASEDIR}/src/pyminehub/mcpe/main/server.py

exit 0
