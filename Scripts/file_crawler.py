import os
import sys
from parse_particles import parse_particles_project_folder

# Find files ending with the extensions in the list and
# returns a list of paths to such files within the given
# directory and sub directories
def find_file_with_extensions(dir_path, extensions=[]):
    file_list = []
    if not extensions:
        return file_list

    for entry in os.listdir(dir_path):
        subdir_path = os.path.join(dir_path, entry)
        if os.path.isdir(subdir_path):
            # recursively searching sub-directories
            file_list.extend(find_file_with_extensions(subdir_path, extensions))
        else:
            ext = os.path.splitext(entry)[-1]
            if ext in extensions:
                file_list.append(entry)

    return file_list

# Checks if a folder is a relion project folder
def is_relion_project(dir_path):
    """
    All Relion project folders have the default_pipeline.star and 
    the .relion_display_gui_settings files.
    """
    files = ['default_pipeline.star', '.relion_display_gui_settings']
    for fname in files:
        if fname not in os.listdir(dir_path):
            return False

    return True

# Checks if a directory contains RELION particle data
def contains_particle_data(dir_path):
    files = ['particles.star']
    for fname in files:
        if fname not in os.listdir(dir_path):
            return False

    return True

# Parse a Relion project folder and save to disk its particle data
def parse_relion_project(dir_path, entry_name):
    """
    There are 3 types of particle data to save to disk:
    (1) Manually Picked particles
    (2) Particles of selected 2D classes
    (3) Particles of selected 3D classes
    (4) Particles from 3D Reconstruction job (Refine3D)

    FILE HIERARCHY
    ---------------

    Database
        |-- Entry1
        |   |-- Micrographs
        |   |       |-- mic1.mrc
        |   |       |-- mic2.mrc
        |   |-- Particles (contains folders for data.txt and info.txt within sub-folders as previously implemented)
        |
        |-- Entry2
        |
        |-- ......
        |
        |-- ......

    """

    db_loc = '../Database/'
    entry_path = os.path.join('../Database', entry_name)
    os.makedirs(entry_path)
    mics_path = os.path.join(entry_path, 'Micrographs')
    os.makedirs(mics_path)
    particles_path = os.path.join(entry_path, 'Particles')
    os.makedirs(particles_path)

    # (1) Handles manually picked particle data
    manual_pick_dir = os.path.join(dir_path, 'ManualPick')
    if os.path.isdir(manual_pick_dir):
        job_dir_path_list = [os.path.join(manual_pick_dir, dir_name) for dir_name in os.listdir(manual_pick_dir) if os.path.isdir(os.path.join(manual_pick_dir, dir_name))]
        for job_dir_path in job_dir_path_list:
            if contains_particle_data(job_dir_path):
                sub_particles_path = os.path.join(particles_path, 'ManualPick %s' % os.path.dirname(job_dir_path))
                os.makedirs(sub_particles_path)
                parse_particles_project_folder(particles_fp = os.path.join(job_dir_path, 'particles.star'), 
                        data_output_dir = sub_particles_path,
                        mics_output_dir = mics_path)

    # (2) Handles particle data from selected 2D classes
    # (3) Handles particle data from selected 3D classes
    select_dir = os.path.join(dir_path, 'Select')
    if os.path.isdir(select_dir):
        job_dir_path_list = [os.path.join(select_dir, dir_name) for dir_name in os.listdir(manual_pick_dir) if os.path.isdir(os.path.join(manual_pick_dir, dir_name))]
        for job_dir_path in job_dir_path_list:
            if contains_particle_data(job_dir_path):
                if _get_particle_type(job_dir_path) == 'Class3D':

                elif _get_particle_type(job_dir_path) == 'Class2D':

                else:
                    # Inconclusive particle type. Should never happen in real use.
                    # For debugging purposes.


def _get_particle_type(job_dir):
    # Returns whether a Relion Select job deals with either
    # 2D classes or 3D classes.
    #
    # Relion sub-folders have a 'job_pipeline.star' file that describes the input
    # and output data type of a particular job. The 'data_pipeline_input_edges'
    # section in particular describes the input job class (whether its from 
    # 2D classification or 3D classification or something else).
    particle_type = ""
    with open(os.path.join(job_dir, 'job_pipeline.star'), 'r') as pipeline_f:





def main():
    # for testing in the command-line as a script
    parse_relion_project('../../relion30_tutorial', 'RelionTest')

if __name__ == '__main__':
    main()
                


