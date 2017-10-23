#!/usr/bin/python

import argparse
import platform
import re
import os
import subprocess

def which(basename):
    if platform.system() == 'Windows':
        separator = ';'
    else:
        separator = ':'
    for dir in os.environ['PATH'].split(separator):
        executable = os.path.join(dir, basename)
        if os.path.exists(executable) and os.access(executable, os.X_OK):
            return executable
    return ''

def getTempDir():
    dir = None
    if platform.system() == 'Windows':
        dir = 'C:\\temp'
    else:
        dir = '/tmp'
    if os.path.exists(dir) and os.path.isdir(dir):
        return dir
    return None

def getRootDir():
    dir = os.getcwd()
    while dir and dir != '/':
        if os.path.exists(os.path.join(dir, '.git')):
            return dir
        dir = os.path.dirname(dir)
    return None

gitRootDir = getRootDir()
if not gitRootDir:
    print('Unable to determine git root directory')
    exit(1)

parser = argparse.ArgumentParser(description='Build the native client.')
parser.add_argument('targets', metavar='target', nargs='*', help='target to build')
args = parser.parse_args()

flags = []
if not args.targets:
    targets = ['build']
else:
    targets = []
    for target in args.targets:
        #./gradlew build -x :geode-old-versions:compileJava -x :geode-old-versions:verifyGeodetest120 -x :geode-old-versions:downloadZipFiletest120 -x :geode-old-versions:downloadAndUnzipFiletest120
        if target == 'quick':
            flags.extend(['-x', 'javadoc', '-x', 'rat', '-x', 'spotlessApply', '-Dskip.tests=true'])
            targets.extend(['assemble', 'installDist', 'testClasses'])
        else:
           targets.append(target)

for target in targets:
    command = gitRootDir + '/gradlew'
    for flag in flags:
        command += ' ' + flag
    for target in targets:
        command += ' ' + target
    print command
    rc = subprocess.call(command, shell=True)
    if 0 != rc:
        exit(rc)

exit(0)