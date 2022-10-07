import gzip
import re
from bloom_filter2 import BloomFilter

with open('saldo.txt') as f:
    saldo_vocab = set(line.casefold().strip() for line in f)

def clean_sentences(bf, inf, outf, dupf=None, rejf=None, strictness=0):
    re_multipunct = re.compile(r'[.,!?]\s*[.,!?]')
    re_url = re.compile(r'\.(se|nu|com|net|org)')
    blacklist = set(
            'haha iaf <3 :) :D hihi imorrn o oxo va dom å e mej dej go'.split())
    re_forbidden = re.compile(r'''[^a-zåäöüéæø0-9–.,!?():\-“”"/'\s]''')
    re_accept = re.compile(
            r'[–.,!?():\-“”"/]|([a-zåäöüéæø0-9]+(-[a-zåäöüé0-9]+)?(:[a-z]+)?)|'
            r'([0-9]+,[0-9]+)$')
    punct = frozenset('. , ! ? ( ) " “ ” / - –'.split())
    #rejected = set()
    #accepted = set()
    #n_sentences = sum(1 for _ in inf)
    #print(f'Cleaning {n_sentences} sentences...', flush=True)
    #inf.seek(0)
    #bf = BloomFilter(max_elements=n_sentences, error_rate=0.001)
    n_duplicates = 0
    n_invalid = 0
    n_final = 0
    for line in inf:
        line = line.strip()
        line_uncased = line.casefold()
        tokens = line_uncased.split()
        n_accept = 0
        n_reject = 0
        n_oov = 0
        n_upper = 0
        has_multipunct = re_multipunct.search(line_uncased) is not None
        has_url = re_url.search(line_uncased) is not None
        has_forbidden = re_forbidden.search(line_uncased) is not None
        n_blacklisted = 0
        if not (has_multipunct or has_url or has_forbidden):
            n_upper = sum(int(token.isupper()) for token in line.split())
            for token in tokens:
                in_vocab = token in saldo_vocab
                if in_vocab or re_accept.match(token):
                    #accepted.add(token)
                    n_accept += 1
                else:
                    #rejected.add(token)
                    n_reject += 1
                if (not in_vocab) and (token not in punct):
                    n_oov += 1
                if token in blacklist:
                    n_blacklisted += 1
        accept = False
        if strictness == 0:
            # TODO: if modified to use anything detected inside the for loop
            # above, make sure the condition outside the for loop does not get
            # in the way!
            accept = 2 <= len(tokens) <= 60 \
                    and tokens[-1] in punct \
                    and not has_url
        else:
            accept = n_reject < n_accept*0.025 \
                and n_oov < n_accept*0.05 \
                and n_upper < n_accept*0.05 \
                and tokens[-1] in punct \
                and not tokens[0][0].islower() \
                and n_blacklisted == 0 \
                and 2 <= len(tokens) <= 60 \
                and not has_multipunct \
                and not has_url \
                and not has_forbidden
        if accept:
            raw = line_uncased.encode('utf-8')
            if raw in bf:
                n_duplicates += 1
                if dupf is not None:
                    print(line, file=dupf)
            else:
                bf.add(raw)
                print(line, file=outf)
                n_final += 1
        else:
            n_invalid += 1
            if rejf is not None:
                print(line, file=rejf)

    print(f'  {n_duplicates} duplicates and {n_invalid} rejected, '
          f'wrote {n_final}',
            flush=True)
    #for token in sorted(accepted):
    #    print('ACCEPT', token)
    #for token in sorted(rejected):
    #    print('REJECT', token)


def open_any(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')


if __name__ == '__main__':
    import sys
    import os.path
    out_filename = sys.argv[1]
    in_filenames = sys.argv[2:]
    # NOTE: specific to the Swedish data used, where all files with names
    # containing "blog" should be filtered more strictly.
    scrub_extra = ['blog']
    # NOTE: currently hard-coded to the approximate max nr of sentences in the
    # Swedish data we are processing
    bf = BloomFilter(max_elements=300000000, error_rate=0.001)
    with open(out_filename, 'a') as outf:
        for in_filename in in_filenames:
            name = os.path.basename(in_filename)
            strictness = 0
            if any(substr in name for substr in scrub_extra):
                strictness = 1
            print(f'Processing {os.path.basename(in_filename)} with '
                  f'strictness {strictness}...',
                    flush=True)
            with open_any(in_filename) as inf:
                clean_sentences(bf, inf, outf, strictness=strictness)

    #in_filename, out_filename = sys.argv[1:]
    #assert not os.path.exists(out_filename)
    #with open('rejected.txt', 'w') as rejf:
    #    with open('duplicates.txt', 'w') as dupf:      
    #        with open(in_filename) as inf, open(out_filename, 'w') as outf:
    #            clean_sentences(inf, outf, dupf=dupf, rejf=rejf)

