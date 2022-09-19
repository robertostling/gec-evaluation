#!/usr/bin/env bash
#SBATCH -A SNIC2021-7-121 -p alvis
#SBATCH --gpus-per-node=A40:1
#SBATCH -t 0-04:00:00

# This is required with 32-bit precision: --gpus-per-node=A100fat:1

# Resource curves, estimated from A100fat node on Alivs with 32-bit GPT-J:
# system RAM: peaks at about 50 GB, then goes down to almost nothing
# GPU RAM: stable just below 32 GB
# More information here:
#   https://huggingface.co/docs/transformers/model_doc/gptj

#SBATCH --output=train.out
module load GCC/10.2.0  CUDA/11.1.1-GCC-10.2.0  OpenMPI/4.0.5-gcccuda-2020b
module load PyTorch/1.9.0-fosscuda-2020b

module load Python/3.8.6-GCCcore-10.2.0

export HF_DATASETS_CACHE="/cephyr/NOBACKUP/groups/smnlp/.hg_cache"
export TRANSFORMERS_CACHE="/cephyr/NOBACKUP/groups/smnlp/.hg_cache"

source /cephyr/users/robertos/Alvis/venv/transformers/bin/activate
#source /cephyr/NOBACKUP/groups/smnlp/python_env_murathan/deep/bin/activate

python -u annotate.py "$@"
