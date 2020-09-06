#!/usr/bin/env bash

#SBATCH --job-name slurm_job
#SBATCH --partition jiang
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 12
#SBATCH --gres gpu:2
#SBATCH --nodelist prp
#SBATCH --output %x.%j.stdout
#SBATCH --error %x.%j.stderr

