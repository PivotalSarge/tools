#!/usr/bin/python

import argparse
import binascii
import random

def parse_range(str):
    parts = str.split('..')
    if 2 < len(parts) < 1:
        raise ValueError("Bad range: '{}'".format(str))

    parts = [int(i) for i in parts]
    if 1 == len(parts):
        return (parts[0], parts[0])
    return (parts[0], parts[len(parts) - 1])

def randomize_length(length_tuple):
    return random.randint(length_tuple[0], length_tuple[1])

def generate_binary_file(path, length, content):
    with open(path, 'wb') as output:
        if 0 < length:
            n = 0

            while n < length:
                if content:
                    if length < n + len(content):
                        output.write(content[0:(length - n)])
                        n = length
                    else:
                        output.write(content)
                        n += len(content)
                else:
                    output.write(bytearray([random.randint(0, 255)]))
                    n += 1

def generate_text_file(path, length, content, magic):
    with open(path, 'w') as output:
        if 0 < length:
            n = 0

            if magic:
                if 2 == len(magic):
                    output.write(magic)
                    n += len(magic)
                else:
                    output.write(magic)
                    output.write('\n')
                    n += len(magic) + 1

            while n < length:
                if content:
                    if length < n + len(content):
                        output.write(content[0:(length - n)])
                        n = length
                    else:
                        output.write(content)
                        n += len(content)
                else:
                    c = random.randint(48, 122)
                    while (57 < c and c < 65) or (90 < c and c < 97):
                        c = random.randint(48, 122)
                    output.write(str(unichr(c)))
                    n += 1
            output.write('\n')

parser = argparse.ArgumentParser(description='Generates file(s).')
parser.add_argument('paths', metavar='path', nargs='*', help='file to generate')
parser.add_argument('--file-type', choices=['TEXT', 'BINARY'], default='TEXT')
parser.add_argument('--magic')
length_group = parser.add_mutually_exclusive_group()
length_group.add_argument('--file-length', type=int)
length_group.add_argument('--random-file-length', type=str)
content_group = parser.add_mutually_exclusive_group()
content_group.add_argument('--file-content', type=str)
content_group.add_argument('--random-file-content', action='store_true')
args = parser.parse_args()

random.seed()

if args.file_length:
    length_tuple = (args.file_length, args.file_length)
elif args.random_file_length:
    length_tuple = parse_range(args.random_file_length)
else:
    length_tuple = (0, 0)

if args.file_content:
    if args.file_type == 'BINARY':
        content = bytearray([ord(x) for x in binascii.unhexlify(args.file_content)])
    else:
        content = args.file_content
elif args.random_file_content:
    content = None
else:
    if args.file_type == 'BINARY':
        content = bytearray([0])
    else:
        content = '0'

for path in args.paths:
    if args.file_type == 'BINARY':
        generate_binary_file(path, randomize_length(length_tuple), content)
    else:
        generate_text_file(path, randomize_length(length_tuple), content, args.magic)

exit(0)
