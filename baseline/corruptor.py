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
        self.target_ngram_freq = Counter()
        self.ngram_substitutions = Counter()
        self.letter_substitutions = defaultdict(Counter)
        self.letter_substitutions_pre = defaultdict(Counter)
        self.letter_substitutions_post = defaultdict(Counter)
        self.letter_ngram_freq = Counter()
        self.ngram_alternatives = defaultdict(Counter)

        original_sentences = {row['original sentence'] for row in self.rows}

        for target in original_sentences:
            target_sent = tuple(target.casefold().split())
            for n in ns:
                self.target_ngram_freq.update(ngrams(target_sent, n))
            for n in char_ns:
                self.letter_ngram_freq.update(ngrams(target, n))

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
            source_toks = tuple(source.casefold().split())
            target_toks = tuple(target.casefold().split())
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


        for (source, target), n in self.ngram_substitutions.most_common():
            if n < 3:
                break
            self.ngram_alternatives[target][source] = n

        self.ngram_alternatives_lens = sorted(
                {len(target) for target in self.ngram_alternatives.keys()},
                reverse=True)


    def corrupt_word_order(self, sentence, p_move=0.1, distance_std=3):
        tokens = sentence.split()
        non_punct = [i for i, token in enumerate(tokens) if token.isalnum()]
        if len(tokens) < 2:
            return sentence
        n_moves = int(np.random.binomial(len(non_punct), p_move))

        def punct_span(center):
            start = center
            end = center
            while start > 0 and tokens[start-1].isalnum():
                start -= 1
            while end < len(tokens)-1 and tokens[end+1].isalnum():
                end += 1
            return start, end

        for _ in range(n_moves):
            i = random.randint(0, len(tokens)-1)
            while not tokens[i].isalnum():
                i = random.randint(0, len(tokens)-1)
            item = tokens.pop(i)
            j = -1
            start, end = punct_span(i)
            while not start <= j <= end:
                j = int(np.random.normal(loc=i, scale=distance_std))
                if j == i:
                    j += 1
            if i == 0 and j != 0:
                item = item.lower()
            elif i != 0 and j == 0:
                item = item[0].upper() + item[1:]
                tokens[0] = tokens[0].lower()
            tokens.insert(j, item)
        return ' '.join(tokens)

    def corrupt_word_choice(sentence):
        def corrupt_ngram(target, temp=1):
            if target not in self.ngram_alternatives:
                return target
            alternatives = list(self.ngram_alternatives[target].items())
            alternatives.append(
                    (target, self.target_ngram_freq[target]-sum(alternatives)))
            ps = np.array([c for _, c in alternatives])
            ps /= ps.sum()
            if temp != 1:
                ps = np.pow(ps, 1.0/temp)
                ps /= ps.sum()
            i = np.random.choice(len(alternatives), p=ps)
            # TODO: continue debugging here...
            if target == ('i',):
                print(alternatives, ps)
            return alternatives[i][0]

        tokens = tuple(sentence.split())

        for n in self.ngram_alternatives_lens:
            for i in range(len(tokens)-n+1):
                ngram = tokens[i:i+n]
                new_ngram = corrupt_ngram(ngram)
                if new_ngram != ngram:
                    tokens[i:i+n] = new_ngram
                    print('**** Replacing', ngram, 'with', new_ngram)


    #def corrupt_sentence(self, sentence):
    #    tokens = sentence.split()
    #    p_permute = 0.1
    #    p_permute_size = [0.5, 0.2, 0.1, 0.1, 0.1]
    #    p_permute_range = list(range(2, 2+len(p_permute_size)))
    #    for i in range(len(tokens)):
    #        if random.random() < p_permute:
    #            k = np.random.choice(p_permute_range, p=p_permute_size)
    #            k = min(len(tokens)-i, k)
    #            tokens[i:i+k] = random.sample(tokens[i:i+k], k=k)
    #    return ' '.join(tokens)


if __name__ == '__main__':
    import sys, pprint
    dalaj = Dalaj()
    dalaj.read_data(sys.argv[1])
    dalaj.compute_statistics([1, 2, 3], [1, 2, 3, 4, 5])

    for row in dalaj.rows[:10]:
        print(row['corrected sentence'])
        print(dalaj.corrupt_word_order(row['corrected sentence']))
        print()

    #pprint.pprint([(' '.join(ngram1), ' '.join(ngram2), c)
    #               for (ngram1, ngram2), c in
    #               dalaj.ngram_substitutions.most_common()
    #               if c >= 3])

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

