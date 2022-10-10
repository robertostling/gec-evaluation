import csv
from collections import Counter, defaultdict
import random
from xml.etree import ElementTree as ET
import time
import multiprocessing

import numpy as np
import Levenshtein
#import spacy


def sample_from_counts(counts):
    elements, n = list(zip(*counts))
    p = np.array(n, dtype=float)
    p /= p.sum()
    i = np.random.choice(len(elements), p=p)
    return elements[i]


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
    if s and ref and ref[0].isupper():
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
        self.spurious_ngrams = Counter()

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
            # l1 = row['l1']
            # level = row['Approximate level']
            err_idx = tuple(map(int, row['error indices'].split('-')))
            cor_idx = tuple(map(int, row['corrected indices'].split('-')))
            # error_label = row['error label']
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
                if ''.join(ngram).isalpha() or ngram == (',',):
                    self.spurious_ngrams[ngram] = c
            if c/n_tokens >= 0.001:
                self.ngram_alternatives[ngram][tuple()] = int(
                        max(1, c*drop_ratio))

        self.ngram_alternatives_lens = sorted(
                {len(target) for target in self.ngram_alternatives.keys()},
                reverse=True)

        if self.saldom is not None:
            self.paradigms = []
            self.paradigm_index = defaultdict(set)
            for lexicalentry in self.saldom.iter('LexicalEntry'):
                lemma = lexicalentry.find('Lemma')
                fr = lemma.find('FormRepresentation')
                feats = {feat.get('att'): feat.get('val')
                         for feat in fr.findall('feat')}
                if feats['partOfSpeech'] not in ('nn', 'vb', 'av'):
                    continue

                paradigm = []
                for wordform in lexicalentry.findall('WordForm'):
                    feats = {feat.get('att'): feat.get('val')
                             for feat in wordform.findall('feat')}
                    paradigm.append((feats['writtenForm'], feats['msd']))
                self.paradigms.append(paradigm)
            for i, paradigm in enumerate(self.paradigms):
                for form, msd in paradigm:
                    self.paradigm_index[form].add(i)

            del self.saldom

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
            if end - start <= 2:
                continue
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
            if alternatives[-1][1] <= 0:
                # This happens in a couple of cases, not sure why
                return target_original
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
                    if any(form == prefix and tag in ('ci', 'cm')
                           for paradigm_idx in prefix_paradigms
                           for form, tag in self.paradigms[paradigm_idx]):
                        return (prefix, suffix)
            return (token,)

        def destroy_token(token):
            parts = split_compound(token)
            if random.random() < p_reinflect:
                if len(parts[-1]) >= 4 and parts[-1] in self.paradigm_index:
                    paradigm_idxs = self.paradigm_index[parts[-1]]
                    paradigm_idx = random.choice(list(paradigm_idxs))
                    paradigm = self.paradigms[paradigm_idx]
                    paradigm = [form for form, msd in paradigm
                                if msd not in ('c', 'ci', 'cm', 'sms')]
                    parts = parts[:-1] + (random.choice(paradigm),)
            if random.random() < p_split:
                return ' '.join(parts)
            else:
                return ''.join(parts)

        return ' '.join(destroy_token(token) for token in sentence.split())

    def corrupt_capitalization(self, sentence):
        p_lowercase = 0.2
        p_uppercase = 0.025
        p_uppercase_token = 0.1
        p_uppercase_all = 0.01
        if random.random() < p_lowercase:
            # often, lower-case everytihng
            sentence = sentence.lower()
        if random.random() < p_uppercase:
            # sometimes, make every few words upper-case
            sentence = ' '.join(
                    token.upper() if random.random() < p_uppercase_token
                            else token
                    for token in sentence.split())
        if random.random() < p_uppercase_all:
            # rarely, EVERYTHING SHOULD BE IN CAPS
            sentence = sentence.upper()
        return sentence

    def corrupt_insert(self, sentence, p_insert=0.025):
        tokens = sentence.split()
        n = int(np.random.binomial(len(tokens), p_insert))
        for _ in range(n):
            i = random.randint(0, len(tokens))
            ngram = sample_from_counts(self.spurious_ngrams.items())
            tokens.insert(' '.join(ngram), i)
        return ' '.join(tokens)


global_corruptor = None

def initializer(corruptor):
    global global_corruptor
    global_corruptor = corruptor


def corrupt_sentences(sentence_batch):
    corrupted_batch = []
    for sentence in sentence_batch:
        sentence = sentence.strip()
        sentence = global_corruptor.corrupt_word_order(
                sentence, p_move=0.1, distance_std=1.5)
        sentence = global_corruptor.corrupt_insert(sentence, p_insert=0.025)
        sentence = global_corruptor.corrupt_word_choice(sentence)
        sentence = global_corruptor.corrupt_inflection(
                sentence, p_reinflect=0.1, p_split=0.25)
        sentence = global_corruptor.corrupt_forms(sentence, temp=1.5)
        sentence = global_corruptor.corrupt_capitalization(sentence)
        corrupted_batch.append(sentence)
    return corrupted_batch


def iter_batches(f, max_size):
    batch = []
    for line in f:
        batch.append(line)
        if len(batch) >= max_size:
            yield batch
            batch = []
    if batch:
        yield batch


if __name__ == '__main__':
    import sys, pprint, os.path

    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
    assert os.path.exists(in_filename)
    assert not os.path.exists(out_filename)

    corruptor = Corruptor()
    corruptor.read_data('datasetDaLAJsplit.csv', 'saldom.xml')
    corruptor.compute_statistics([1, 2, 3], [1, 2, 3, 4, 5])

    n_sentences = 0
    with open(in_filename) as f, open(out_filename, 'w') as outf:
        with multiprocessing.Pool(
                initializer=initializer, initargs=[corruptor]) as p:
            for corrupted in p.imap(
                    corrupt_sentences, iter_batches(f, 100), 100):
                for s in corrupted:
                    n_sentences += 1
                    print(s, file=outf)
                    if n_sentences % 10000 == 0:
                        print(time.asctime(), n_sentences, '...', flush=True)
        # Old single-processing code:
        #for sentence in f:
        #    sentence = sentence.strip()
        #    sentence = corruptor.corrupt_word_order(
        #            sentence, p_move=0.1, distance_std=1.5)
        #    sentence = corruptor.corrupt_word_choice(sentence)
        #    sentence = corruptor.corrupt_inflection(
        #            sentence, p_reinflect=0.1, p_split=0.25)
        #    sentence = corruptor.corrupt_forms(sentence, temp=1.5)
        #    sentence = corruptor.corrupt_capitalization(sentence)
        #    print(sentence, file=outf)
        #    n_sentences += 1
        #    if n_sentences % 10000 == 0:
        #        print(time.asctime(), n_sentences, '...', flush=True)
 
