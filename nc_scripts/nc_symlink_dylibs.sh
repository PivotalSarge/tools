#!/bin/sh

if [ $# -ne 1 ]
then
  echo "Usage: $0 <executable>" >&2
  exit 1
fi

DIR=`pwd`
while [ $DIR != "/" -a ! -d $DIR/.git ]
do
  DIR=`dirname $DIR`
done
if [ $DIR = "/" ]
then
  echo "Unable to find git root" >&2
  exit 2
fi

TAB=$'\t'
for LIB in `otool -L $1 | grep -E '^\t[^/]' | sed -e "s/^${TAB}\(lib[^ ]*\) .*/\1/"`
do
  if [ ! -e $LIB ]
  then
    SRC=`find $DIR -type f -name "$LIB" -print | fgrep -v _CPack_Packages`
    if [ -n "$SRC" ]
    then
      ln -s $SRC $LIB
      ls -l $LIB
    fi
  fi
done
