"""Script to correct text files using Granska's API

It works by passing the input file, line by line, to Granska's API. Each line
is passed as many times as needed (up to 5) to implement all the suggested
changes. At each iteration, changes are applied in order of increasing span
length, and newer changes that overlap with older ones are saved for the next
iteration.

Usage:
    python3 granska.py input.txt >output.txt 2>log.txt

The log file can be used to diagnose problems, because the API has some quirks
and I am not certain this code covers all corner cases.
"""

import sys
import html
from collections import OrderedDict
import xml.etree.ElementTree as ET

import requests


# NOTE: the API does not correctly escape text, so e.g. quotation marks
# and ampersand can cause invalid XML output. We work aronud this by
# translating XML metacharacters to obscure unicode versions, and back.
hack_table = {
        '<': '〈',
        '>': '〉',
        '"': '”',
        '&': '⅋'}
unhack_table = {v: k for k, v in hack_table.items()}


def number_lines(text):
    lines = text.split('\n')
    return '\n'.join(f'{i+1:4d}  {line}' for i, line in enumerate(lines))


def check_text(text):
    text = ''.join(hack_table.get(c, c) for c in text)
    r = requests.post(
            'https://skrutten.csc.kth.se/granskaapi/scrutinize.php',
            data={'text': text})
    xml = html.unescape(r.text)
    # NOTE: seems there is something weird with the API, sometimes the final
    # end tag is left out.
    if '</Root>' not in xml:
        xml = xml + '</Root>'

    # print(xml)
    # sys.exit(0)
    try:
        return ET.fromstring(xml), xml
    except ET.ParseError as e:
        print(number_lines(xml), file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)


def correct_text(text):
    """Correct a text (may be a single sentence) using Granska's API

    The text will be passed through the Granska API once. Use
    correct_text_iterative() if you want to iteratively call Granska until
    no further changes are made. This function handles overlapping suggestions
    for changes by accepting the smallest one, and thus may under-correct.

    Args:
        text -- str containing text to be corrected

    Returns:
        tuple(
            int n_corrections
            str containing space-separated tokens of corrected text)
    """
    root, xml = check_text(text)
    sentence_contents = OrderedDict()
    for s in root.findall('s'):
        ws = OrderedDict()
        sentence_contents[int(s.get('ref'))] = ws
        contents = s.find('contents')
        for w in contents.findall('w'):
            token = ''.join(unhack_table.get(c, c) for c in w.text)
            ws[int(w.get('no'))] = token
    scrutinizer = root.find('scrutinizer')
    n_corrections = 0
    modified = set()

    def to_str():
        return ' '.join(
                form
                for ref, sentence in sentence_contents.items()
                for no, form in sentence.items())

    def gramerror_length(gramerror):
        marked_section = gramerror.find('marked_section')
        mark = marked_section.find('mark')
        begin = int(mark.get('begin')) - 2
        end = int(mark.get('end')) - 2
        return 1+end-begin
 
    for s in scrutinizer.findall('s'):
        ref = int(s.get('ref'))
        gramerrors = s.find('gramerrors')
        if gramerrors:
            gramerror_list = sorted(
                    gramerrors.findall('gramerror'),
                    key=gramerror_length)
            for gramerror in gramerror_list:
                marked_section = gramerror.find('marked_section')
                mark = marked_section.find('mark')
                begin = int(mark.get('begin')) - 2
                end = int(mark.get('end')) - 2
                suggestions = gramerror.find('suggestions')
                if suggestions:
                    top_suggestion = suggestions.find('sugg')
                    replacement = ''.join(top_suggestion.itertext())
                    # If this span or parts of it has been fixed previously,
                    # do not modify it again.
                    if all(((i in sentence_contents[ref]) and
                             (i not in modified))
                            for i in range(begin, end+1)):
                        n_corrections += 1
                        old = ' '.join(sentence_contents[ref][i]
                                       for i in range(begin, end+1))
                        sentence_contents[ref][begin] = replacement
                        modified |= set(range(begin, end+1))
                        for i in range(begin+1, end+1):
                            del sentence_contents[ref][i]
                        print(f'FIX {ref} {begin}:{end}: {old} --> '
                              f'{replacement}',
                                file=sys.stderr, flush=True)
                        print(f'    {to_str()}', file=sys.stderr, flush=True)
                    else:
                        print('SKIP', file=sys.stderr, flush=True)

    return n_corrections, to_str()


def correct_text_iterative(text, max_iter=5):
    """Correct text by iteratively passing it through Granska.

    Args:
        text -- str: text to correct
        max_iter -- int: maximum number of passes

    Returns:
        str: corrected text as space-separated tokens
    """
    for i in range(max_iter):
        n_corrections, text = correct_text(text)
        print(f'ITERATION {i} fixed {n_corrections} errors',
                file=sys.stderr, flush=True)
        if n_corrections == 0:
            break
    return text


def main():
    with open(sys.argv[1]) as f:
        for sentence in f:
            corrected = correct_text_iterative(sentence.strip())
            print(corrected)


if __name__ == '__main__':
    main()

