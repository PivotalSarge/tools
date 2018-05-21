#!/usr/bin/python

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Find the named classes in the directories or classpaths')
parser.add_argument('-c', '--class', dest='classes', nargs='*', default=[], help='class to find')
parser.add_argument('-cp', '--classpath', dest='classpaths', nargs='*', default=[], help='classpath in which to find')
parser.add_argument('-d', '--directory', dest='directories', nargs='*', default=[], help='directory in which to find')
parser.add_argument('-j', '--jar', dest='jars', nargs='*', default=[], help='.jar file in which to find')
parser.add_argument('candidates', metavar='class-jar-directory-or-classpath', nargs='*', help='class to find or .jar file, directory, or classpath in which to find')
args = parser.parse_args()

for candidate in args.candidates:
  if ':' in candidate:
    for path in candidate.split(':'):
      if path.endswith('.jar'):
        args.jars.append(path)
      else:
        args.directories.append(path)
  elif '/' in candidate:
      args.directories.append(candidate)
  elif candidate.endswith('.jar'):
    args.jars.append(candidate)
  else:
    args.classes.append(candidate)

first = True
devnull = open(os.devnull,"w")
for clazz in args.classes:
  if first:
    first = False
  else:
    print('')
  print(clazz + ':')

  finds = []
  for directory in args.directories:
    command = 'javap -cp ' + directory + ' ' + clazz
    if subprocess.call(command, stdout=devnull, stderr=devnull, shell=True) == 0:
      finds.append(directory)

  if finds:
    for find in finds:
      print(find)
  else:
    print('Not found!')