import csv
from collections import Counter, defaultdict
import random

import numpy as np
import Levenshtein
#import spacy


def ngrams(seq, n):
    for i in range(len(seq)-n+1):
        yield seq[i:i+n]


def get_edit_spans(source, target):
    ops = Levenshtein.editops(source, target)
    span = (-2, -2, -2, -2)
    for op,i,j in ops:
        i_inc = 1 if op in ('delete', 'replace') else 0
        j_inc = 1 if op in ('insert', 'replace') else 0
        if span[0] in (i, i-1) or span[2] in (j, j-1):
            span = (span[0], i+i_inc, span[2], j+j_inc)
        else:
            if span[0] >= 0:
                yield span
            span = (i, i+i_inc, j, j+j_inc)
    if span[0] >= 0:
        yield span


class Dalaj:
    def __init__(self):
        pass

    def read_data(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = list(reader)

    def compute_statistics(self, ns, char_ns):
        self.source_ngram_freq = {n: Counter() for n in ns}
        self.ngram_substitutions = Counter()
        self.letter_substitutions = defaultdict(Counter)
        self.letter_substitutions_pre = defaultdict(Counter)
        self.letter_substitutions_post = defaultdict(Counter)
        self.letter_ngram_freq = Counter()

        original_sentences = {row['original sentence'] for row in self.rows}

        for source in original_sentences:
            source_sent = tuple(source.split())
            for n in ns:
                self.source_ngram_freq[n].update(ngrams(source_sent, n))
            for n in char_ns:
                self.letter_ngram_freq.update(ngrams(source, n))

        for row in self.rows:
            original = row['original sentence']
            corrected = row['corrected sentence']
            l1 = row['l1']
            level = row['Approximate level']
            err_idx = tuple(map(int, row['error indices'].split('-')))
            cor_idx = tuple(map(int, row['corrected indices'].split('-')))
            error_label = row['error label']
            source = original[err_idx[0]:err_idx[1]+1]
            target = corrected[cor_idx[0]:cor_idx[1]+1]
            source_toks = tuple(source.split())
            target_toks = tuple(target.split())
            self.ngram_substitutions[(source_toks, target_toks)] += 1

        for (source, target), n in self.ngram_substitutions.most_common():
            source = ' '.join(source).casefold()
            target = ' '.join(target).casefold()
            nld = Levenshtein.distance(source, target) \
                    / max(len(source), len(target))
            if nld < 0.4 and max(len(source), len(target)) > 2:
                source = f'#{source}#'
                target = f'#{target}#'
                for s0, s1, t0, t1 in get_edit_spans(source, target):
                    self.letter_substitutions[
                            source[s0:s1]][target[t0:t1]] += 1
                    self.letter_substitutions_pre[
                            source[s0-1:s1]][target[t0-1:t1]] += 1
                    self.letter_substitutions_post[
                            source[s0:s1+1]][target[t0:t1+1]] += 1


    def corrupt_sentence(self, sentence):
        tokens = sentence.split()
        p_permute = 0.1
        p_permute_size = [0.5, 0.2, 0.1, 0.1, 0.1]
        p_permute_range = list(range(2, 2+len(p_permute_size)))
        for i in range(len(tokens)):
            if random.random() < p_permute:
                k = np.random.choice(p_permute_range, p=p_permute_size)
                k = min(len(tokens)-i, k)
                tokens[i:i+k] = random.sample(tokens[i:i+k], k=k)
        return ' '.join(tokens)


if __name__ == '__main__':
    import sys, pprint
    dalaj = Dalaj()
    dalaj.read_data(sys.argv[1])
    dalaj.compute_statistics([1, 2, 3], [1, 2, 3, 4, 5])

    print(dalaj.corrupt_sentence('Det här är en liten testmening !'))

    #print('INSERTIONS')
    #pprint.pprint(dalaj.letter_substitutions_pre['#'])
    #print('REPLACEMENTS')
    #for ngram, c in dalaj.letter_ngram_freq.most_common():
    #    if ngram in dalaj.letter_substitutions:
    #        print(ngram, c)
    #        pprint.pprint(dalaj.letter_substitutions[ngram])
    #    #else:
    #    #    print(ngram, c)


    #print(len(dalaj.letter_substitutions))
    #pprint.pprint(dalaj.letter_substitutions)

    #pprint.pprint(dalaj.letter_substitutions_pre.most_common())
    #pprint.pprint(dalaj.letter_substitutions_post.most_common())

