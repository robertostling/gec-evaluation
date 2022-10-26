from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import logging
import argparse
from collections import OrderedDict


def load_model(model_name, precision):
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    pad_token_id = tokenizer.pad_token_id \
        if tokenizer.pad_token_id \
        else tokenizer.eos_token_id

    if precision == 16:
        model_revision = 'float16'
        torch_dtype = torch.float16
    elif precision == 32:
        model_revision = 'float32'
        torch_dtype = torch.float32
    else:
        raise NotImplementedError(f'Precision {precision} not implemented')

    model = AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=model_revision,
            torch_dtype=torch_dtype,
            pad_token_id=pad_token_id).cuda()

    if "max_position_embeddings" in model.config.__dict__.keys():
        model_max_length = model.config.max_position_embeddings
    elif "n_positions" in model.config.__dict__.keys():
        model_max_length = model.config.n_positions
    else:
        raise ValueError

    return model, tokenizer, model_max_length, pad_token_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Process JSON file with language model')
    parser.add_argument(
        '-l', '--log', dest='log_filename', metavar='FILE',
        help='Output log file')
    parser.add_argument(
        '-i', '--input', dest='input_filename', required=True, metavar='FILE',
        help='JSON file containing `prompt` and `n_tokens` attributes')
    parser.add_argument(
        '-o', '--output', dest='output_filename', required=True,
        metavar='FILE',
        help='JSON file to be written with `generated` attribute added')
    parser.add_argument(
        '-m', '--model', dest='model', default='EleutherAI/gpt-j-6B',
        metavar='MODEL',
        help='Huggingface model name (WARNING: beware of hardcoded models in '
             'prepare_bea2019.py)')
    parser.add_argument(
        '-s', '--subsample', dest='subsample', type=int, default=None,
        metavar='N',
        help='If given, only process every Nth item')
    parser.add_argument(
        '-p', '--precision', dest='model_precision', type=int, default=16,
        metavar='N', choices={16, 32},
        help='Number of bits of precision for the language model')
    parser.add_argument(
        '--beam-size', dest='beam_size', type=int, default=1,
        metavar='N',
        help='Beam size for generation (defaults to greedy search)')
    parser.add_argument(
        '--n-sequences', dest='n_sequences', type=int, default=1,
        metavar='N',
        help='Number of returned sequences for each item')
    parser.add_argument(
        '--temperature', dest='temperature', type=float, default=0.0,
        metavar='T',
        help='Temperature parameter (non-zero value enables random sampling)')
    parser.add_argument(
        '--top-p', dest='top_p', type=float, default=1.0,
        metavar='X',
        help='Nucleus sampling parameter')

    args = parser.parse_args()

    with open(args.input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    if args.log_filename:
        logging.basicConfig(
                format='%(asctime)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO,
                handlers=[logging.FileHandler(args.log_filename, mode="w"),
                          logging.StreamHandler()])
        logger = logging.getLogger()
    else:
        logger = logging.getLogger()
        logger.disabled = True

    model_name = args.model

    model, tokenizer, model_max_length, pad_token_id = load_model(
        model_name,
        args.model_precision)

    processed_data = []
    for item_no, item in enumerate(data):
        if args.subsample and (item_no % args.subsample != 0):
            continue
        n_tokens = item['n_tokens']
        input_ids = tokenizer(item['prompt'],
                              return_tensors="pt",
                              padding="opt" in model_name).input_ids.cuda()

        logging.info(f'Processing example {item_no+1}/{len(data)} with '
                     f'{input_ids.shape[1]} tokens')

        generated_ids = model.generate(
                input_ids,
                num_beams=args.beam_size,
                do_sample=(args.temperature != 0 or args.top_p != 1),
                temprature=args.temperature,
                num_return_sequences=args.n_sequences,
                max_length=input_ids.shape[1] + n_tokens,
                pad_token_id=pad_token_id)

        generated_texts = [
            tokenizer.decode(
                ids[input_ids.shape[1]:],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True)
            for ids in generated_ids]

        # This may be e.g. "\n\n" and anything after that is cut off
        if 'terminator' in item:
            generated_texts = [
                    text.split(item['terminator'])[0]
                    for text in generated_texts]

        item['generated'] = generated_texts
        item.move_to_end('prompt')
        processed_data.append(item)

    torch.cuda.empty_cache()

    with open(args.output_filename, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4)
