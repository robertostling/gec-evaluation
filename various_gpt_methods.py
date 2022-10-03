import openai
import os
import argparse
import time

SWE_PRELUDE = 'Dessa meningar är skrivna av en elev som lär sig svenska. ' \
              'Meningarna är rättade av en lärare. Läraren har ändrat så ' \
              'lite som möjligt i meningarna.\n\n'

SWE_EXAMPLES = [
        ('föra vecka jag har fått ett brev från dig och du hade sagt du är liten huvudvärk . är du mår bra nu ?',
         'Förra veckan fick jag ett brev från dig där du sade att du har lite huvudvärk . Mår du bra nu ?'),

        ('På andra sidan mycket lättare man hitar bostad hit en på gransteder , man kan resa gratis med kollektivt trafik bra hela kommunen .',
         'Å andra sidan är det mycket lättare att hitta bostad här än i grannstäderna . Man kan resa gratis med bra kollektivtrafik i hela kommunen .'),

        ('Livet är hård man måste kämpa för att man leva bättra .',
         'Livet är hårt , man måste kämpa för att kunna leva bättre .'),

        ('Kvinnorna måste jobba och skät barn i samtid .',
         'Kvinnorna måste jobba och sköta barn samtidigt .'),

        ('Det är svårt att ge råd för någon, om man har själv ekonomiska '
         'problem .',
         'Det är svårt att ge råd till någon om man själv har ekonomiska '
         'problem .'),
        ]

SWE_ENG_EXAMPLES = [
        ('föra vecka jag har fått ett brev från dig och du hade sagt du är '
         'liten huvudvärk . är du mår bra nu ?',
         'Last week I received a letter from you where you said that you '
         'have a slight headache . Are you feeling well now ?'),

        ('På andra sidan mycket lättare man hitar bostad hit en på '
         'gransteder , man kan resa gratis med kollektivt trafik bra hela '
         'kommunen .',
         'On the other hand it is much easier to find housing here than in '
         'neighboring towns . You can travel for free with good public transit '
         'in the whole municipality .'),
        ]

ENG_SWE_MT = [
        ('You have written that you will move to Stockholm , and you want '
         'to know how it is to live here .',
         'Du har skrivit att du ska flytta till Stockholm , och du vill '
         'veta hur det är att bo här .'),
        ('For instance you have to pay more than 4000 crows for a one-room '
         'apartment if you live near the city , and it is difficult to find '
         'an apartment where you would like to live .',
         'T.ex. får du betala mer än 4000:- för en etta om du bor nära stan ,'
         'och det är svårt att hitta en lägenhet där du vill bo .'),
        ]

def openai_request(args, prompt, max_tokens):
    """Greedy LM generation request"""
    time.sleep(args.delay)
    response = openai.Completion.create(
            model=args.model_name,
            prompt=prompt,
            temperature=0,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0)
    return ' '.join(response['choices'][0]['text'].strip().split())


def process_sentence(line, args, logf):
    if args.method_name in ('swe-p2s', 'swe-2s', 'swe-p5s'):
        if '2' in args.method_name:
            n = 2
        elif '5' in args.method_name:
            n = 5
        else:
            raise NotImplementedError(args.method_name)
        # NOTE: changed from ' '.join(...) after Nyberg.CEFR_A.manual_test.ps5
        prompt = ''.join(
                     f'Elevens text: {SWE_EXAMPLES[i][0]}\n' \
                     f'Rättad text: {SWE_EXAMPLES[i][1]}\n\n'
                     for i in range(n)) + \
                 f'Elevens text: {line}\n' \
                 f'Rättad text:'
        if '-p' in args.method_name:
            prompt = SWE_PRELUDE + prompt
        result = openai_request(args, prompt, 50+3*len(line.split()))
        print(prompt + '<<<' + result + '>>>', file=logf, flush=True)
        return result
    elif args.method_name == 'eng-zs':
        prompt = f'Original sentence: {line}\nCorected sentence:'
        result = openai_request(args, prompt, 50+3*len(line.split()))
        print(prompt + '<<<' + result + '>>>', file=logf, flush=True)
        return result
    elif args.method_name == 'swe-eng-swe-2s':
        prompt1 = ' '.join(
                     f'Elevens text på svenska: {SWE_ENG_EXAMPLES[i][0]}\n' \
                     f'The text in correct English: {SWE_ENG_EXAMPLES[i][1]}\n\n'
                     for i in range(2)) + \
                 f'Elevens text på svenska: {line}\n' \
                 f'The text in correct English:'
        eng_result = openai_request(args, prompt1, 50+3*len(line.split()))
        # TODO: version where the original Swedish is included as a hint
        prompt2 = ' '.join(
                     f'English: {ENG_SWE_MT[i][0]}\n' \
                     f'Swedish: {ENG_SWE_MT[i][1]}\n\n'
                     for i in range(2)) + \
                 f'English: {eng_result}\n' \
                 f'Swedish:'
        result = openai_request(args, prompt2, 50+3*len(eng_result.split()))
        print(eng_result, file=logf, flush=True)
        #print(prompt1 + '<<<' + eng_result + '>>>\n', file=logf)
        #print(prompt2 + '<<<' + result + '>>>', file=logf)
        #print('-'*72, file=lofg, flush=True)
        return result
    else:
        raise NotImplementedError(f'Unknown method ({args.method_name})')


def main():
    parser = argparse.ArgumentParser(
            description='GEC with GPT-3 at OpenAI')
    parser.add_argument(
        '-i', '--input', dest='input_filename', required=True, metavar='FILE',
        help='Input text file containing one sentence per line.')
    parser.add_argument(
        '-o', '--output', dest='output_filename', required=True,
        metavar='FILE',
        help='Output text file containing one sentence per line.')
    parser.add_argument(
        '--log', dest='log_filename', metavar='FILE', required=True,
        help='Additional information will be written to this file.')
    #parser.add_argument(
    #    '--add-skipped', dest='add_skipped', action='store_true',
    #    help='Add all items to output, including ones not annotated')
    parser.add_argument(
        '--method', dest='method_name', required=True, metavar='NAME',
        help='Method to use (see process_sentence)')
    parser.add_argument(
        '--model', dest='model_name', required=True, metavar='NAME',
        help='OpenAI model name (e.g.: text-babbage-001, text-davinci-002')
    parser.add_argument(
        '--delay', dest='delay', default=4.0, metavar='X', type=float,
        help='Delay in seconds between OpenAI API requests')

    args = parser.parse_args()

    assert os.path.exists(args.input_filename)
    assert not os.path.exists(args.output_filename)

    with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
        openai.api_key = f.read().strip()

    with open(args.input_filename) as f:
        input_lines = [line.strip() for line in f]

    with open(args.output_filename, 'w') as f, \
         open(args.log_filename, 'w') as logf:
        for i, input_line in enumerate(input_lines):
            output_line = process_sentence(input_line, args, logf)
            print(output_line, file=f, flush=True)
            print(f'{i+1}/{len(input_lines)}...', flush=True)

if __name__ == '__main__':
    main()

