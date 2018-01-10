#!/usr/bin/env bash

min_version="Python 3.5.3"
use_version=$( python3 --version )

to_array ()
{
  if [ $1 != "Python" ]; then
    echo "0 0 0"
  fi
  echo "$2" | tr -s '.' ' '
}

min_version_array=( $( to_array ${min_version} ) )
use_version_array=( $( to_array ${use_version} ) )

for i in 0 1 2
do
  min_ver=${min_version_array[${i}]}
  use_ver=${use_version_array[${i}]}
  if [ ${use_ver} -gt ${min_ver} ]; then
    exit 0
  fi
  if [ ${use_ver} -lt ${min_ver} ]; then
    echo "Python version must be grater than or equal to ${min_version}"
    exit 1
  fi
done

exit 0
