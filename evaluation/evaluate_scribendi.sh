#!/usr/bin/env bash
#SBATCH -A SNIC2021-7-121 -p alvis
#SBATCH --gpus-per-node=A40:1
#SBATCH -t 0-02:00:00
#SBATCH --output=scribendi.out

# NOTE: this script uses an updated version of scribendi_score which can be
# found here:
# https://github.com/robertostling/scribendi_score
# A pull request has been submitted.

module load GCC/10.2.0  CUDA/11.1.1-GCC-10.2.0  OpenMPI/4.0.5-gcccuda-2020b
module load PyTorch/1.9.0-fosscuda-2020b

module load Python/3.8.6-GCCcore-10.2.0

export HF_DATASETS_CACHE="/cephyr/NOBACKUP/groups/smnlp/.hg_cache"
export TRANSFORMERS_CACHE="/cephyr/NOBACKUP/groups/smnlp/.hg_cache"

source /cephyr/users/robertos/Alvis/venv/transformers/bin/activate

DATA=/cephyr/users/robertos/Alvis/few-shot-gec/data
MODEL=/cephyr/NOBACKUP/groups/smnlp/GPT-SW3

# s2 granska mt-base
for SYSTEM in granska mt-base s2; do
    echo "Launching at:"
    date
    python -u /cephyr/users/robertos/Alvis/.local/scribendi_score/scribendi.py \
	--src $DATA/nyberg_test_dev/Nyberg.CEFR_A.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_B.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_C.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.test.orig.txt \
	--pred $DATA/experiments/Nyberg.CEFR_A.test.$SYSTEM:$DATA/experiments/Nyberg.CEFR_B.test.$SYSTEM:$DATA/experiments/Nyberg.CEFR_C.test.$SYSTEM:$DATA/experiments/Nyberg.CEFR_ABC.test.$SYSTEM \
	--model_id "$MODEL"
    echo "Finished at:"
    date
done

echo "Launching at:"
date
python -u /cephyr/users/robertos/Alvis/.local/scribendi_score/scribendi.py \
    --src $DATA/nyberg_test_dev/Nyberg.CEFR_A.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_B.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_C.test.orig.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.test.orig.txt \
    --pred $DATA/nyberg_test_dev/Nyberg.CEFR_A.test.corr.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_B.test.corr.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_C.test.corr.txt:$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.test.corr.txt \
    --model_id "$MODEL"
echo "Finished at:"
date

#
#echo "Launching at:"
#date
#python -u /cephyr/users/robertos/Alvis/.local/scribendi_score/scribendi.py \
#    --src $DATA/nyberg_test_dev/Nyberg.CEFR_A.test.orig.txt \
#    --pred $DATA/experiments/Nyberg.CEFR_A.test.granska:$DATA/experiments/Nyberg.CEFR_A.test.s2:$DATA/nyberg_test_dev/Nyberg.CEFR_A.test.corr.txt \
#    --model_id "$MODEL"
#echo "Finished at:"
#date
#
#echo "Launching at:"
#date
#python -u /cephyr/users/robertos/Alvis/.local/scribendi_score/scribendi.py \
#    --src $DATA/nyberg_test_dev/Nyberg.CEFR_C.test.orig.txt \
#    --pred $DATA/experiments/Nyberg.CEFR_C.test.granska:$DATA/nyberg_test_dev/Nyberg.CEFR_C.test.corr.txt \
#    --model_id "$MODEL"
#echo "Finished at:"
#date
#
#echo "Launching at:"
#date
#python -u /cephyr/users/robertos/Alvis/.local/scribendi_score/scribendi.py \
#    --src $DATA/nyberg_test_dev/Nyberg.CEFR_B.test.orig.txt \
#    --pred $DATA/experiments/Nyberg.CEFR_B.test.granska:$DATA/experiments/Nyberg.CEFR_B.test.s2x:$DATA/nyberg_test_dev/Nyberg.CEFR_B.test.corr.txt \
#    --model_id "$MODEL"
#echo "Finished at:"
#date
#
