# Convenience script to randomize the order of multiple files jointly

import sys
import random

def read_lines(filename):
    with open(filename) as f:
        return [line.rstrip('\n') for line in f]

def write_lines(filename, lines):
    with open(filename, 'w') as f:
        for line in lines:
            print(line, file=f)

in_filenames = sys.argv[1:]
assert len(in_filenames) >= 2

files_lines = list(map(read_lines, in_filenames))
assert len(set(map(len, files_lines))) == 1

lines_zipped = list(zip(*files_lines))
#print(len(lines_zipped))
#print(len(lines_zipped[0]))
#print(lines_zipped[0][0][0])
random.shuffle(lines_zipped)

files_lines = list(zip(*lines_zipped))
for in_filename, lines in zip(in_filenames, files_lines):
    out_filename = in_filename + '.shuf'
    write_lines(out_filename, lines)

