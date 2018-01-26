#!/bin/bash

git branch -d $1
git push PivotalSarge --delete $1

