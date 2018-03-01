#!/bin/sh

if [ ! -d geode-protobuf ]
then
  echo "$0 must be run from the root of a Geode checkout." >&2
  exit 1
fi

LOG_FILE=/tmp/`date '+%Y%m%d%H%M%S'`.txt
cat /dev/null >$LOG_FILE
if [ ! -f $LOG_FILE ]
then
  echo "Unable to create log file: $LOG_FILE" >&2
  exit 2
fi

OVERALL_SUCCESS=1
EXPECTED_SUCCESSES=1
for MATCH in `find geode-protobuf/src/test geode-protobuf-messages/src/test geode-experimental-driver/src/test \
    -type f -name '*.java' \
    -exec egrep -IH '@Category\(IntegrationTest|@Category\(DistributedTest' {} \; 2>/dev/null`
do
  TEST_FILE=`echo $MATCH | cut -d: -f1`
  CATEGORY=`echo $MATCH | cut -d: -f2 | sed -e 's?@Category(\([^.]*\)\.class)?\1? ; s?^D?d? ; s?^I?i?'`
  MODULE=`echo $TEST_FILE | cut -d/ -f1`
  TEST=`echo $TEST_FILE | sed -e 's?.*/\([^/.][^/.]*\)\(\.java\)?\1?'`
  printf "Running %.50s" "${TEST}........................................................."
  ./gradlew -D${CATEGORY}.single=$TEST ${MODULE}:${CATEGORY} >>$LOG_FILE 2>&1
  ACTUAL_SUCCESSES=`fgrep 'BUILD SUCC' $LOG_FILE | wc -l`
  if [ $ACTUAL_SUCCESSES -lt $EXPECTED_SUCCESSES ]
  then
    printf "FAIL\n"
    OVERALL_SUCCESS=0
  else
    printf "PASS\n"
    EXPECTED_SUCCESSES=`expr $EXPECTED_SUCCESSES + 1`
  fi
done

if [ $OVERALL_SUCCESS -ne 1 ]
then
  NEW_LOG_FILE=`pwd`/`basename $LOG_FILE`
  mv $LOG_FILE $NEW_LOG_FILE
  printf "Results: %s\n" $NEW_LOG_FILE
  exit 1
else
  rm $LOG_FILE
  exit 0
fi
