"""Script to extract plain text from Språkbanken XML data"""

import sys
import os
import multiprocessing
import re

import bz2
from xml.etree import ElementTree as ET

def extract_xml_re(xml_filename, outf):
    re_w = re.compile(r'>([^<>]+)</w>')
    sentence = []
    with bz2.open(xml_filename, 'rt', encoding='utf-8') as inf:
        for line in inf:
            if line.startswith('</sentence>'):
                print(' '.join(sentence), file=outf)
                sentence = []
            elif line.startswith('<w '):
                m = re_w.search(line)
                if m is None:
                    print(f'WARNING: "{line}"')
                if line.endswith('</w>\n'):
                    line = line[:-5]
                    i = line.rfind('>')
                    if i >= 0:
                        sentence.append(line[i+1:])
                #sentence.append(m.group(1))

# NOTE: due to XML errors in Språkbanken's Wikipedia corpus, this version
# fails. Use the regular expression version above instead.
def extract_xml(xml_filename, outf):
    with bz2.open(xml_filename, 'rt', encoding='utf-8') as inf:
        context = ET.iterparse(inf)
        for event_type, element in context:
            if event_type == 'end' and element.tag == 'sentence':
                tokens = [w.text for w in element.iter('w')]
                if tokens and not (None in tokens):
                    print(' '.join(tokens), file=outf)
            if event_type == 'end' and element.tag in ('sentence', 'text'):
                element.clear()

def extract_wrapper(xml_filename, out_path):
    name = os.path.basename(xml_filename).split('.')[0]
    out_filename = os.path.join(out_path, f'{name}.txt')
    temp_filename = os.path.join(out_path, f'{name}.txt.tmp')
    if os.path.exists(out_filename):
        print(f'Skipping {name}', flush=True)
        return
    try:
        with open(temp_filename, 'w', encoding='utf-8') as outf:
            print(f'Extracting {name}...', flush=True)
            extract_xml_re(xml_filename, outf)
        os.rename(temp_filename, out_filename)
    except ET.ParseError:
        print(f'XML parser error in {name}! Skipping.', flush=True)
        os.remove(temp_filename)


def main():
    out_path = sys.argv[1]
    xml_filenames = sys.argv[2:]
    assert os.path.isdir(out_path)

    with multiprocessing.Pool() as p:
        p.starmap(extract_wrapper, [(fn, out_path) for fn in xml_filenames])

if __name__ == '__main__':
    main()

