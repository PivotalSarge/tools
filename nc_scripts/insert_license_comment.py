#!/usr/bin/python

import argparse
import re
import os

def determine_comment_type(path):
    extension = os.path.splitext(path)[1]
    if '.xml' == extension:
        return 'xml'
    if '.sh' == extension or '.csh' == extension or '.bash' == extension:
        return 'shell'
    if '.bat' == extension or '.ps1' == extension or '.psm1' == extension:
        return 'batch'
    if '.cpp' == extension or '.cxx' == extension or '.C' == extension or '.c' == extension or '.hpp' == extension or '.hxx' == extension or '.H' == extension or '.h' == extension or '.java' == extension:
        return 'c'

    with open(path, 'r') as input:
        for line in input:
            # We have to use '.*' because Windows puts wacky Unicode characters in their files.
            if re.match('.*<\?xml\s+', line):
                return 'xml'
            if re.match('.*<Project\s+.*', line):
                return 'xml'
    return None

def insert_shell_comment(file, license):
    for line in license:
        file.write('# ' + line)

def insert_batch_comment(file, license):
    for line in license:
        file.write('rem ' + line)

def insert_c_comment(file, license):
    file.write('/*\n')
    for line in license:
        file.write(' * ' + line)
    file.write(' */\n')

def insert_xml_comment(file, license):
    file.write('<!--\n')
    for line in license:
        file.write('  ' + line)
    file.write('-->\n')

def insert_license_comment(path, comment_type, license):
    if not comment_type:
        comment_type = determine_comment_type(path)
    if not comment_type:
        print('Unable to determine comment type for {0}'.format(path))
        return

    temp_path = path + '.tmp'
    with open(path, 'r') as input:
        with open(temp_path, 'w') as output:
            count = 0
            for line in input:
                if 0 == count:
                    if 'shell' != comment_type:
                        function = 'insert_{0}_comment'.format(comment_type)
                        eval(function)(output, license)
                elif 1 == count:
                    if 'shell' == comment_type:
                        output.write('\n')
                        insert_shell_comment(output, license)
                        output.write('\n')

                output.write(line)
                count += 1

    if os.path.exists(temp_path):
        os.rename(temp_path, path)

parser = argparse.ArgumentParser(description='Insert license as comment into files.')
parser.add_argument('files', metavar='file', nargs='*', help='file into which to insert license')
parser.add_argument('--type', dest='comment_type', help='type of comment, e.g., shell, batch, c, xml')
parser.add_argument('--license', dest='license_path', help='path to file containing license text')
args = parser.parse_args()
if not args.license_path:
    print('License file not specified!')
    exit(1)

for file in args.files:
    with open(args.license_path, 'r') as license:
        insert_license_comment(file, args.comment_type, license)

exit(0)
