from xml.etree import ElementTree as ET

saldom = ET.parse('saldom.xml')
tokens = set()
for lexicalentry in saldom.iter('LexicalEntry'):
    lemma = lexicalentry.find('Lemma')
    #fr = lemma.find('FormRepresentation')
    #feats = {feat.get('att'): feat.get('val')
    #        for feat in fr.findall('feat')}
    #if feats['partOfSpeech'] not in ('nn', 'vb', 'av'):
    #   continue
    for wordform in lexicalentry.findall('WordForm'):
        feats = {feat.get('att'): feat.get('val')
                 for feat in wordform.findall('feat')}
        if not (feats['msd'].startswith('c') or feats['msd'] == 'sms'):
            for token in feats['writtenForm'].split():
                tokens.add(token)

for token in sorted(tokens):
    print(token)

