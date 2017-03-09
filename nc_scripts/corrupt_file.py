#!/usr/bin/python

import argparse
import binascii
import mmap
import random

def corrupt_file(path, content, percentage):
    with open(path, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        length = len(mm)
        if 0 < length:
            n = 0

            while n < (percentage * length):
                i = random.randint(0, length - 1)
                if content:
                    if length < i + len(content):
                        i = length - len(content)
                    mm[i:(i + len(content))] = content
                    n += len(content)
                else:
                    c = random.randint(48, 122)
                    while (57 < c and c < 65) or (90 < c and c < 97):
                        c = random.randint(48, 122)
                    mm.seek(i)
                    mm.write_byte(chr(c))
                    n += 1

parser = argparse.ArgumentParser(description='corrupts file(s).')
parser.add_argument('paths', metavar='path', nargs='*', help='file to corrupt')
parser.add_argument('--file-type', choices=['TEXT', 'BINARY'], default='TEXT', help='whether the file is text or binary')
parser.add_argument('--percentage', type=int, default=1, help='percentage of file to corrupt')
corruption_group = parser.add_mutually_exclusive_group()
corruption_group.add_argument('--file-corruption', type=str, help='content with which to corrupt the file')
corruption_group.add_argument('--random-file-corruption', action='store_true', help='corrupt the file with random content')
args = parser.parse_args()

random.seed()

if args.file_corruption:
    if args.file_type == 'BINARY':
        content = bytearray([ord(x) for x in binascii.unhexlify(args.file_corruption)])
    else:
        content = args.file_corruption
elif args.random_file_corruption:
    content = None
else:
    if args.file_type == 'BINARY':
        content = bytearray([88])
    else:
        content = 'X'

for path in args.paths:
    corrupt_file(path, content, (0.01 * args.percentage))

exit(0)
