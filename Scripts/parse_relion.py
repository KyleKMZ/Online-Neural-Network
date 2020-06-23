######
# Module that uses EMAN2star.py to extract relevant information for training data from a
# RELION star file. Handles the following jobs and cases:
# 
# Select -> 2D Classification
# Select -> 3D Classification
# Extract -> Manual/Autopick
# 
# Does not save particle info and micrographs to disk. That task is done in
# parse_particles.py, which wraps around both parse_relion.py and parse_csparc.py
# to save training data to a centralized database.
######

from EMAN2star import StarFile
import warnings

def parse_relion(fp):
 
    star_dict = StarFile(fp)

    training_data_dict = {}

    # Check that the STAR file contains necessary metadata for the particles
    metadata_list = ['rlnVoltage', 'rlnSphericalAberration', 'rlnAmplitudeContrast', 'rlnImagePixelSize']
    for metadata in metadata_list:
        if metadata not in star_dict:
            warnings.warn('STAR file is missing metadata: %s' % metadata)
        else:
            training_data_dict[metadata] =  star_dict[metadata][0]


    # Check that the STAR file has the following necessary parameters for particles
    parameter_list = ['rlnCoordinateX', 'rlnCoordinateY', 'rlnMicrographName']
    assert(len(star_dict['rlnCoordinateX']) == len(star_dict['rlnCoordinateY']) == len(star_dict['rlnMicrographName'])) # sanity check
    for parameter in parameter_list:
        if parameter in star_dict:
            training_data_dict[parameter] = star_dict[parameter]
        else:
            raise Exception('STAR file is missing necessary parameter: %s' % parameter)

    return training_data_dict


        
