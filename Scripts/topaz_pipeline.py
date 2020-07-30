#!/usr/bin/env python

import os

def convert_to_topaz_particles(particle_data_f, topaz_data_f="particles.txt"):
    """
    Convert a particle_data_f 'data.txt' (output of file_crawler.py and parse_particles.py)
    to a format used by the Topaz neural network for particle training data.

    Topaz Format
    ------------
    Mic_name X_coord Y_coord

    """

    topaz_f = open(topaz_data_f, "w")
    topaz_f.write("Mic_name X_coord Y_coord\n")

    with open(particle_data_f, "r") as data_f:
        all_data = data_f.read().split('$')
        # the first element is particle metadata and the last element is just a newline character
        for particle_data in all_data[1:-1]:
            particle_data = particle_data.split('\n')
            particle_data = list(filter(None, particle_data)) # get rid of empty strings
            
            mic_info = particle_data[0]
            mic_name = mic_info.split()[1]

            for coords in particle_data[1:]:
                x_coord, y_coord = coords.split()
                x_coord, y_coord = round(float(x_coord)), round(float(y_coord))
                topaz_f.write("{} {} {}\n".format(mic_name, x_coord, y_coord))

    topaz_f.close()

def topaz_train(job_folders, output_folder, processed_dir='processed', save_prefix='models', output='models/model_training.txt', downsample=8):
    """
    Takes a list of job folders and creates conveniently formatted Topaz training data.
    Also creates a Slurm script that allows training with a single command.
    """
    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    processed_dir = os.path.join(output_folder, processed_dir) 
    if not os.path.exists(processed_dir):
        os.mkdir(processed_dir)

    mics_dir = os.path.join(processed_dir, 'micrographs')
    if not os.path.exists(mics_dir):
        os.mkdir(mics_dir)

    save_prefix = os.path.join(output_folder, save_prefix)
    if not os.path.exists(save_prefix):
        os.mkdir(save_prefix)

    for job_folder in job_folders:
        # preprocess the micrographs and particle coordinates by downsampling them (default: 8x)






def topaz_pick():

def main():

    test_data_f = "../Database/relion30_tutorial/Particles/Refine3D_job035/data.txt"
    convert_to_topaz_particles(test_data_f, "topaz_test.txt")

if __name__ == '__main__':
    main()


