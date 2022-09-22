import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description='Extract ERRANT-compatible parallel files')
    parser.add_argument(
         '-i', '--input', dest='input_filename', required=True, metavar='FILE',
         help='JSON file from `annotate.py`')
    parser.add_argument(
         '-o', '--original', dest='original_filename', required=True,
         metavar='FILE',
         help='File to be passed as orig_file to ERRANT')
    parser.add_argument(
         '-c', '--corrected', dest='corrected_filename', required=True,
         metavar='FILE',
         help='File to be passed as cor_file to ERRANT')
    parser.add_argument(
         '-r', '--reference', dest='reference_filename',
         metavar='FILE',
         help='Human-corrected version (e.g. for GLEU scoring)')

    args = parser.parse_args()

    with open(args.input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    corrected = []
    original = []
    reference = []

    for item in data:
        corrected.append(item['generated'][0].split('\n\n')[0].strip())
        original.append(item['item'].strip())
        if 'target' in item:
            reference.append(item['target'].strip())

    assert len(reference) in (0, len(original))

    with open(args.original_filename, 'w') as f:
        f.write('\n'.join(original))

    with open(args.corrected_filename, 'w') as f:
        f.write('\n'.join(corrected))

    if args.reference_filename and reference:
        with open(args.reference_filename, 'w') as f:
            f.write('\n'.join(reference))

if __name__ == '__main__':
    main()
