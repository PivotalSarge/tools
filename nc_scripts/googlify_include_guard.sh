#!/bin/sh

while [ $# -gt 0 ]
do
  OLD_GUARD=`egrep '#ifndef[ \t]+APACHE_GEODE_GUARD_[0-9a-f]+' $1 | sed -e 's/.*\(APACHE_GEODE_GUARD_[0-9a-f]*\).*/\1/'`
  NEW_GUARD="GEODE_`echo $1 | sed -e 's?^src/?? ; s?^tests/cpp/?? ; s?/?_?g ; s?\.[^.]*$?_H_?' | tr '[a-z]' '[A-Z]'`"
  sed -i "" -e "s/$OLD_GUARD/$NEW_GUARD/g" $1
  shift
done
