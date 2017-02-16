#!/bin/sh

if [ $# -ne 2 ]
then
  echo "Usage: $0 <pattern> <replacement>" >&2
  exit 1
fi


for FILE in `find * -type f -exec grep -E -l -e "$1" {} \;`
do
  EXTENSION=`echo $FILE | sed -e 's/.*\(\.[^.]*\)$/\1/'`
  if [ "$EXTENSION" != ".doc" -a "$EXTENSION" != ".docx" ]
  then
    sed -i "" -e "s?$1?$2?g" $FILE
  fi
done
