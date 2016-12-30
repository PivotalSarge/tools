#!/usr/bin/python

import argparse
import os
import platform
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
parser.add_argument('--generator', dest='generator', help='generator')
parser.add_argument('--install', dest='install_prefix', default='', help='install prefix')
args = parser.parse_args()

gemfire_home=os.environ.get('GEMFIRE_HOME')
if not gemfire_home:
	if platform.system() == 'Windows':
		gemfire_home = 'C:\\gemfire'
	else:
		gemfire_home = '/gemfire'

gemfire_version=os.environ.get('GEMFIRE_VERSION')
if not gemfire_version:
    gemfire_version = '0.0.42-build.000'

if not args.targets:
    if not args.generator and not args.install_prefix:
        targets = ['build']
    else:
        targets = ['generate']
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
        if not args.generator:
            if platform.system() == 'Windows':
                args.generator = '"Visual Studio 12 2013 Win64"'
            elif platform.system() == 'Darwin':
                args.generator = 'Xcode'
        command = 'cmake'
        if args.generator:
            command += ' -G ' + args.generator
        if gemfire_home:
            command += ' -DGEMFIRE_HOME=' + gemfire_home
        if gemfire_version:
            command += ' -DGEMFIRE_VERSION=' + gemfire_version
        if args.build_type:
            command += ' -DCMAKE_BUILD_TYPE=' + args.build_type
        if args.install_prefix:
            command += ' -DCMAKE_INSTALL_PREFIX=' + args.install_prefix
        command += ' ' + srcDir
    elif target == 'build':
        os.chdir(buildDir)
        command = 'cmake --build . --config ' + args.build_type
        if os.name == 'nt':
            command += ' -- /m /v:m'
        else:
            command += ' -- -j 8'
    elif target == 'unit':
        if os.path.isdir(os.path.join(buildDir, 'cppcache', 'test', args.build_type)):
            os.chdir(os.path.join(buildDir, 'cppcache', 'test', args.build_type))
        else:
            os.chdir(os.path.join(buildDir, 'cppcache', 'test'))
        if os.name == 'nt':
            command = 'gfcppcache_unittests.bat'
        else:
            command = 'bash gfcppcache_unittests.sh'
    elif target == 'quick':
        os.chdir(os.path.join(buildDir, 'cppcache', 'integration-test'))
        command = 'ctest -C ' + args.build_type + ' -L QUICK'
    elif target == 'stable':
        os.chdir(os.path.join(buildDir, 'cppcache', 'integration-test'))
        command = 'ctest -C ' + args.build_type + ' -L STABLE'
    else:
        os.chdir(buildDir)
        command = 'cmake --build . --config ' + args.build_type + ' --target ' + target
    print command
    subprocess.call(command, shell=True)

exit(0)
