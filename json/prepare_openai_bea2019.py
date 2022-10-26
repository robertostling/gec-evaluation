import json
import os.path
from collections import OrderedDict
import sys

import m2

#model_name = 'text-babbage-001' # 'text-davinci-002'

PROMPTS = {
        'prompt1': ('Original sentence:', 'Corrected sentence:'),
        }

# Many corrections:
#9, 11, 18, 33, 130, 259, 644, 714, 824, 946,
# Without corrections:
#679, 704,
EXAMPLE_SETS = {
        'zero': {},
        'four': {
            'A.train.gold.bea19': [9, 11, 679, 704],
            },
        'six': {
            'A.train.gold.bea19': [9, 679, 11, 644, 704, 259],
            },
        }

def read_data(dataset):
    filename = os.path.join('data', 'wi+locness', 'm2', dataset + '.m2')
    pairs = m2.read_pairs(filename)
    return pairs


def create_prompt(train_data, test_sentence, prompt_name='prompt1'):
    prompt_item, prompt_ask = PROMPTS[prompt_name]
    examples = '\n\n'.join(f'{prompt_item} {" ".join(original)}\n'
                           f'{prompt_ask} {" ".join(corrected)}'
                           for original, corrected in train_data)
    return (examples + f'\n\n{prompt_item} {" ".join(test_sentence)}\n' +
            prompt_ask)


def main():
    prompt_name = sys.argv[1]
    assert prompt_name in PROMPTS
    example_set = sys.argv[2]
    assert example_set in EXAMPLE_SETS

    train_data = []
    for dataset, indexes in EXAMPLE_SETS[example_set].items():
        pairs = read_data(dataset)
        for i in indexes:
            train_data.append(pairs[i])

    # Levels to generate data from (typically, all three)
    levels = ('A', 'B', 'C')

    #with open('prompts/eng-test1.corrupted') as f1:
    #    with open('prompts/eng-test1.target') as f2:
    #        train = list(zip(map(str.split, f1), map(str.split, f2)))

    examples = []
    with open('data/ABCN.test.bea19.orig', 'r') as f:
        test = [line.strip() for line in f]
        print(f'{len(test)} sentences in official test set')
        for i, original in enumerate(test):
            original = original.split()
            prompt = create_prompt(
                    train_data, original, prompt_name=prompt_name)
            item = OrderedDict(
                    index=i,
                    item=' '.join(original),
                    terminator='\n\n',
                    n_tokens=len(original)*2,
                    prompt=prompt)
            examples.append(item)

    with open(f'data/{prompt_name}-{example_set}.test.bea19.json', 'w') as f:
        json.dump(examples, f, sort_keys=False, indent=4)


    for level in levels:
        dev = read_data(f'{level}.dev.gold.bea19')
        examples = []
        for i, (original, corrected) in enumerate(dev):
            prompt = create_prompt(
                    train_data, original, prompt_name=prompt_name)
            item = OrderedDict(
                    index=i,
                    item=' '.join(original),
                    target=' '.join(corrected),
                    terminator='\n\n',
                    n_tokens=len(original)*2,
                    prompt=prompt)
            examples.append(item)

        with open(
                f'data/{level}-{prompt_name}-few.dev.gold.bea19.json',
                'w') as f:
            json.dump(examples, f, sort_keys=False, indent=4)


if __name__ == '__main__':
    main()
