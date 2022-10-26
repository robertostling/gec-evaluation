import csv
from collections import Counter

import Levenshtein
import spacy

def ngrams(tokens, n):
    for i in range(len(tokens)-n+1):
        yield tokens[i:i+n]


class Dalaj:
    def __init__(self):
        pass

    def read_data(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = list(reader)

    def compute_statistics(self, ns):
        nlp = spacy.load('sv_core_news_md')
        #nlp.tokenizer = nlp.tokenizer.tokens_from_list

        self.source_ngram_freq = {n: Counter() for n in ns}
        self.target_ngram_freq = {n: Counter() for n in ns}
        self.ngram_substitutions = Counter()
        self.inflect_substitutions = Counter()
        self.tag_substitutions = Counter()
        self.source_tag_freq = Counter()
        self.target_tag_freq = Counter()
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
            source_doc = nlp(source)
            target_doc = nlp(target)
            self.ngram_substitutions[(source_toks, target_toks)] += 1
            self.source_tag_freq.update(token.tag_ for token in source_doc)
            self.target_tag_freq.update(token.tag_ for token in target_doc)
            source_annotated = [token for token in source_doc
                                if token.idx == err_idx[0]]
            target_annotated = [token for token in target_doc
                                if token.idx == cor_idx[0]]
            source_sent = tuple(row['original sentence'].split())
            target_sent = tuple(row['corrected sentence'].split())
            if source_annotated and target_annotated:
                source_token = source_annotated[0]
                target_token = target_annotated[0]
                self.tag_substitutions[(
                    source_token.tag_, target_token.tag_)] += 1
                if source_token.lemma_ == target_token.lemma_:
                    self.inflect_substitutions[(
                        source_token.tag_, target_token.tag_)] += 1
            for n in ns:
                self.source_ngram_freq[n].update(ngrams(source_sent, n))
                self.target_ngram_freq[n].update(ngrams(target_sent, n))


if __name__ == '__main__':
    import sys, pprint
    dalaj = Dalaj()
    dalaj.read_data(sys.argv[1])
    dalaj.compute_statistics([1, 2, 3])

    print('REPLACEMENTS')
    for (source_tag, target_tag), n in dalaj.tag_substitutions.most_common():
        print(source_tag, target_tag, n)

    print('INFLECTIONS')
    for (source_tag, target_tag), n in dalaj.inflect_substitutions.most_common():
        print(source_tag, target_tag, n)

    for (source, target), n in dalaj.ngram_substitutions.most_common():
        if max(len(source), len(target)) > 3:
            continue
        print(source, dalaj.source_ngram_freq[len(source)][source],
              target, dalaj.target_ngram_freq[len(target)][target],
              n)

    letter_confusion = Counter()
    for (source, target), n in dalaj.ngram_substitutions.most_common():
        source = ' '.join(source)
        target = ' '.join(target)
        nld = Levenshtein.distance(source, target) \
                / max(len(source), len(target))
        if nld < 0.5:
            ops = Levenshtein.editops(source, target)
            print(round(nld, 3), source, target)
            for op,i,j in ops:
                if op == 'replace':
                    c_source = source[i].casefold()
                    c_target = target[j].casefold()
                    letter_confusion[(c_source, c_target)] += 1
    pprint.pprint(letter_confusion.most_common())
