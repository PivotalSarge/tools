#!/usr/bin/python

import os
import subprocess

def getRootDir():
    dir = os.getcwd()
    while dir and dir != "/":
        if os.path.exists(os.path.join(dir, ".git")):
            return dir
        dir = os.path.dirname(dir)
    return None

def getBuildDir(rootDir):
    if os.path.exists(os.path.join(rootDir, "CMakeCache.txt")):
        return rootDir
    for child in os.listdir(rootDir):
        childDir = os.path.join(rootDir, child)
        if os.path.exists(os.path.join(childDir, "CMakeCache.txt")):
            return childDir
    return None

gitRootDir = getRootDir()
if not gitRootDir:
    print("Unable to determine git root directory")
    exit(1)
buildDir = getBuildDir(gitRootDir)
if not buildDir:
    print("Unable to determine build directory")
    exit(1)
os.chdir(buildDir)

subprocess.call("ls")

exit(0)
