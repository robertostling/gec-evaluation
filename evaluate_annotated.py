import argparse
import json
import os

import m2


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate a JSON file from annotate.py to an m2 reference')
    parser.add_argument(
         '-i', '--input', dest='input_filename', required=True, metavar='FILE',
         help='JSON file from `annotate.py`')
    parser.add_argument(
         '-r', '--reference', dest='reference_filename', required=True,
         metavar='FILE',
         help='m2 file with error annotations')

    args = parser.parse_args()

    with open(args.input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    annotated_indexes = [
            item['index'] for item in data
            if 'generated' in item]

    # This will be used to store m2 annotations for *only* the subset of
    # sentences annotated in the JSON file
    temp_ref_m2_filename = 'temp_ref.m2'

    # This will be used to store m2 annotations for the system being
    # evaluated, with data extracted from the input JSON file and passed
    # through errant_parallel
    temp_cor_m2_filename = 'temp_cor.m2'

    # Temporary plain-text files used by errant_parallel
    temp_orig_filename = 'temp_orig.txt'
    temp_cor_filename = 'temp_cor.txt'
    # And this one is used for GLEU
    temp_ref_filename = 'temp_ref.txt'

    corrected = []
    original = []
    reference = []

    for item in data:
        if 'generated' in item:
            if isinstance(item['generated'], list):
                generated = item['generated'][0]
            else:
                generated = item['generated']
            corrected.append(generated.split('\n\n')[0].strip())
            original.append(item['item'].strip())
            reference.append(item['target'].strip())

    with open(temp_orig_filename, 'w') as f:
        f.write('\n'.join(original))

    with open(temp_cor_filename, 'w') as f:
        f.write('\n'.join(corrected))

    with open(temp_ref_filename, 'w') as f:
        f.write('\n'.join(reference))

    os.system(
            f'errant_parallel -tok -orig {temp_orig_filename} '
            f'-cor {temp_cor_filename} -out {temp_cor_m2_filename}')

    with open(args.reference_filename) as f:
        m2_sentences = f.read().split('\n\n')

    with open(temp_ref_m2_filename, 'w') as f:
        for i in annotated_indexes:
            f.write(m2_sentences[i] + '\n\n')

    os.system(
            f'errant_compare -hyp {temp_cor_m2_filename} '
            f'-ref {temp_ref_m2_filename}')

    os.system(
            f'python gleu_py3/compute_gleu -s {temp_orig_filename} '
            f'-r {temp_ref_filename} -o {temp_cor_filename} -n 4')

    print('No-corrections baseline:')
    os.system(
            f'python gleu_py3/compute_gleu -s {temp_orig_filename} '
            f'-r {temp_ref_filename} -o {temp_orig_filename} -n 4')


if __name__ == '__main__':
    main()
