import os
import sys
import re
import json
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

# Checks if a folder is a CSPARC project folder
def is_csparc_project(dir_path):
    """
    ALL CSparc project folders have settings and metadata files that identifies
    them as a CSparc project.
    """
    files = ['job_manifest.json', 'workspaces.json', 'project.json']
    for fname in files:
        if fname not in os.listdir(dir_path):
            return False

    return True

# Recursively search starting from a root directory for Relion and CSparc
# projects to parse them and add their particle data to a database
def parse_particles_cryoem_projects(root_dir):
    for root, subdirs, files in os.walk(root_dir):
        if is_relion_project(root):
            try:
                parse_relion_project(root, os.path.basename(os.path.normpath(root)))
            except:
                # Do nothing in case an exception is triggered,
                # there can be various reasons as to an exception.
                # Many parameters missing will cause an exception of their own.
                # In the future, might wanna implement more detailed error
                # or warnings about which parameters are missing.
                pass
        if is_csparc_project(root):
            try:
                parse_csparc_project(root, os.path.basename(os.path.normpath(root)))
            except:
                pass

        else:
            for dir_path in subdirs:
                parse_particles_cryoem_projects(dir_path)



# Checks if a directory contains RELION particle data
def _contains_particle_data(dir_path):
    """
    ManualPick and Select -> 2D, 3D contains a 'particles.star' file.
    For Refine3D jobs, check for a file of the type: 'run_itxxx_data.star',
    where xxx is the max iteration for a particular 3D refinement.
    Returns the name of the file that contains particle data if it exists,
    which is particles.star or run_itMAX_data.star.
    """

    if 'particles.star' in os.listdir(dir_path):
        return 'particles.star'
    elif 'Refine3D' in dir_path:
        run_iters = []
        for fname in os.listdir(dir_path):
            if re.match('run_it[0-9]{3}_data.star', fname):
                run_iters.append(fname)
        iter_nums = [re.findall('\d+', iteration)[0] for iteration in run_iters]
        print(dir_path, iter_nums)
        max_run_iter = 'run_it%s_data.star' % '{0:0=3d}'.format(int(max(iter_nums)))
        return max_run_iter

    return ''

# checks if a directory contains CSPARC particle data
def _contains_particle_data_csparc(dir_path):
    particle_fnames = ['extracted_particles.cs',
                        'passthrough_particles_selected.cs',
                        'passthrough_particles.cs',
                        'passthrough_particles_all_classes.cs']
    for fname in os.listdir(dir_path):
        for particle_file_name in particle_fnames:
            if particle_file_name in fname:
                return fname

    return ''

# returns the type of a cryosparc job folder 
def _csparc_job_type(job_dir_path):
    if not os.path.isdir(job_dir_path):
        return ''
    if not re.match('J\d', os.path.basename(os.path.normpath(job_dir_path))):
        return ''
    json_path = os.path.join(job_dir_path, 'job.json')
    with open(json_path) as json_f:
        data = json.load(json_f)
        if data['job_type'] == 'manual_picker':
            # Manual Picking jobs can also be for micrographs, clarify this
            if 'particles' in data['output_group_images']:
                return 'manual_picker_particles'
            else:
                return 'manual_picker_mics'
        return data['job_type']
    

# Parse a Cryosparc project folder and save to disk its particle data
def parse_csparc_project(dir_path, entry_name):
    """
    There are 4 types of particle data to save to disk:
    (1) Manually Picked particles
    (2) Particles of selected 2D classes
    (3) Particles from heterogeneous refinement
    (4) Particles from homogeneous refinement (best particles)
    """

    db_loc = '../Database/'
    entry_path = os.path.join('../Database', entry_name)
    os.makedirs(entry_path)
    mics_path = os.path.join(entry_path, 'Micrographs')
    os.makedirs(mics_path)
    particles_path = os.path.join(entry_path, 'Particles')
    os.makedirs(particles_path)

    # Handles manually picked particle data
    manual_dir_path_list = [os.path.join(dir_path, dir_name) for dir_name in os.listdir(dir_path) 
        if _csparc_job_type(os.path.join(dir_path, dir_name)) == 'manual_picker_particles']
    for manual_job_dir in manual_dir_path_list:
        particles_fname = _contains_particle_data_csparc(manual_job_dir)
        if particles_fname:
            sub_particles_path = os.path.join(particles_path, 'ManualPick_%s' % os.path.basename(os.path.normpath(manual_job_dir)))
            os.makedirs(sub_particles_path)
            parse_particles_project_folder(particles_fp = os.path.join(manual_job_dir, particles_fname),
                    data_output_dir = sub_particles_path,
                    mics_output_dir = mics_path)

    # Handles particle data from selected 2D classes
    select2D_dir_path_list = [os.path.join(dir_path, dir_name) for dir_name in os.listdir(dir_path) 
            if _csparc_job_type(os.path.join(dir_path, dir_name)) == 'select_2D']
    for select2D_job_dir in select2D_dir_path_list:
        particles_fname = _contains_particle_data_csparc(select2D_job_dir)
        if particles_fname:
            sub_particles_path = os.path.join(particles_path, 'Select2D_%s' % os.path.basename(os.path.normpath(select2D_job_dir)))
            os.makedirs(sub_particles_path)
            parse_particles_project_folder(particles_fp = os.path.join(select2D_job_dir, particles_fname),
                    data_output_dir = sub_particles_path,
                    mics_output_dir = mics_path)

    # Handles particle data from heterogenous refinement
    hetero_dir_path_list = [os.path.join(dir_path, dir_name) for dir_name in os.listdir(dir_path)
            if _csparc_job_type(os.path.join(dir_path, dir_name)) == 'hetero_refine']
    for hetero_job_dir in hetero_dir_path_list:
        particles_fname = _contains_particle_data_csparc(hetero_job_dir)
        if particles_fname:
            sub_particles_path = os.path.join(particles_path, 'Hetero_%s' % os.path.basename(os.path.normpath(hetero_job_dir)))
            os.makedirs(sub_particles_path)
            parse_particles_project_folder(particles_fp = os.path.join(hetero_job_dir, particles_fname),
                    data_output_dir = sub_particles_path,
                    mics_output_dir = mics_path)

    # Handles particle data from homogeneous refinement
    homo_dir_path_list = [os.path.join(dir_path, dir_name) for dir_name in os.listdir(dir_path)
            if _csparc_job_type(os.path.join(dir_path, dir_name)) == 'homo_refine' or
            _csparc_job_type(os.path.join(dir_path, dir_name)) == 'homo_refine_new']
    for homo_job_dir in homo_dir_path_list:
        particles_fname = _contains_particle_data_csparc(homo_job_dir)
        if particles_fname:
            sub_particles_path = os.path.join(particles_path, 'Homo_%s' % os.path.basename(os.path.normpath(homo_job_dir)))
            os.makedirs(sub_particles_path)
            parse_particles_project_folder(particles_fp = os.path.join(homo_job_dir, particles_fname),
                    data_output_dir = sub_particles_path,
                    mics_output_dir = mics_path)

