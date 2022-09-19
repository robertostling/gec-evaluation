import json
import os.path
from collections import OrderedDict
import sys

PROMPTS = {
        'swe1': ('Här är originalmeningen:', 'Den rättade meningen är:'),
        }

EXAMPLE_SETS = {
        'zero': [],
        'two': [
            ('en muket bra sak i Göteborg är den maten alltid farsk',
             'En mycket bra sak med Göteborg är att maten alltid är färsk.'),
            ('om alldrig du har levat med tre barn du inte forstor att '
                'det inte nogon tid är tyst hemma.',
             'Om du aldrig har bott med tre barn så förstår du inte att det '
                'aldrig är tyst hemma.')
            ],
        }

def read_data(dataset):
    filename = os.path.join('data', 'SweLL_test_dev', dataset + '.txt')
    with open(filename) as f:
        return [line.strip() for line in f]


def create_prompt(train_set, test_sentence, prompt_name):
    prompt_item, prompt_ask = PROMPTS[prompt_name]
    examples = '\n\n'.join(f'{prompt_item} {original}\n'
                           f'{prompt_ask} {corrected}'
                           for original, corrected in EXAMPLE_SETS[train_set])
    if examples:
        examples = examples + '\n\n'
    return f'{examples}{prompt_item} {test_sentence}\n{prompt_ask}'


def main():
    prompt_name = sys.argv[1]
    assert prompt_name in PROMPTS
    example_set = sys.argv[2]
    assert example_set in EXAMPLE_SETS

    datasets = [
            ('dev.err', 'dev.cor'),
            ('test.err', 'test.cor'),
            ('levels/test-err-lvlA', 'levels/test-corr-lvlA'),
            ('levels/test-err-lvlB', 'levels/test-corr-lvlB'),
            ('levels/test-err-lvlC', 'levels/test-corr-lvlC'),
            ]

    for err_name, cor_name in datasets:
        assert '-err' in err_name or '.err' in err_name, err_name
        err_data = read_data(err_name)
        cor_data = read_data(cor_name)
        assert len(err_data) == len(cor_data)
        name = os.path.basename(err_name).replace('-err', '').\
                replace('.err', '')

        examples = []
        for i, (err, cor) in enumerate(zip(err_data, cor_data)):
            prompt = create_prompt(example_set, err, prompt_name)
            item = OrderedDict(
                    index=i,
                    item=err,
                    target=cor,
                    terminator='\n\n',
                    n_tokens=8+len(err.split())*3,
                    prompt=prompt)
            examples.append(item)

        print(f'data/{prompt_name}-{example_set}.{name}.json')
        with open(f'data/{prompt_name}-{example_set}.{name}.json', 'w') as f:
            json.dump(examples, f, sort_keys=False, indent=4)



if __name__ == '__main__':
    main()
