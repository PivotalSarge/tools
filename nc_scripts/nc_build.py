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

def getCmakeValue(path, propertyName):
    cacheFile = file(path)
    for line in cacheFile:
        m = re.match('\w*{0}=(.+)'.format(propertyName), line)
        if m:
            return m.group(1)
    return ''

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
parser.add_argument('--clang', dest='clang_directory', default='', help='clang directory')
parser.add_argument('--parallel-build', dest='parallel_build', default=True, help='whether to build in parallel')
parser.add_argument('--gemfire', action='store_true', default=False, help='whether to do a GemFire build')
args = parser.parse_args()

if not args.clang_directory:
    args.clang_directory = os.path.dirname(which('clang-format'))

geode_root=os.environ.get('GEODE_ROOT')
if not geode_root:
    if platform.system() == 'Windows':
        geode_root = 'C:\\gemfire'
        if not os.path.exists(geode_root) or not os.path.isdir(geode_root):
            geode_root = 'C:\\geode'
    else:
        geode_root = '/gemfire'
        if not os.path.exists(geode_root) or not os.path.isdir(geode_root):
            geode_root = '/geode'

product_version=os.environ.get('PRODUCT_VERSION')
if not product_version:
    product_version = '0.0.42-build.000'

if not args.targets:
    if not args.generator and not args.install_prefix:
        if os.path.exists(os.path.join(buildDir, 'CMakeCache.txt')):
            targets = ['build']
        else:
            targets = ['generate', 'build']
    else:
        targets = ['generate']

    if not args.install_prefix:
        tempDir = getTempDir()
        if tempDir:
            installDir = os.path.join(tempDir, 'install')
            if os.path.exists(installDir) and os.path.isdir(installDir):
                args.install_prefix = installDir
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
                args.generator = 'Visual Studio 12 2013 Win64'
            elif platform.system() == 'Darwin':
                args.generator = 'Xcode'
        if not os.path.exists(args.install_prefix):
            os.makedirs(args.install_prefix)

        command = 'cmake'
        if args.generator:
            command += ' -G "' + args.generator + '"'
        if geode_root:
            command += ' -DGEODE_ROOT=' + geode_root
        if product_version:
            command += ' -DPRODUCT_VERSION=' + product_version
        if args.build_type:
            command += ' -DCMAKE_BUILD_TYPE=' + args.build_type
        if args.install_prefix:
            command += ' -DCMAKE_INSTALL_PREFIX=' + args.install_prefix
        if args.clang_directory:
            command += ' -DCLANG_FORMAT=' + os.path.join(args.clang_directory, 'clang-format')
            command += ' -DCLANG_TIDY=' + os.path.join(args.clang_directory, 'clang-tidy')
            command += ' -DENABLE_CLANG_TIDY=ON'
        if args.gemfire:
            command += ' -DPRODUCT_LIB_NAME=pivotal-gemfire'
            command += ' -DPRODUCT_PACKAGE_NAME=pivotal-gemfire-native'
            command += ' -DPRODUCT_DLL_NAME=Pivotal.Gemfire'
        command += ' ' + srcDir
    elif target == 'build':
        os.chdir(buildDir)
        command = 'cmake --build . --config ' + args.build_type
        generator = getCmakeValue(os.path.join(buildDir, 'CMakeCache.txt'), 'CMAKE_GENERATOR:INTERNAL')
        if args.parallel_build:
            if 'Visual Studio' in generator:
                command += ' -- /m /v:m'
            elif 'Xcode' not in generator:
                command += ' -- -j 8'
    elif target == 'unit':
        os.chdir(os.path.join(buildDir, 'cppcache', 'test'))
        command = 'ctest -C ' + args.build_type + ' -V'
    elif target == 'quick':
        os.chdir(os.path.join(buildDir, 'cppcache', 'integration-test'))
        command = 'ctest -C ' + args.build_type + ' -L QUICK' + ' -j 4' + ' --schedule-random'
    elif target == 'stable':
        os.chdir(os.path.join(buildDir, 'cppcache', 'integration-test'))
        command = 'ctest -C ' + args.build_type + ' -L STABLE' + ' -j 4' + ' --schedule-random'
    else:
        os.chdir(buildDir)
        command = 'cmake --build . --config ' + args.build_type + ' --target ' + target
    print command
    rc = subprocess.call(command, shell=True)
    if 0 != rc:
        exit(rc)

exit(0)
