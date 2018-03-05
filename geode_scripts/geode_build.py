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
        if os.path.exists(os.path.join(dir, 'gradlew')):
            return dir
        if os.path.exists(os.path.join(dir, '.git')):
            return dir
        dir = os.path.dirname(dir)
    return None

def getGradleWrapper(dir):
    path = os.path.join(dir, 'gradlew')
    if os.path.isfile(path):
        return path
    path = os.path.join(os.path.join(dir, 'closed'), 'gradlew')
    if os.path.isfile(path):
        return path
    return None

gitRootDir = getRootDir()
if not gitRootDir:
    print('Unable to determine git root directory')
    exit(1)
closed = None
if (os.path.basename(gitRootDir) == 'gemfire' or os.path.basename(gitRootDir) == 'closed'):
    closed = True

parser = argparse.ArgumentParser(description='Build Geode.')
parser.add_argument('targets', metavar='target', nargs='*', help='target to build')
args = parser.parse_args()

flags = ['--parallel']
if not args.targets:
    targets = ['build']
else:
    targets = []
    for target in args.targets:
        #./gradlew build -x :geode-old-versions:compileJava -x :geode-old-versions:verifyGeodetest120 -x :geode-old-versions:downloadZipFiletest120 -x :geode-old-versions:downloadAndUnzipFiletest120
        if target == 'quick':
            flags.extend(['-x', 'javadoc', '-x', 'rat', '-x', 'spotlessApply', '-Dskip.tests=true'])
            if (closed):
                targets.extend(['build'])
            else:
                targets.extend(['assemble', 'installDist', 'testClasses'])
        else:
           targets.append(target)

if 'build' in targets:
    if (not closed):
        if 'spotlessApply' not in targets:
            targets.insert(0, 'spotlessApply')

command = getGradleWrapper(gitRootDir)
for target in targets:
    for flag in flags:
        command += ' ' + flag
    command += ' ' + target

print command
rc = subprocess.call(command, shell=True)
if 0 != rc:
    exit(rc)

exit(0)
