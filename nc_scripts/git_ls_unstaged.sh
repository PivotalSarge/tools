#!/bin/bash

git status -u | grep -E -e '[	 ]modified:[	 ]' | sed -e 's/.*modified:[^/a-z]*//'
