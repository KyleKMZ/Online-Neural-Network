#!/usr/bin/env python

""" Cryolo Pipeline Script

Contains functions that handle the pipelining and processing of particle data
from the output of file_crawler.py, to a form usable by the Cryolo software
for both training and picking.

Can also be used as a standalone executable script.
Example usage: $cryolo_pipeline.py --job-folders Select2D_job030 Select3D_job033 --box-sizes 150 150
Optional parameters: config_fname, train_image_folder, train_annot_folder, saved_weights_name, pretrained_weights
"""

import os
import subprocess
import shutil
import warnings


def create_config_file(box_size, config_fname,
                       train_image_folder, train_annot_folder,
                       saved_weights_name, pretrained_weights):

    command = "cryolo_gui config %s %d --train_image_folder %s --train_annot_folder %s --saved_weights_name %s --pretrained_weights %s" %\
        (config_fname, box_size, train_image_folder,
         train_annot_folder, saved_weights_name, pretrained_weights)
    subprocess.run(command)

def train_model(config_fname):

    command = "cryolo_train -c %s -w 5 -g 0" % config_fname
    subprocess.run(command)


def convert_to_cryolo_training(particle_data_file, box_size, output_image_folder,
                               output_annot_folder):
    """
    Converts the output of file_crawler.py's particle files 'data.txt' into
    the box format used by Cryolo for training data. Also arranges the micrograph
    files in separate train_image folder.
    """
    if not os.path.exists(output_image_folder):
        os.makedir(output_image_folder)
    if not os.path.exists(output_annot_folder):
        os.makedir(output_annot_folder)
    with open(particle_data_file, 'r') as data_f:
        all_data = data_f.read()
        all_data = all_data.split('$')
        # the first element in the list would be particle metadata
        for mic_data in all_data[1:]:
            mic_name = mic_data[0].split()[-1]
            mic_path = os.path.normpath(os.path.join(
                particle_data_file, '../../Micrographs/%s' % mic_name))
            if os.path.exists(mic_path):
                shutil.copy(mic_path, os.path.join(
                    output_image_folder, mic_name))
                box_file_path = os.path.join(
                    output_annot_folder, '%s.box' % os.path.splitext(mic_name)[0])
                with open(box_file_path, 'w') as box_f:
                    # the first element in the list would be the micrograph name
                    particle_data = mic_data.split('\n')[1:]
                    for particle in particle_data:
                        x, y = particle.split()
                        box_f.write('%d %d %d $%d\n' %
                                    (x, y, box_size, box_size))
            else:
                warnings.warn('Micrographs folder is missing %s: particle data \
                    related to it will not be used for training data.' % mic_name)


def cryolo_training(job_folders=[], box_sizes=[], cryolo_output_folder='cryolo_training',
                    config_fname='config_cryolo.json', train_image_folder='train_image', train_annot_folder='train_annot',
                    saved_weights_name='cryolo_model.h5', pretrained_weights=''):
    """
    Automatically sets up the necessary box files, images and config files for
    training a Cryolo model from the job_folder output(s) of file_crawler.py,
    such as Refine3D_job035. It then trains a Cryolo model based on user-given settings.

    job_folders can be a simple particle job folder or a list of job folders which can be
    combined to train a Cryolo model. box_sizes contain the corresponding box sizes used
    to train the model.
    """
    assert(len(job_folders) == len(box_sizes))\
        os.makedir(cryolo_output_folder)
    box_sizes_list = []
    for i in range(len(job_folders)):
        job_folder = job_folders[i]
        box_size = box_sizes[i]
        box_sizes_list.append(box_size)
        convert_to_cryolo_training(particle_data_file=os.path.join(job_folder, 'data.txt'),
                                   box_size=box_size,
                                   output_image_folder=os.path.join(
                                       cryolo_output_folder, train_image_folder),
                                   output_annot_folder=os.path.join(cryolo_output_folder, train_annot_folder))

    # As per official Cryolo documentation, use the average box size for training when using
    # multiple datasets. An alternative is to try with the max box size.
    avg_box_size = int(sum(box_sizes_list) / len(box_sizes))
    # max_box_size = int(max(box_sizes_list))
    create_config_file(avg_box_size, config_fname=os.path.join(cryolo_output_folder, config_fname),
                       train_image_folder=os.path.join(
                           cryolo_output_folder, train_image_folder),
                       train_annot_folder=os.path.join(
                           cryolo_output_folder, train_annot_folder),
                       saved_weights_name=os.path.join(
                           cryolo_output_folder, saved_weights_name),
                       pretrained_weights=pretrained_weights)

    train_model(os.path.join(cryolo_output_folder, config_fname))

def main():


if __name__ == '__main__':
    main()
