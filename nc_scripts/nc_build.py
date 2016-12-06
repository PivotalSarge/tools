#!/usr/bin/python

import argparse
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
    if os.path.exists(os.path.join(rootDir, "build")):
        return os.path.join(rootDir, "build")
    return None

gitRootDir = getRootDir()
if not gitRootDir:
    print("Unable to determine git root directory")
    exit(1)
srcDir = os.path.join(gitRootDir, 'src')
buildDir = getBuildDir(gitRootDir)
if not buildDir:
    print("Unable to determine build directory")
    exit(1)
os.chdir(buildDir)

parser = argparse.ArgumentParser(description='Build the native client.')
parser.add_argument('targets', metavar='target', nargs='*', help='target to build')
parser.add_argument('--config', dest='build_type', default='Debug', help='build type')
parser.add_argument('--install', dest='install_prefix', default='/tmp', help='build type')
args = parser.parse_args()

gemfire_home=os.environ.get('GEMFIRE_HOME')
if not gemfire_home:
    gemfire_home = '/gemfire'

targets = args.targets
if not targets:
    targets.extend(['build'])
for target in targets:
    if target == 'configure' or target == 'generate':
        command = 'cmake -DGEMFIRE_HOME=%s -DCMAKE_BUILD_TYPE=%s -DCMAKE_INSTALL_PREFIX=%s %s' % (gemfire_home, args.build_type, args.install_prefix, srcDir)
    elif target == 'build':
        command = 'cmake --build . --config %s -- -j 8' % args.build_type
    else:
        command = 'cmake --build . --config %s --target %s' % (args.build_type, target)
    print command
    subprocess.call(command, shell=True)

exit(0)
