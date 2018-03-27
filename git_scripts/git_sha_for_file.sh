#!/bin/bash

FILE=$1
SHAS=/tmp/$$
for SHA in `git log | egrep '^commit [0-9a-f]+' | sed 's/^commit //'`
do
  git show $SHA | fgrep "diff --git a/$FILE " >/dev/null 2>&1 && echo $SHA >> $SHAS
done

for SHA in `cat $SHAS`
do
  git show $SHA
done

rm -f $SHAS
