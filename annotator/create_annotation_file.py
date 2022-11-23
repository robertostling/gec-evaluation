"""Create a file for the new annotation tool

python3 create_annotation_file.py annotations/round1/test.json data/playing/Nyberg.CEFR_ABC.dev.orig.round1 data/playing/Nyberg.CEFR_ABC.dev.corr.round1 data/playing/Nyberg.CEFR_ABC.dev.orig.round1.*

python3 annotator/create_annotation_file.py annotations/round2/robert.json data/playing/Nyberg.CEFR_ABC.dev.orig.round2 data/playing/Nyberg.CEFR_ABC.dev.corr.round2 data/playing/Nyberg.CEFR_ABC.dev.orig.round2.*

python3 annotator/create_annotation_file.py annotations/balanced_A/robert.json data/balanced_test/Nyberg.CEFR_A.balanced_test.orig.txt data/balanced_test/Nyberg.CEFR_A.balanced_test.corr.txt data/balanced_test/Nyberg.CEFR_A.balanced_test.granska data/balanced_test/Nyberg.CEFR_A.balanced_test.mt data/balanced_test/Nyberg.CEFR_A.balanced_test.s2 data/balanced_test/Nyberg.CEFR_A.balanced_test.mw data/balanced_test/Nyberg.CEFR_A.balanced_test.mm 

python3 annotator/create_annotation_file.py annotations/balanced_A/katarina.json data/balanced_test/Nyberg.CEFR_A.balanced_test.orig.txt data/balanced_test/Nyberg.CEFR_A.balanced_test.corr.txt data/balanced_test/Nyberg.CEFR_A.balanced_test.granska data/balanced_test/Nyberg.CEFR_A.balanced_test.mt data/balanced_test/Nyberg.CEFR_A.balanced_test.s2 data/balanced_test/Nyberg.CEFR_A.balanced_test.mw data/balanced_test/Nyberg.CEFR_A.balanced_test.mm 

"""

import os
import json
import sys
import random

import spacy


def read_file_lines(filename):
    nlp = spacy.load('sv_core_news_sm')

    def tokenize(s):
        doc = nlp.tokenizer(s.strip())
        return ' '.join(t.text for t in doc).strip()

    with open(filename) as f:
        return [tokenize(line) for line in f]


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

    item_order = [i for i,_ in enumerate(data)]
    random.shuffle(item_order)

    metadata = dict(
            next_item=0,
            item_order=item_order,
            data=data)
    with open(out_filename, 'w') as f:
        json.dump(metadata, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
