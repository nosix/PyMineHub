#!/usr/bin/env bash

usage ()
{
  CMD_NAME=`basename $0`
  echo "Usage: $CMD_NAME command"
  echo "  command:"
  echo "      deploy - Copy PyMineHub to Raspberry Pi Zero connected via USB"
  echo "      run    - Run PyMineHub server on Raspberry Pi Zero"
  echo "      test   - Run test on Raspberry Pi Zero"
  exit 1
}

REMOTE_HOME='~/PyMineHub'

if [ $# -ne 1 ]; then
  usage
fi

if [ $1 = "deploy" ]; then
  scp -r . pi@raspberrypi.local:${REMOTE_HOME}
  exit 0
fi

if [ $1 = "run" ]; then
  # run remote PyMineHub server
  ssh pi@raspberrypi.local ${REMOTE_HOME}/bin/run.sh &

  # run local PyMineHub proxy server
  BASEDIR=$(dirname "$0")/..
  export PYTHONPATH=${PYTHONPATH}:${BASEDIR}/src
  python3 ${BASEDIR}/tool/tool/proxy.py &

  wait

  exit 0
fi

if [ $1 = "test" ]; then
  ssh pi@raspberrypi.local ${REMOTE_HOME}/bin/test.sh
  exit 0
fi

usage
exit 1
