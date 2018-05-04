#!/usr/bin/python

import platform
import os

dir = os.getcwd()
while dir and dir != '/':
  if os.path.exists(os.path.join(dir, 'gradlew')):
    print dir
    exit(0)
  if os.path.exists(os.path.join(dir, '.git')):
    print dir
    exit(0)
  dir = os.path.dirname(dir)

exit(1)
