import csv
from collections import Counter, defaultdict
import random
from xml.etree import ElementTree as ET

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


def capitalize_like(s, ref):
    if ref[0].isupper():
        return s[0].upper() + s[1:]
    else:
        return s


def capitalize(s):
    return s[0].upper() + s[1:]


class Corruptor:
    def __init__(self):
        pass

    def read_data(self, dalaj_filename, saldom_filename=None):
        with open(dalaj_filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = list(reader)

        self.saldom = ET.parse(saldom_filename) if saldom_filename else None

    def compute_statistics(self, ns, char_ns):
        self.target_ngram_freq = Counter()
        self.ngram_substitutions = Counter()
        self.letter_substitutions = defaultdict(Counter)
        self.letter_substitutions_pre = defaultdict(Counter)
        self.letter_substitutions_post = defaultdict(Counter)
        self.letter_ngram_freq = Counter()
        self.ngram_alternatives = defaultdict(Counter)

        # Common n-grams (relative frequency >= 0.001) will be dropped with
        # this probability, adjusted by the temp parameter in
        # corrupt_word_choice
        drop_ratio = 0.1

        n_tokens = sum(len(row['corrected sentence'].split())
                       for row in self.rows)
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

        for ngram, c in self.target_ngram_freq.items():
            if c/n_tokens >= 0.001:
                self.ngram_alternatives[ngram][tuple()] = int(
                        max(1, c*drop_ratio))

        self.ngram_alternatives_lens = sorted(
                {len(target) for target in self.ngram_alternatives.keys()},
                reverse=True)

        if self.saldom is not None:
            self.paradigms = []
            self.paradigm_index = defaultdict(list)
            for lexicalentry in self.saldom.iter('LexicalEntry'):
                paradigm = []
                for wordform in lexicalentry.findall('WordForm'):
                    feats = {feat.get('att'): feat.get('val')
                             for feat in wordform.findall('feat')}
                    paradigm.append((feats['writtenForm'], feats['msd']))
                self.paradigms.append(paradigm)
            for paradigm in self.paradigms:
                for form, msd in paradigm:
                    self.paradigm_index[form].append(paradigm)

    def corrupt_word_order(self, sentence, p_move=0.1, distance_std=1.5):
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
            #item = tokens.pop(i)
            j = -1
            start, end = punct_span(i)
            while not start <= j <= end:
                j = int(np.random.normal(loc=i, scale=distance_std))
                if j == i:
                    j += 1
            i, j = sorted([i, j])
            item = tokens[i]
            tokens[i] = tokens[j]
            tokens[j] = item
            if i == 0:
                tokens[i] = capitalize_like(tokens[i], tokens[j])
                tokens[j] = tokens[j][0].lower() + tokens[j][1:]
        return ' '.join(tokens)

    def corrupt_word_choice(self, sentence, temp=1):
        def corrupt_ngram(target_original):
            target = tuple(s.casefold() for s in target_original)
            if target not in self.ngram_alternatives:
                return target_original
            alternatives = list(self.ngram_alternatives[target].items())
            alternatives.append(
                    (target, self.target_ngram_freq[target]-
                                sum(c for _, c in alternatives)))
            ps = np.array([c for _, c in alternatives], dtype=float)
            ps /= ps.sum()
            if temp != 1:
                ps = np.power(ps, 1.0/temp)
                ps /= ps.sum()
            i = np.random.choice(len(alternatives), p=ps)
            result = alternatives[i][0]
            if not result:
                # could be a 0-gram
                return result
            return (capitalize_like(result[0], target_original[0]),) + \
                   result[1:]

        tokens = sentence.split()

        for n in self.ngram_alternatives_lens:
            for i in range(len(tokens)-n+1):
                ngram = tuple(tokens[i:i+n])
                new_ngram = corrupt_ngram(ngram)
                if new_ngram != ngram:
                    tokens[i:i+n] = new_ngram
                    if tokens and i == 0 and not new_ngram:
                        tokens[i] = capitalize(tokens[i])
                    #print('**** Replacing', ngram, 'with', new_ngram)

        return ' '.join(tokens)


    def corrupt_forms(self, sentence, temp=1):
        def corrupt_letter(c):
            if c in self.letter_substitutions:
                alternatives = [c]
                ps = [self.letter_ngram_freq.get(c, 1)]
                for alt, n in self.letter_substitutions[c].items():
                    if n >= 3:
                        alternatives.append(alt)
                        ps.append(n)
                ps = np.array(ps, dtype=float)
                ps /= ps.sum()
                if temp != 1:
                    ps = np.power(ps, 1.0/temp)
                    ps /= ps.sum()
                return alternatives[np.random.choice(len(alternatives), p=ps)]
            return c

        def corrupt_spelling(original_token):
            token = original_token.lower()
            new_token = ''.join(corrupt_letter(c) for c in token)
            return capitalize_like(new_token, original_token)

        return ' '.join(corrupt_spelling(token) for token in sentence.split())


    def corrupt_inflection(self, sentence, p_reinflect=0.1, p_split=0.25):
        def split_compound(token):
            min_suffix = 4
            min_prefix = 4
            if len(token) < min_suffix + min_prefix:
                return (token,)
            for i in range(min_prefix, len(token)-min_suffix+1):
                suffix = token[i:]
                prefix = token[:i]
                suffix_paradigms = self.paradigm_index.get(suffix, None)
                prefix_paradigms = self.paradigm_index.get(prefix, None)
                if suffix_paradigms and prefix_paradigms:
                    #print('prefix_paradigms', prefix_paradigms)
                    if any(form == prefix and tag in ('ci', 'cm')
                           for paradigm in prefix_paradigms
                           for form, tag in paradigm):
                        return (prefix, suffix)
            return (token,)

        def destroy_token(token):
            parts = split_compound(token)
            if random.random() < p_reinflect:
                # TODO: something weird going on here, e.g. är -> smid,
                # mamma -> gosse
                if parts[-1] in self.paradigm_index:
                    paradigms = self.paradigm_index[parts[-1]]
                    parts = parts[:-1] + \
                        (random.choice(random.choice(paradigms))[0],)
            if random.random() < p_split:
                return ' '.join(parts)
            else:
                return ''.join(parts)

        return ' '.join(destroy_token(token) for token in sentence.split())


if __name__ == '__main__':
    import sys, pprint
    dalaj = Corruptor()
    dalaj.read_data(*sys.argv[1:])
    dalaj.compute_statistics([1, 2, 3], [1, 2, 3, 4, 5])

    for row in dalaj.rows[:50]:
        sentence = row['corrected sentence']
        print(sentence)
        sentence = dalaj.corrupt_word_order(sentence)
        print(sentence)
        sentence = dalaj.corrupt_word_choice(sentence)
        print(sentence)
        sentence = dalaj.corrupt_inflection(
                sentence, p_reinflect=0.1, p_split=0.25)
        print(sentence)
        sentence = dalaj.corrupt_forms(sentence, temp=1.75)
        print(sentence)
        print()


    #n_tokens = sum(len(row['corrected sentence'].split()) for row in dalaj.rows)
    #pprint.pprint(
    #        [(ngram, c/n_tokens)
    #            for ngram, c in dalaj.target_ngram_freq.most_common()
    #         if c >= 100])
    #print(n_tokens, 'tokens')


    #pprint.pprint(dalaj.ngram_alternatives)

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

    #pprint.pprint(dalaj.letter_substitutions_pre)
    #pprint.pprint(dalaj.letter_substitutions_post.most_common())

