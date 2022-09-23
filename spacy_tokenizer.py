import json
import sys
import os.path

import spacy

model_name = sys.argv[1] # 'en_core_web_sm'
nlp = spacy.load(model_name)

def fix_overtokenization(s):
    return s.replace("' ve ", " 've ")

for text in sys.stdin.readlines():
    doc = nlp.tokenizer(text.strip())
    tokenized = ' '.join(t.text for t in doc).strip()
    tokenized = fix_overtokenization(tokenized)
    print(tokenized)

