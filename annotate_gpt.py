import openai
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(
            description='Process JSON file with language model')
    parser.add_argument(
        '-i', '--input', dest='input_filename', required=True, metavar='FILE',
        help='JSON file containing `prompt` and `n_tokens` attributes')
    parser.add_argument(
        '-o', '--output', dest='output_filename', required=True,
        metavar='FILE',
        help='JSON file to be written with `generated` attribute added')
    parser.add_argument(
        '--indexes', dest='indexes', metavar='LIST',
        help='Comma-separated list of item indexes to annotate')
    parser.add_argument(
        '-m', '--model', dest='model_name', default='text-babbage-001',
        metavar='MODEL',
        help='OpenAI model name')

    args = parser.parse_args()

    #  'text-babbage-001' # 'text-davinci-002'
    #indexes = [986]
    indexes = [int(s) for s in args.indexes.split(',')] if args.indexes \
            else None

    with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
        openai.api_key = f.read().strip()

    processed_data = []
    with open(args.input_filename) as f:
        data = json.load(f)

        for item in data:
            if indexes is None or item['index'] not in indexes:
                continue
            kwargs = {}
            if 'terminator' in item:
                kwargs['stop'] = [item['terminator']]
            response = openai.Completion.create(
                    model=args.model_name,
                    prompt=item['prompt'],
                    temperature=0,
                    max_tokens=int(item['n_tokens']),
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    **kwargs)
            # Note: the evaluation scripts are currently hard-coded to always
            # use the first item of the list of generated corrections, so we
            # put this in a dummy 1-item list
            item['generated'] = [response['choices'][0]['text']]
            item['model'] = args.model_name
            processed_data.append(item)
            print(f'Annotated item {item["index"]}', flush=True)

    with open(args.output_filename, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4)


if __name__ == '__main__':
    main()

