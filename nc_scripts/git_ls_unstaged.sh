#!/bin/bash
REMOTE=origin
for BRANCH in `git branch -r | grep origin | grep -v master | grep -v HEAD | sed -e 's/.*\///g'`
do
  echo git branch --track $BRANCH $REMOTE/$BRANCH
  git branch --track $BRANCH $REMOTE/$BRANCH
done
