#! /bin/bash
# Shared by Bruce Schuchardt
##
BTFILE=${1:-tests.bt}
################################################################################
# edit this section as desired to choose
#   1) java version
#   2) checkout directory
#   3) an open or closed build
buildRoot=$(dirname $($(dirname $0)/geode_root.py))
# choose to run open or closed
# open
#buildType=open
#GEMFIRE=$buildRoot/$buildType/gemfire-assembly/build/install/gemfire
# closed
buildType=closed
GEMFIRE=$buildRoot/$buildType/pivotalgf-assembly/build/install/pivotal-gemfire
################################################################################
PATH=$JAVA_HOME/bin:$PATH
JTESTS=$buildRoot/closed/gemfire-test/build/resources/test
rm -f batterytest.log
CLASSPATH=$GEMFIRE/lib/geode-dependencies.jar:\
$GEMFIRE/lib/gfsh-dependencies.jar:\
$JTESTS:$JTESTS/../../classes/hydraClasses:\
$JTESTS/../extraJars/groovy-all-2.4.3.jar:\
$JTESTS/../extraJars/rest-client-dependencies.jar:\
$buildRoot/closed/gemfire-test/build/classes/test:\
$buildRoot/open/geode-test/build/classes/main:\
$buildRoot/open/geode-core/build/classes/test
if [ x"$WINDIR" != x ]; then
  CLASSPATH=`cygpath -mp $CLASSPATH`
fi
#echo $JAVA_HOME
#echo $GEMFIRE
#echo $JTESTS
#echo $CLASSPATH
#REMOVE_PASSES="-DremovePassedTest=true"
OLD_RELEASE_DIR="-DRELEASE_DIR=/export/gcm/where/gemfire/releases"

set -x
java -server -d64 \
  -cp $CLASSPATH \
  -DprovideBugReportTemplate=true -DprovideRegressionSummary=true \
  -DnukeHungTest=true -DJTESTS=$JTESTS -DGEMFIRE=$GEMFIRE \
  $REMOVE_PASSES \
  $OLD_RELEASE_DIR \
  -DtestFileName=$BTFILE -DnumTimesToRun=1 \
  batterytest.BatteryTest
set +x
echo "checking oneliner.txt"
if [ -r oneliner.txt ]; then
  grep " F " oneliner.txt
  grep " H " oneliner.txt
else
  echo "could not locate oneliner.txt in $PWD"
  ls
fi

