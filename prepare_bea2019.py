import json
import os.path
import random
from collections import OrderedDict
from transformers import AutoTokenizer
import sys

import m2


model_name = "EleutherAI/gpt-j-6B"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

PROMPTS = {
        'prompt1': ('Original sentence: ', 'Corrected sentence: '),
        'prompt2': ('This sentence has some issues: ',
                    'A better way to express the sentence would be: ')
        }


def read_data(dataset):
    filename = os.path.join('data', 'wi+locness', 'm2', dataset + '.m2')
    pairs = m2.read_pairs(filename)
    return pairs


def create_prompt(train_data, test_sentence, max_tokens=2000, prompt_name='prompt1'):
    prompt_item, prompt_ask = PROMPTS[prompt_name]
    context = ''
    prompt = ''
    shuffled_data = train_data.copy()
    random.shuffle(shuffled_data)
    while True:
        original, corrected = shuffled_data.pop()
        new_context = (
            context +
            prompt_item + ' '.join(original) + '\n' +
            prompt_ask + ' '.join(corrected) + '\n\n')
        new_prompt = (new_context + prompt_item + ' '.join(test_sentence) +
                      '\n' + prompt_ask)
        # Estimate length of prompt + example + answer, assuming the answer
        # is twice the size of the example.
        # This should be synchronized with the calculation of n_tokens in the
        # main() function.
        expected_answer = (
            new_prompt +
            ' '.join(test_sentence + test_sentence) + '\n\n')
        n_tokens = tokenizer(expected_answer, return_tensors='pt',
                             padding='opt' in model_name).input_ids.shape[1]
        if n_tokens > max_tokens:
            break
        prompt = new_prompt
        context = new_context

    return prompt


def main():
    # Levels to generate data from (typically, all three)
    levels = ('A', 'B', 'C')
    # Levels to use as few-shot examples. Currently C is excluded because they
    # tend to contain few errors.
    train_levels = ('A', 'B')
    prompt_name = sys.argv[1]
    assert prompt_name in PROMPTS

    # Conforming with BEA 2019 guidelines, we are assumed to be unaware of
    # the CEFR level of the text we are correcting. For this reason we mix
    # few-shot examples from all levels deemed suitable for training.
    train = sum(
        [read_data(f'{level}.train.gold.bea19') for level in train_levels], [])

    for level in levels:
        # train = read_data(f'{level}.train.gold.bea19')
        dev = read_data(f'{level}.dev.gold.bea19')
        examples = []
        for i, (original, corrected) in enumerate(dev):
            # Conservative estimate of number of tokens in expected answer
            n_tokens = 2 * tokenizer(
                    ' '.join(original),
                    return_tensors='pt',
                    padding='opt' in model_name).input_ids.shape[1]
            prompt = create_prompt(train, original, prompt_name=prompt_name)
            item = OrderedDict(
                    index=i,
                    item=' '.join(original),
                    target=' '.join(corrected),
                    n_tokens=n_tokens,
                    prompt=prompt
                    )
            examples.append(item)
            print(f'Generated {i+1}/{len(dev)}')

        with open(f'data/{level}-{prompt_name}.dev.gold.bea19.json', 'w') as f:
            json.dump(examples, f, sort_keys=False, indent=4)


if __name__ == '__main__':
    main()
