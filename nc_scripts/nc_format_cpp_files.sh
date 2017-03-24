#!/bin/sh

if [ $# -lt 1 ]
then
  echo "Usage: $0 <file...>" >&2
  exit 1
fi

while [ 0 -lt $# ]
do
  echo "Formatting ${1}"
  clang-format -i -style=file -fallback-style=Google ${1}
  shift
done
