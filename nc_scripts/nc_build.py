#!/usr/bin/python

import os

def getRoot():
    dir = os.getcwd()
    while dir and dir != "/":
        if os.path.exists(os.path.join(dir, ".git")):
            return dir
        dir = os.path.dirname(dir)
    return None

gitRoot = getRoot()
if gitRoot:
    print("gitRoot=" + gitRoot)

exit(37)
