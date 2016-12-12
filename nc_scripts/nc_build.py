#!/usr/bin/python

import argparse
import os
import subprocess

def getRootDir():
    dir = os.getcwd()
    while dir and dir != '/':
        if os.path.exists(os.path.join(dir, '.git')):
            return dir
        dir = os.path.dirname(dir)
    return None

def getBuildDir(rootDir):
    if os.path.exists(os.path.join(rootDir, 'CMakeCache.txt')):
        return rootDir
    for child in os.listdir(rootDir):
        childDir = os.path.join(rootDir, child)
        if os.path.exists(os.path.join(childDir, 'CMakeCache.txt')):
            return childDir
    if os.path.exists(os.path.join(rootDir, 'build')):
        return os.path.join(rootDir, 'build')
    return None

gitRootDir = getRootDir()
if not gitRootDir:
    print('Unable to determine git root directory')
    exit(1)
srcDir = os.path.join(gitRootDir, 'src')
buildDir = getBuildDir(gitRootDir)
if not buildDir:
    print('Unable to determine build directory')
    exit(1)

parser = argparse.ArgumentParser(description='Build the native client.')
parser.add_argument('targets', metavar='target', nargs='*', help='target to build')
parser.add_argument('--config', dest='build_type', default='Debug', help='build type')
parser.add_argument('--install', dest='install_prefix', default='', help='build type')
args = parser.parse_args()

install_prefix = args.install_prefix
if not install_prefix:
	if os.name == 'nt':
		install_prefix = 'C:\\tmp'
	else:
		install_prefix = '/tmp'

gemfire_home=os.environ.get('GEMFIRE_HOME')
if not gemfire_home:
	if os.name == 'nt':
		gemfire_home = 'C:\\gemfire'
	else:
		gemfire_home = '/gemfire'

gemfire_version=os.environ.get('GEMFIRE_VERSION')
if not gemfire_version:
    gemfire_version = '0.0.42-build.000'

if not args.targets:
    targets = ['build']
else:
    targets = []
    for target in args.targets:
        if target == 'unit':
            targets.extend(['build', 'unit'])
        elif target == 'quick':
            targets.extend(['build', 'unit', 'quick'])
        elif target == 'stable':
            targets.extend(['build', 'unit', 'stable'])
        elif target == 'docs':
            targets.extend(['build', 'unit', 'quick', 'docs'])
        elif target == 'install':
            targets.extend(['build', 'unit', 'quick', 'docs', 'install'])
        elif target == 'all':
            targets.extend(['build', 'unit', 'quick', 'docs', 'install', 'package'])
        else:
            targets.append(target)

for target in targets:
    if target == 'configure' or target == 'generate':
        os.chdir(buildDir)
        if os.name == 'nt':
			command = 'cmake -G"Visual Studio 12 2013 Win64" -DGEMFIRE_HOME=%s -DGEMFIRE_VERSION=%s -DCMAKE_BUILD_TYPE=%s -DCMAKE_INSTALL_PREFIX=%s %s' %\
					  (gemfire_home, gemfire_version, args.build_type, install_prefix, srcDir)
        else:
			command = 'cmake -DGEMFIRE_HOME=%s -DGEMFIRE_VERSION=%s -DCMAKE_BUILD_TYPE=%s -DCMAKE_INSTALL_PREFIX=%s %s' %\
					  (gemfire_home, gemfire_version, args.build_type, install_prefix, srcDir)
    elif target == 'build':
        os.chdir(buildDir)
        if os.name == 'nt':
            command = 'cmake --build . --config %s -- /m /v:m' % args.build_type
        else:
            command = 'cmake --build . --config %s -- -j 8' % args.build_type
    elif target == 'unit':
        os.chdir(os.path.join(os.path.join(buildDir, 'cppcache'), 'test'))
        if os.name == 'nt':
            command = 'gfcppcache_unittets.bat'
        else:
            command = 'bash gfcppcache_unittests.sh'
    elif target == 'quick':
        os.chdir(os.path.join(os.path.join(buildDir, 'cppcache'), 'integration-test'))
        command = 'ctest -C %s -L QUICK' % args.build_type
    elif target == 'stable':
        os.chdir(os.path.join(os.path.join(buildDir, 'cppcache'), 'integration-test'))
        command = 'ctest -C %s -L STABLE' % args.build_type
    else:
        os.chdir(buildDir)
        command = 'cmake --build . --config %s --target %s' % (args.build_type, target)
    print command
    subprocess.call(command, shell=True)

exit(0)
