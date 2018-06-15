#! /bin/bash

if [ -z "$GEODE_ROOT" ]
then
    echo "GEODE_ROOT is not set." >&2
    exit 1
fi

PATH=$JAVA_HOME/bin:$PATH
JTESTS=$GEODE_ROOT/closed/gemfire-test/build/resources/test
CLASSPATH=$GEMFIRE/lib/geode-dependencies.jar:\
$GEODE_ROOT/closed/pivotalgf-assembly/build/install/pivotal-gemfire/lib/gfsh-dependencies.jar:\
$JTESTS:$JTESTS/../../classes/hydraClasses:\
$JTESTS/../extraJars/groovy-all-2.4.3.jar:\
$JTESTS/../extraJars/rest-client-dependencies.jar:\
$GEODE_ROOT/closed/gemfire-test/build/classes/test:\
$GEODE_ROOT/open/geode-test/build/classes/main:\
$GEODE_ROOT/open/geode-core/build/classes/test

if [ $# -eq 0 ]
then
    set -x
    java -Xmx1500m -Xms750m -server \
      -cp $CLASSPATH \
      org.apache.geode.internal.logging.MergeLogFiles \
      `pwd`
    set +x
else
    set -x
    java -Xmx1500m -Xms750m -server \
      -cp $CLASSPATH \
      org.apache.geode.internal.logging.MergeLogFiles \
      $@
    set +x
fi