# Parse a Relion project folder and save to disk its particle data
def parse_relion_project(dir_path, entry_name):
    """
    There are 3 types of particle data to save to disk:
    (1) Manually Picked particles
    (2) Particles of selected 2D classes
    (3) Particles of selected 3D classes
    (4) Particles from 3D Reconstruction job (Refine3D - homogeneous refinement, best particles)

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
            # For jobs with user-given names, Relion creates a symbolink link to the real job directory
            # Parsing only the actual job directories will prevent double-parsing particle data
            if os.path.islink(job_dir_path):
                continue
            if _contains_particle_data(job_dir_path):
                sub_particles_path = os.path.join(particles_path, 'ManualPick_%s' % os.path.basename(os.path.normpath(job_dir_path)))
                os.makedirs(sub_particles_path)
                parse_particles_project_folder(particles_fp = os.path.join(job_dir_path, 'particles.star'), 
                        data_output_dir = sub_particles_path,
                        mics_output_dir = mics_path)

    # (2) Handles particle data from selected 2D classes
    # (3) Handles particle data from selected 3D classes
    select_dir = os.path.join(dir_path, 'Select')
    if os.path.isdir(select_dir):
        job_dir_path_list = [os.path.join(select_dir, dir_name) for dir_name in os.listdir(select_dir) if os.path.isdir(os.path.join(select_dir, dir_name))]
        for job_dir_path in job_dir_path_list:
            if os.path.islink(job_dir_path):
                continue
            if _contains_particle_data(job_dir_path):
                if _get_particle_type(job_dir_path) == 'Class3D':
                    sub_particles_path = os.path.join(particles_path, 'Select3D_%s' % os.path.basename(os.path.normpath(job_dir_path)))
                elif _get_particle_type(job_dir_path) == 'Class2D':
                    sub_particles_path = os.path.join(particles_path, 'Select2D_%s' % os.path.basename(os.path.normpath(job_dir_path)))
                else:
                    # Inconclusive particle type. Should never happen in real use.
                    # For debugging purposes.
                    sub_particles_path = os.path.join(particles_path, 'Inconclusive_%s' % os.path.dirname(job_dir_path))
                    warnings.warn("Inconclusive particle file type...")

                os.makedirs(sub_particles_path)
                parse_particles_project_folder(particles_fp = os.path.join(job_dir_path, 'particles.star'),
                        data_output_dir = sub_particles_path,
                        mics_output_dir = mics_path)

    # (4) Handles cases of just one 3D reconstruction in a project - the Refine3D job
    refine3D_dir = os.path.join(dir_path, 'Refine3D')
    if os.path.isdir(refine3D_dir):
        job_dir_path_list = [os.path.join(refine3D_dir, dir_name) for dir_name in os.listdir(refine3D_dir) if os.path.isdir(os.path.join(refine3D_dir, dir_name))]
        for job_dir_path in job_dir_path_list:
            if os.path.islink(job_dir_path):
                continue
            data_fname = _contains_particle_data(job_dir_path)
            if data_fname:
                sub_particles_path = os.path.join(particles_path, 'Refine3D_%s' % os.path.basename(os.path.normpath(job_dir_path)))
                os.makedirs(sub_particles_path)
                parse_particles_project_folder(particles_fp = os.path.join(job_dir_path, data_fname),
                        data_output_dir = sub_particles_path,
                        mics_output_dir = mics_path)


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
        while True:
            line = pipeline_f.readline().strip()
            if line == "data_pipeline_input_edges":
                particle_type = [pipeline_f.readline().strip() for i in range(5)][4]
                break
    particle_type  = particle_type.split('/')[0]
    return particle_type





def main():
    # for testing in the command-line as a script
    parse_particles_cryoem_projects('/net/jiang/home/zaw/scratch/relion30_tutorial')

if __name__ == '__main__':
    main()
                


