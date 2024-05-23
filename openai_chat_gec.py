"""
Simple one-shot English Grammatical Error Correction system.

This is compatible with the most recent (as of 2024-05-23) OpenAI API.
"""

import openai
import os
import argparse
import time


with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
    client = openai.OpenAI(api_key=f.read().strip())


SYSTEM_STR = "Please correct the following sentence to make it " \
             "sound natural and fluent to a native speaker of " \
             "English. You should fix grammatical mistakes, " \
             "awkward phrases, spelling errors, etc. following " \
             "standard written usage conventions, but your " \
             "edits must be conservative. Please keep the " \
             "original sentence (words, phrases, and structure) " \
             "as much as possible. Keep the spaces that exist " \
             "around punctuation, and do not write anything except " \
             "the corrected sentence."

N_SHOT = [
        ("We can use the words as a method to socially categorizing , "
         "that is making individuals as members of a group from "
         "social connections .",
         "We can use these words as a means of social categorization , "
         "that is , marking individuals as members of a group defined by "
         " social connections .")
        ]


def correct_sentences(args, input_sentences):
    output_sentences = []
    for i, input_sentence in enumerate(input_sentences):
        print(f'{i+1} of {len(input_sentences)}...', flush=True)
        response = client.chat.completions.create(
                model=args.model_name,
                seed=args.seed,
                temperature=args.temperature,
                messages=[
                    {"role": "system",
                     "content": SYSTEM_STR},
                    {"role": "user",
                     "content": N_SHOT[0][0]},
                    {"role": "assistant",
                     "content": N_SHOT[0][1]},
                    {"role": "user",
                     "content": input_sentence},
                    ])
        output_sentence = ''
        if response.choices[0].finish_reason == 'stop':
            output_sentence = response.choices[0].message.content
        output_sentences.append(output_sentence)
        time.sleep(args.delay)
    return output_sentences


def main():
    parser = argparse.ArgumentParser(
            description='Grammatical Error Correction with OpenAI')
    parser.add_argument(
        '-i', '--input', dest='input_filename', required=True, metavar='FILE',
        help='Input text file containing one sentence per line.')
    parser.add_argument(
        '-o', '--output', dest='output_filename', required=True,
        metavar='FILE',
        help='Output text file containing one sentence per line.')
    parser.add_argument(
        '--model', dest='model_name', required=True, metavar='NAME',
        help='OpenAI model name (e.g.: gpt-4o)')
    parser.add_argument(
        '--seed', required=False, metavar='N', default=123,
        help='Random seed for reproducibility (default: 123)')
    parser.add_argument(
        '--temperature', required=False, metavar='X', default=0,
        help='Generation temperature (default: 0)')
    parser.add_argument(
        '--delay', dest='delay', default=4.0, metavar='X', type=float,
        help='Delay in seconds between OpenAI API requests')

    args = parser.parse_args()

    assert os.path.exists(args.input_filename)
    assert not os.path.exists(args.output_filename)

    with open(args.input_filename) as f:
        input_lines = [line.strip() for line in f]

    output_lines = correct_sentences(args, input_lines)

    with open(args.output_filename, 'w') as f:
        for line in output_lines:
            print(line, file=f)


if __name__ == '__main__':
    main()
