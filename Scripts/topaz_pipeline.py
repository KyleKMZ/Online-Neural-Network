#!/usr/bin/env python

import os
import subprocess

def topaz_train(job_folders, output_folder, save_prefix='models', output='models/model_training.txt', downsample=8):
    """
    Takes a list of job folders and creates conveniently formatted Topaz training data.
    Also create a Slurm script that allows training with a single command.
    """
    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)


    raw_dir = os.path.join(output_folder, 'raw')
    if not os.path.exists(raw_dir):
        os.mkdir(raw_dir)

    processed_dir = os.path.join(output_folder, 'processed')
    if not os.path.exists(processed_dir):
        os.mkdir(processed_dir)

    save_prefix = os.path.join(output_folder, save_prefix)
    if not os.path.exists(save_prefix):
        os.mkdir(save_prefix)

    particles_file = open(os.path.join(raw_dir, 'particles.txt'), 'w')
    particles_file.write('image_name\tx_coord\ty_coord\n')

    # Keep track of these stats to calculate avg. particles per mic for training
    total_particles = 0
    total_mics = 0

    for job_folder in job_folders:
        with open(os.path.join(job_folder, 'data.txt')) as data_f:
            all_data = data_f.read()
            all_data = all_data.split('$')[:-1]

            for mic_data in all_data[1:]:
                # list and filter func. used to get rid of empty strings just in case
                mic_name = list(filter(None, mic_data.split('\n')))[0].split()[-1]
                mic_path = os.path.normpath(os.path.join(particle_data_file, '../../../Micrographs/%s' % mic_name))

                if os.path.exists(mic_path):
                    # copy the necessary micrographs over to micrographs/raw/, which will later be preprocessed
                    shutil.copy(mic_path, raw_mics_dir, follow_symlinks=False)

                    # reformat particles to the format used by Topaz and save them to particles.txt
                    particle_data = list(filter(None, mic_data.split('\n')))[1:]
                    for particle in particle_data:
                        x, y = particle.split()
                        x = round(float(x))
                        y = round(float(y))
                        particles_file.write('{}\t{:<4d}\t{:<4d}\n'.format(mic_name, x, y))

        with open(os.path.join(job_folder, 'info.txt')) as info_f:
            total_particles += int(info_f.readline().split(':')[-1])
            total_mics += int(info_f.readline().split(':')[-1])

    particles_file.close()
    avg_particles_per_mic = round(total_particles / total_mic)

    # Create Slurm script for preprocessing and training
    script_path = os.path.join(output_folder, 'topaz_train.slurm')
    with open(script_path, 'w') as slurm_f:
        slurm_f.write("#!/usr/bin/env bash\n")
        slurm_f.write("\n")
        slurm_f.write("#SBATCH --job-name ttrain\n")
        slurm_f.write("#SBATCH --partition jiang-gpu\n")
        slurm_f.write("#SBATCH --ntasks 2\n")
        slurm_f.write("#SBATCH --cpus-per-task 12\n")
        slurm_f.write("#SBATCH --gres gpu:2\n")
        slurm_f.write("#SBATCH --nodelist prp\n")
        slurm_f.write("#SBATCH --output %x.%j.stdout\n")
        slurm_f.write("#SBATCH --error %x.%j.stderr\n")
        slurm_f.write("\n")
        slurm_f.write("source activate topaz\n")
        slurm_f.write("topaz preprocess -v -s {} -o {} {}\n".format(downsample, processed_dir, os.path.join(raw_dir, "*.mrc")))
        slurm_f.write("topaz convert -s {} -o {} {}\n".format(downsample, os.path.join(processed_dir, "particles.txt"), os.path.join(raw_dir, "particles.txt")))
        slurm_f.write("topaz train -n {} \
                                   --num-workers=12 \ 
                                   --train-images {} \
                                   --train-targets {} \
                                   --save-prefix={} \
                                   -o {}".format(avg_particles_per_mic,
                                                 processed_dir,
                                                 os.path.join(processed_dir, "particles.txt"),
                                                 save_prefix,
                                                 output))


def topaz_pick(output, mics_folder, model, particle_radius=14, upsample=8):
    """
    Generates a Slurm script for picking particles using a trained Topaz model.
    """
    with open("topaz_pick.slurm", 'w') as slurm_f:
        slurm_f.write("#!/usr/bin/env bash\n")
        slurm_f.write("\n")
        slurm_f.write("#SBATCH --job-name tpick\n")
        slurm_f.write("#SBATCH --partition jiang-gpu\n")
        slurm_f.write("#SBATCH --ntasks 1\n")
        slurm_f.write("#SBATCH --cpus-per-task 12\n")
        slurm_f.write("#SBATCH --gres gpu:1\n")
        slurm_f.write("#SBATCH --nodelist prp\n")
        slurm_f.write("#SBATCH --output %x.%j.stdout\n")
        slurm_f.write("#SBATCH --error %x.%j.stderr\n")
        slurm_f.write("\n")
        slurm_f.write("source activate topaz\n")
        slurm_f.write("topaz extract -r {} -x {} \
                                     -o {} {}".format(particle_radius, upsample, output, os.path.join(mics_folder, '*.mrc')))


def main():

    #Do some testing

if __name__ == '__main__':
    main()


