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
    #return ET.fromstring(html.unescape(r.text))
    xml = html.unescape(r.text)
    # NOTE: seems there is something weird with the API, sometimes the final
    # end tag is left out.
    if '</Root>' not in xml:
        xml = xml + '</Root>'

    #print(xml)
    #sys.exit(0)
    try:
        return ET.fromstring(xml), xml
    except ET.ParseError as e:
        print(number_lines(xml), file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)


def correct_text(text):
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

    def to_str():
        return ' '.join(
                form
                for ref, sentence in sentence_contents.items()
                for no, form in sentence.items())

    for s in scrutinizer.findall('s'):
        ref = int(s.get('ref'))
        gramerrors = s.find('gramerrors')
        if gramerrors:
            for gramerror in gramerrors.findall('gramerror'):
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
                    if all(i in sentence_contents[ref]
                           for i in range(begin, end+1)):
                        old = ' '.join(sentence_contents[ref][i]
                                       for i in range(begin, end+1))
                        sentence_contents[ref][begin] = replacement
                        for i in range(begin+1, end+1):
                            del sentence_contents[ref][i]
                        print(f'FIX {ref} {begin}:{end}: {old} --> '
                              f'{replacement}',
                                file=sys.stderr, flush=True)
                        print(f'    {to_str()}', file=sys.stderr, flush=True)
                    else:
                        print('SKIP', file=sys.stderr, flush=True)



    return to_str()


def main():
    with open(sys.argv[1]) as f:
        for sentence in f:
            corrected = correct_text(sentence.strip())
            print(corrected)


if __name__ == '__main__':
    main()

