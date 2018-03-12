#!/bin/bash

while [ 0 -lt $# ]
do
  git branch -D $1
  git push PivotalSarge --delete $1
  shift
done
