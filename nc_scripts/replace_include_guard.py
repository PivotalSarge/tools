#!/usr/bin/python

import argparse
import re
import os

def replace_include_guard(path):
    temp_path = path + '.tmp'
    with open(path, 'r') as input:
        with open(temp_path, 'w') as output:
            first = True
            macro = None
            endif = None
            for line in input:
                if first:
                    first = False
                    if '#pragma once' not in line:
                        output.write('#pragma once\n\n')

                ifndef_match = None
                if not macro:
                    ifndef_match = re.match('\s*#ifndef\s+(.+)\s*', line)
                    if ifndef_match:
                            macro = ifndef_match.group(1)

                define_match = None
                if macro:
                    define_match = re.match('\s*#define\s*{0}\s*'.format(macro), line)

                endif_match = re.match('\s*#endif.*', line)
                if endif_match:
                    endif = line
                elif not ifndef_match and not define_match:
                    if endif:
                        output.write(endif)
                        endif = None
                    output.write(line)
    if os.path.exists(temp_path):
        os.rename(temp_path, path)

parser = argparse.ArgumentParser(description='Replace include guards with #pragma once.')
parser.add_argument('files', metavar='file', nargs='*', help='file in which to replace include guards')
args = parser.parse_args()

for file in args.files:
    replace_include_guard(file)

exit(0)
