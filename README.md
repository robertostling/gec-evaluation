# few-shot-gec
Experiments with few-shot learning for Grammatical Error Correction

## Anontation

The [annotation tool](./annotator/) is a simple tkinter-based Python
program which is used for quality estimation of GEC system output.
There is also a script to 

For this project we store annotations in the [annotations/](./annotations)
subdirectory.

## Evaluation

The main GLEU evaluation script can be run like this:

    evaluation/evaluate_experiments.sh

The [evaluation/](./evaluation/) subdirectory contains a GLEU scoring script (adapted for
Python 3), a SLURM script for Scribendi score evaluation, and an ERRANT + GLEU
evaluation wrapper for the
[JSON format used below](#few-shot-with-user-defined-prompts).

## NMT based baseline system

The [baseline/](./baseline) subdirectory contains a baseline system, using
OpenNMT trained on large amounts of text where the source has been corrupted
using a method for producing "L2-like" errors.

## Few-shot with OpenAI

The script `openai_fewshot.py` is used for most experiments currently. It uses
a simple one-sentence-per-line input and output format, and features some
built-in prompts for Swedish and English.

## Granska

The script `granska.py` uses the public API of the Swedish
[GEC system Granska](https://www.csc.kth.se/tcs/projects/granska/) to produce
corrected versions of texts. Note that the API is mainly meant for providing
student feedback, and not all errors will be taken into account. This applies
when no alternative is suggested by Granska, or when overlapping alternatives
are suggested.

## Few-shot with user-defined prompts

Note that this part of the repository is not currently used, and is kept here
in case it is needed in the future.

This collection of scripts are based on a common JSON-based file format,
containing queries ready to be dispatched to different language models.

Currently the GPT-J 6B model is used, with BEA 2019 shared task data
(W&I+LOCNESS v2.1). Optionally one can also use GPT-3 via OpenAI's API.

See the [json/](./json/) subdirectory for more information.


