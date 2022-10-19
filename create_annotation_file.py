"""Create a file for the new annotation tool

python3 create_annotation_file.py annotations/round1/test.json data/playing/Nyberg.CEFR_ABC.dev.orig.round1 data/playing/Nyberg.CEFR_ABC.dev.corr.round1 data/playing/Nyberg.CEFR_ABC.dev.orig.round1.*
"""

import os
import json
import sys


def read_file_lines(filename):
    with open(filename) as f:
        return [line.strip() for line in f]


def main():
    out_filename, orig_filename, corr_filename, *system_filenames \
            = sys.argv[1:]
    assert out_filename.endswith('.json') and not os.path.exists(out_filename)
    orig = read_file_lines(orig_filename)
    corr = read_file_lines(corr_filename)
    systems = [read_file_lines(filename) for filename in system_filenames]
    names = [os.path.splitext(os.path.basename(filename))[1][1:]
             for filename in system_filenames]
    assert all(names)

    lengths = {len(orig), len(corr)} | set(map(len, systems))
    assert len(lengths) == 1, lengths

    data = []
    for orig_line, corr_line, *system_lines in zip(orig, corr, *systems):
        system_info = {}
        for name, line in zip(names, system_lines):
            system_info[name] = dict(
                    output=line,
                    annotators={})
        data.append(dict(
            original=orig_line,
            reference=corr_line,
            systems=system_info))

    with open(out_filename, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
