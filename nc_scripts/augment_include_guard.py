#!/usr/bin/python

import argparse
import hashlib
import re
import os

def create_guard(path):
    return 'APACHE_GEODE_GUARD_{0}'.format(hashlib.md5(path).hexdigest())

def replace_include_guard(path):
    temp_path = path + '.tmp'
    with open(path, 'r') as input:
        with open(temp_path, 'w') as output:
            first = True
            guard = None
            for line in input:
                output.write(line)
                if first:
                    first = False
                    match = re.match('\s*#pragma\s+once\s*', line)
                    if match:
                        guard = create_guard(path)
                        output.write('\n#ifndef {0}\n#define {0}\n'.format(guard))
            if guard:
                output.write('\n#endif // {0}\n'.format(guard))
    if os.path.exists(temp_path):
        os.rename(temp_path, path)

parser = argparse.ArgumentParser(description='Replace include guards with #pragma once.')
parser.add_argument('files', metavar='file', nargs='*', help='file in which to replace include guards')
args = parser.parse_args()

for file in args.files:
    replace_include_guard(file)

exit(0)
