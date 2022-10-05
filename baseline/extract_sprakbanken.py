"""Script to extract plain text from Språkbanken XML data"""

import sys
import os.path

import bz2
from xml.etree import ElementTree as ET

def extract_xml(xml_filename, outf):
    with bz2.open(xml_filename, 'rt', encoding='utf-8') as inf:
        context = ET.iterparse(inf)
        for event_type, element in context:
            if event_type == 'end' and element.tag == 'sentence':
                tokens = [w.text for w in element.iter('w')]
                if tokens:
                    print(' '.join(tokens), file=outf)
            if event_type == 'end' and element.tag in ('sentence', 'text'):
                element.clear()

def main():
    out_filename = sys.argv[1]
    xml_filenames = sys.argv[2:]

    with open(out_filename, 'at', encoding='utf-8') as outf:
        for xml_filename in xml_filenames:
            print('Extracting', os.path.basename(xml_filename), flush=True)
            extract_xml(xml_filename, outf)

if __name__ == '__main__':
    main()

