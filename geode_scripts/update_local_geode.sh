#!/bin/sh

GEODE_VERSION=1.5.0
GEODE_HOME=/apache-geode-$GEODE_VERSION
cp -p geode-assembly/build/install/apache-geode/lib/*.jar $GEODE_HOME/lib/

for SRC in `find g*/src/main -name *.java`
do
   DST=`echo $SRC | sed -e 's?[^/]*/src/main/java/??'`
   mkdir -p $GEODE_HOME/src/`dirname $DST`
   cp -p $SRC $GEODE_HOME/src/$DST
done
