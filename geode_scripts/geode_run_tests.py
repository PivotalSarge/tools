#!/usr/bin/python

import argparse
import datetime
import platform
import re
import os
import subprocess
import sys

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

def findTestFile(dir, testname):
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            if re.search('^{}\.java'.format(testname), filename):
                return os.path.join(dirpath, filename)
    return None

def getModule(filepath, rootDir):
    rootDir += '/'
    if filepath.startswith(rootDir):
        filepath = filepath[len(rootDir):]
    return filepath.split('/')[0]

def getCategory(filename):
    file = open(filename, 'r')
    for line in file:
        m = re.search('@Category\(([A-Za-z]+)\.class', line)
        if m:
            return m.group(1)[:1].lower() + m.group(1)[1:]
    return None

def getTestName(filename):
    m = re.search('.*/([^/]+)\.java', filename)
    if m:
        return m.group(1)
    return filename

def getTest(filepath, integration, distributed, module):
    category = getCategory(filepath)
    if integration and "integrationTest" == category:
        return (category, getTestName(filepath), module)
    if distributed and "distributedTest" == category:
        return (category, getTestName(filepath), module)
    return None

def getTests(dir, module, integration, distributed):
    tests = []
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                if filepath.endswith('.java'):
                    test = getTest(filepath, integration, distributed, module)
                    if test:
                        tests.append(test)
    return tests

def getDecimalWidth(n):
    width = 1
    while 10 <= n:
        width += 1
        n //= 10
    return width

gitRootDir = getRootDir()
if not gitRootDir:
    print('Unable to determine git root directory')
    exit(1)
closed = None
if (os.path.basename(gitRootDir) == 'gemfire' or os.path.basename(gitRootDir) == 'closed'):
    closed = True

parser = argparse.ArgumentParser(description='Run Geode distributed and integration tests.')
parser.add_argument('--integration', dest='integration', default=False, action='store_true')
parser.add_argument('--distributed', dest='distributed', default=False, action='store_true')
parser.add_argument('candidates', metavar='test-or-module', nargs='*', help='test to run or module whose tests should be run')
args = parser.parse_args()
if not args.integration and not args.distributed:
    args.integration = True
    args.distributed = True

if not args.candidates:
    for module in os.listdir(gitRootDir):
        if module.startswith('geode'):
            args.candidates.append(module)

tests = []
for candidate in args.candidates:
    if os.path.isdir(candidate):
        tests.extend(getTests(candidate, candidate, args.integration, args.distributed))
    else:
        filepath = findTestFile(gitRootDir, candidate)
        if filepath:
            test = getTest(filepath, True, True, getModule(filepath, gitRootDir))
            if test:
                tests.append(test)

totalSuccess = True
if tests:
    logfile = os.path.join(getTempDir(), datetime.datetime.now().strftime("%Y%m%d%H%M%S.txt"))
    log = open(logfile, 'w')

    n = len(tests)
    width = getDecimalWidth(n)
    i = 0
    for test in tests:
        sys.stdout.write(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        sys.stdout.write(': Running ')
        i += 1
        sys.stdout.write(str(i).rjust(width, ' '))
        sys.stdout.write(' of ')
        sys.stdout.write(str(n).rjust(width, ' '))
        sys.stdout.write(': ')
        sys.stdout.write(test[1].ljust(55, '.'))
        sys.stdout.flush()
        # ./gradlew -D${CATEGORY}.single=$TEST ${MODULE}:${CATEGORY} >>$LOG_FILE 2>&1
        command = getGradleWrapper(gitRootDir)
        command += ' -D'
        command += test[0]
        command += '.single='
        command += test[1]
        command += ' '
        command += test[2]
        command += ':'
        command += test[0]
        rc = subprocess.call(command, stdout=log, stderr=log, shell=True)
        if rc == 0:
            sys.stdout.write('PASS')
        else:
            sys.stdout.write('FAIL')
            totalSuccess = False
        sys.stdout.write('\n')
        sys.stdout.flush()
    if totalSuccess:
        os.remove(logfile)
    else:
        os.rename(logfile, os.path.join(os.getcwd(), os.path.basename(logfile)))
        print('Output available at: {}'.format(os.path.join(os.getcwd(), os.path.basename(logfile))))
if not totalSuccess:
    exit(1)
exit(0)