# few-shot-gec
Experiments with few-shot learning for Grammatical Error Correction

Currently the GPT-J 6B model is used, with BEA 2019 shared task data
(W&I+LOCNESS v2.1).

## Quick start

Note that `prepare_bea2019.py` uses the `transformers` library, so at this step you need to have its dependencies available. See `annotate.sh` for how to do
this on Alvis (load the right modules and activate the Python venv).

    # Download and unpack BEA 2019 shared task data
    ./download.sh
    # Generate a JSON file with prompts and other data
    python3 prepare_bea2019.py prompt1
    # Use GPT-J to generate corrections, which are added as extra `generated`
    # attributes to the input data and written to a new JSON file
    sbatch annotate.sh --input data/A-prompt1.dev.gold.bea19.json \
        --output data/A-prompt1.dev.gold.bea19.annotated.json 
    # Extract pairs of original/corrected sentences for ERRANT
    python3 extract_parallel.py \
        -i data/A-prompt1.dev.gold.bea19.annotated.json \
        -o data/original -c data/corrected
    # Tokenize and prepare the m2 format required for ERRANT scoring
    errant_parallel -tok -orig data/original -cor data/corrected \
        -out data/out.m2
    # Perform ERRANT scoring
    errant_compare -hyp data/out.m2 -ref data/wi+locness/m2/A.dev.gold.bea19.m2

On other systems you may be able to run `annotate.py` directly instead of
`annotate.sh`. The command-line arguments are identical.

## Important files

 * `prepare_bea2019.py` generates JSON files of the format expected by `annotate.py`   using data from the BEA 2019 shared task.
 * `annotate.py` annotates each element of a JSON file with the `generated`
   attribute, by generating `n_tokens` new tokens after `prompt`.
 * `annotate.sh` is a SLURM script to run `annotate.py` on Alvis.
 * `download.sh` is a shell script to download and unpack the W&I+LOCNESS v2.1
   data from BEA 2019.
 *  `extract_parallel.py` extract original/corrected pairs from the output of
    `annotate.py` into a format suitable for ERRANT scoring
