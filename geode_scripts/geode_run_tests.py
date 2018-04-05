#!/usr/bin/python

import argparse
import datetime
import os
import platform
import random
import re
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

def getCategories(filename):
    categories = []

    # Try to parse the category out of the source file.
    file = open(filename, 'r')
    for line in file:
        m = re.search('^@Category\({?([^]{}]+)}?\)', line)
        if m:
            for category in re.split(', ', m.group(1)):
                category = re.sub('\.class$', '', category)
                category = category[:1].lower() + category[1:]
                # The unit test category is called "test" by gradle.
                if 'unitTest' == category:
                    category = 'test'
                categories.append(category)

    # Move flaky tests to the front because if a test is marked flaky and another category,
    # it can only be run as a flaky test.
    if 'flakyTest' in categories:
        categories.insert(0, categories.pop(categories.index('flakyTest')))

    return categories

def getTestName(filename):
    m = re.search('.*/([^/]+)\.java', filename)
    if m:
        return m.group(1)
    return filename

def getTest(filepath, module, unit, integration, distributed, flaky):
    for category in getCategories(filepath):
        if unit and 'test' == category:
            return (category, getTestName(filepath), module)
        if integration and 'integrationTest' == category:
            return (category, getTestName(filepath), module)
        if distributed and 'distributedTest' == category:
            return (category, getTestName(filepath), module)
        if flaky and 'flakyTest' == category:
            return (category, getTestName(filepath), module)
    return None

def getTests(dir, module, unit, integration, distributed, flaky):
    tests = []
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                if filepath.endswith('.java'):
                    test = getTest(filepath, module, unit, integration, distributed, flaky)
                    if test:
                        tests.append(test)
    return tests

def randomizeIndices(n):
    random.seed()
    indices = []
    while len(indices) < n:
        index = random.randint(0, n - 1)
        if index not in indices:
            indices.append(index)
    return indices

def getDecimalWidth(n):
    width = 1
    while 10 <= n:
        width += 1
        n //= 10
    return width

def formatDelta(delta):
    s = str(delta)
    # if s.startswith('0:'):
    #     s = s[2:]
    # if s.startswith('00:'):
    #     s = s[3:]
    return s.split('.')[0]

def addTest(candidate):
    filepath = findTestFile(gitRootDir, candidate)
    if filepath:
        test = getTest(filepath, getModule(filepath, gitRootDir), True, True, True, True)
        if test:
            tests.append(test)

gitRootDir = getRootDir()
if not gitRootDir:
    print('Unable to determine git root directory')
    exit(1)
closed = None
if (os.path.basename(gitRootDir) == 'gemfire' or os.path.basename(gitRootDir) == 'closed'):
    closed = True

parser = argparse.ArgumentParser(description='Run Geode unit, integration, distributed, and flaky tests.')
parser.add_argument('--unit', dest='unit', default=False, action='store_true')
parser.add_argument('--integration', dest='integration', default=False, action='store_true')
parser.add_argument('--distributed', dest='distributed', default=False, action='store_true')
parser.add_argument('--flaky', dest='flaky', default=False, action='store_true')
parser.add_argument('candidates', metavar='test-or-module', nargs='*', help='test to run or module whose tests should be run')
args = parser.parse_args()
if not args.unit and not args.integration and not args.distributed and not args.flaky:
    args.integration = True
    args.distributed = True

if not args.candidates:
    for module in os.listdir(gitRootDir):
        if module.startswith('geode'):
            args.candidates.append(module)

tests = []
for candidate in args.candidates:
    candidate = candidate.strip('/')
    if os.path.isdir(candidate):
        tests.extend(getTests(candidate, candidate, args.unit, args.integration, args.distributed, args.flaky))
    else:
        if not addTest(candidate):
            if candidate == 'serializables':
                addTest('AnalyzeSerializablesJUnitTest')
                addTest('AnalyzeWANSerializablesJUnitTest')
                addTest('AnalyzeCQSerializablesJUnitTest')
                addTest('AnalyzeLuceneSerializablesJUnitTest')
                addTest('AnalyzeWebApiSerializablesJUnitTest')
                addTest('AnalyzeConnectorsSerializablesJUnitTest')

totalSuccess = True
if tests:
    print('Started at  ' + datetime.datetime.now().isoformat())
    if 1 < len(tests):
        logfile = os.path.join(getTempDir(), datetime.datetime.now().strftime("%Y%m%d%H%M%S.txt"))
        log = open(logfile, 'w')

    n = len(tests)
    width = getDecimalWidth(n)
    i = 0
    previous = datetime.datetime.now()
    indices = randomizeIndices(n)
    for index in indices:
        i += 1
        test = tests[index]
        if 1 < len(tests):
            sys.stdout.write('Running ')
            sys.stdout.write(str(i).rjust(width, ' '))
            sys.stdout.write(' of ')
            sys.stdout.write(str(n).rjust(width, ' '))
            sys.stdout.write(': ')
            sys.stdout.write(test[1].ljust(60, '.'))
            sys.stdout.flush()
        # ./gradlew -D${CATEGORY}.single=$TEST ${MODULE}:${CATEGORY} >>$LOG_FILE 2>&1
        command = getGradleWrapper(gitRootDir)
        command += ' -x'
        command += ' javadoc'
        command += ' -x'
        command += ' rat'
        command += ' -x'
        command += ' spotlessApply'
        command += ' -D'
        command += test[0]
        command += '.single='
        command += test[1]
        command += ' '
        command += test[2]
        command += ':'
        command += test[0]
        if 1 < len(tests):
            rc = subprocess.call(command, stdout=log, stderr=log, shell=True)
        else:
            rc = subprocess.call(command, shell=True)
        if rc != 0:
            totalSuccess = False
        current = datetime.datetime.now()
        if 1 < len(tests):
            if rc == 0:
                sys.stdout.write('PASS')
            else:
                sys.stdout.write('FAIL')
            sys.stdout.write(' (')
            sys.stdout.write(formatDelta(current - previous))
            sys.stdout.write(')\n')
            sys.stdout.flush()
        previous = current
    if 1 < len(tests):
        if totalSuccess:
            os.remove(logfile)
        else:
            os.rename(logfile, os.path.join(os.getcwd(), os.path.basename(logfile)))
            print('Output available at: {}'.format(os.path.join(os.getcwd(), os.path.basename(logfile))))
    print('Finished at ' + datetime.datetime.now().isoformat())

if not totalSuccess:
    exit(1)
exit(0)
