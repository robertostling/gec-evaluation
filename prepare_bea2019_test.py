import json
import sys
import os.path

import spacy

input_filename = sys.argv[1]
output_filename = sys.argv[2]

assert os.path.exists(input_filename)
assert not os.path.exists(output_filename)

nlp = spacy.load('en_core_web_sm')

with open(input_filename) as f:
    data = json.load(f)

with open(output_filename, 'w') as f:
    for item in data:
        if 'generated' not in item:
            print(f'Item {item["index"]} lacks generated text')
            continue
        text = item['generated'][0]
        doc = nlp.tokenizer(text)
        tokenized = ' '.join(t.text for t in doc).strip()
        print(tokenized, file=f)

