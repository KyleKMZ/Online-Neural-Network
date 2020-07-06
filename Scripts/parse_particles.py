#!/usr/bin/env python

######
# Wrapper method around all the other parsing modules.
# Saves particle info as a text file and micrographs to disk.
######

import os
import warnings
import argparse
import numpy as np
from shutil import copyfile
from parse_relion import parse_relion
from parse_csparc import parse_csparc

def main():
    # For testing purposes as a command-line script
    parser = argparse.ArgumentParser(description = 'Enter particle file to parse.')
    parser.add_argument('filename', metavar = 'N', type = str)
    parser.add_argument('entryname', metavar = 'N', type = str)
    args = parser.parse_args()
    fp = args.filename
    entry_name = args.entryname
    print(fp, entry_name)
    parse_particles(fp, entry_name)

def parse_particles(fp, entry_name):
 
    ext = os.path.splitext(fp)[-1].lower()
    if not os.path.isfile(fp) or ext != '.star' or ext != '.cs':
        raise Exception('Please provide a valid Relion .star or CryoSparc .cs file.')

    db_loc = '../Database/'
    entry_path = os.path.join(db_loc, entry_name)
    if os.path.isdir(entry_path):
        raise Exception('An entry with the given name already exists in the database. Please choose another.')

    if (ext == '.star'):
        data_dict = parse_relion(fp)

        # Write training data info to disk
        num_particles = len(data_dict['rlnCoordinateX'])
        micrographs = set(data_dict['rlnMicrographName'])
        num_mics = len(micrographs)
        print("Adding %d particles..." % num_particles)
        print("Adding %d micrographs..." % num_mics)

        # The metadata can be usually parsed from the STAR file
        # But if it doesn't exist, the user can input value within the GUI
        try:
            voltage = data_dict['rlnVoltage']
        except:
            voltage = 0
        try:
            cs = data_dict['rlnSphericalAberration']
        except:
            cs = 0.0
        try:
            amp_cont = data_dict['rlnAmplitudeContrast']
        except:
            amp_cont = 0.0
        try:
            pix_size = data_dict['rlnImagePixelSize']
        except:
            pix_size = 0.0

        os.makedirs(entry_path)
        # the training micrographs associated with the particles will be copied to this directory
        os.makedirs(os.path.join(entry_path, 'Micrographs'))
        
        # Write the info file to disk
        info_f = open(os.path.join(entry_path, 'info.txt'), 'w')
        info_f.write('Number of Particles: %d\n' % num_particles)
        info_f.write('Number of Micrographs: %d\n' % num_mics)
        info_f.write('Voltage: %d\n' % voltage)
        info_f.write('Spherical Aberration (CS): %g\n' % cs)
        info_f.write('Amplitude Contrast: %g\n' % amp_cont)
        info_f.write('Pixel Size: %g\n' % pix_size)
        info_f.write('$\n') #'$' will be used as the delimiter between sections 
        info_f.write('Missing Micrographs\n')

         
        # Write the metadata of particles to disk.
        data_f = open(os.path.join(entry_path, 'data.txt'), 'w')
        data_f.write('Voltage %d\n' % voltage)
        data_f.write('CS %g\n' % cs)
        data_f.write('AmpContrast %g\n' % amp_cont)
        data_f.write('PixelSize %g\n' % pix_size)
        data_f.write('$\n') #'$' will be used as the delimiter between sections 
 
        # write the training data to disk, organized by micrograph
        for mic in micrographs:
            mic_name = os.path.basename(mic)
            # save/copy over the necessary micrographs to disk
            # By default, assume that the Relion project folder is two directories above the STAR file being parsed
            # and the script is ran at the same file system level (how parse_particles.py is used in the GUI)
            mic_path = os.path.join(os.getcwd(), os.path.abspath(os.path.join('../../', mic)))
            if os.path.isfile(mic_path):
                copyfile(mic_path, os.path.join(entry_path, 'Micrographs', os.path.basename(mic)))
                print("Added micrograph: %s." % mic_name)
            else:
                # issue a warning that a particular micrograph does not exist
                # record missing micrographs in the info file
                warnings.warn("WARNING: The micrograph '%s' cannot be found. It will not be copied over." % mic_name)
                info_f.write('%s\n' % mic_name) 

            data_f.write('Micrograph %s\n' % mic_name)
            # write all the particles (x, y locations) belonging to this micrograph
            for i in range(num_particles):
                if data_dict['rlnMicrographName'][i] == mic:
                    data_f.write('%f %f\n' % (data_dict['rlnCoordinateX'][i], data_dict['rlnCoordinateY'][i]))
            data_f.write('$\n')

        info_f.close()
        data_f.close()

    elif (ext == '.cs'):
        data_dict = parse_csparc(fp)
        
        num_particles = len(data_dict['location/center_x_frac'])
        micrographs = set(data_dict['location/micrograph_path'])
        num_mics = len(micrographs)
        print("Adding %d particles..." % num_particles)
        print("Adding %d micrographs..." % num_mics)

        # The metadata can usually be parsed from the CS file
        # If it doesn't exist, the user can input value within the GUI
        try:
            voltage = data_dict['ctf/accel_kv']
        except:
            voltage = 0
        try:
            cs = data_dict['ctf/cs_mm']
        except:
            cs = 0.0
        try:
            amp_cont = data_dict['ctf/amp_contrast']
        except:
            amp_cont = 0.0
        try:
            pix_size = data_dict['blob/psize_A']
        except:
            pix_size = 0.0

        os.makedirs(entry_path)
        # the training micrographs associated with the particles will be copied to this directory
        os.makedirs(os.path.join(entry_path, 'Micrographs'))
        
        # Write training data info to disk
        info_f = open(os.path.join(entry_path, 'info.txt'), 'w')
        info_f.write('Number of Particles: %d\n' % num_particles)
        info_f.write('Number of Micrographs: %d\n' % num_mics)
        info_f.write('Voltage: %d\n' % voltage)
        info_f.write('Spherical Aberration (CS): %g\n' % cs)
        info_f.write('Amplitude Contrast: %g\n' % amp_cont)
        info_f.write('$\n') #'$' will be used as the delimiter between sections 
        info_f.write('Missing Micrographs\n')

        # Write the metadata of particles to disk.
        data_f = open(os.path.join(entry_path, 'data.txt'), 'w')
        data_f.write('Voltage %d\n' % voltage)
        data_f.write('CS %g\n' % cs)
        data_f.write('AmpContrast %g\n' % amp_cont)
        data_f.write('PixelSize %g\n' % pix_size)
        data_f.write('$\n') #'$' will be used as the delimiter between sections 

        # write the training data to disk, organized by micrograph
        for mic in micrographs:
            mic_name = os.path.basename(mic.decode('utf-8'))
            # save/copy over the necessary micrographs to disk
            # By default, assume that the CryoSparc project folder is one directory above the CS file being parsed
            # and the script is ran at the same file system level (how parse_particles.py is used in the GUI)
            mic_path = os.path.join(os.getcwd(), os.path.abspath(os.path.join('../', mic.decode('utf-8'))))
            if os.path.isfile(mic_path):
                copyfile(mic_path, os.path.join(entry_path, 'Micrographs', os.path.basename(mic.decode('utf-8'))))
                print("Added micrograph: %s." % mic_name)
            else:
                # issue a warning that a particular micrograph does not exist
                # record missing micrographs in info.txt
                print(mic_path)
                warnings.warn("WARNING: The micrograph '%s' cannot be found. It will not be copied over." % mic_name)
                info_f.write('%s\n' % mic_name) 

            data_f.write('Micrograph %s\n' % mic_name)
            # write all the particles (x, y locations) belonging to this micrograph
            for i in range(num_particles):
                if data_dict['location/micrograph_path'][i] == mic:
                    x_coord = data_dict['location/center_x_frac'][i] * data_dict['location/micrograph_shape'][i][0].astype(np.int)
                    y_coord = data_dict['location/center_y_frac'][i] * data_dict['location/micrograph_shape'][i][1].astype(np.int)
                    data_f.write('%f %f\n' % (x_coord, y_coord))
            data_f.write('$\n')

        info_f.close()
        data_f.close()

def parse_particles_project_folder(particles_fp, data_output_dir, mics_output_dir, copy_mics = False):
    # Implementation of parse_particles used for parsing particle data
    # by their Relion or CSparc project folder hierarchy
    # particles_fp: input particle file -> .STAR or .CS
    # data_output_dir: directory to save particle data files info.txt and data.txt
    # mics_output_dir: directory to save micrographs that contains the particles
    # copy_mics: if set to False (default), micrographs are symbolically linked instead of hard-copied

    ext = os.path.splitext(particles_fp)[-1].lower()
    if not os.path.isfile(particles_fp) or (ext != '.star' and ext != '.cs'):
        raise Exception('Please provide a valid Relion .star or CryoSparc .cs file.')

    if (ext == '.star'):
        data_dict = parse_relion(particles_fp)
        # Write training data info to disk
        try:
            num_particles = len(data_dict['rlnCoordinateX'])
            micrographs = set(data_dict['rlnMicrographName'])
            num_mics = len(micrographs)
        except:
            raise Exception('STAR file %s is missing necessary information\
                    about number of particles and micrographs.' % particles_fp)

        # The metadata can be usually parsed from the STAR file
        # But if it doesn't exist, the user can input value within the GUI
        try:
            voltage = data_dict['rlnVoltage']
        except:
            warnings.warn("STAR file %s is missing parameter 'rlnVoltage':\
                    voltage is set to 0." % particles_fp)
            voltage = 0
        try:
            cs = data_dict['rlnSphericalAberration']
        except:
            warnings.warn("STAR file %s is missing parameter 'rlnSphericalAberration':\
                    CS is set to 0.0." % particles_fp)
            cs = 0.0
        try:
            amp_cont = data_dict['rlnAmplitudeContrast']
        except:
            warnings.warn("STAR file %s is missing parameter 'rlnAmplitudeContrast':\
                    amp_cont is set to 0.0." % particles_fp)
            amp_cont = 0.0
        try:
            pix_size = data_dict['rlnImagePixelSize']
        except:
            warnings.warn("STAR file %s is missing parameter: 'rlnImagePixelSize':\
                    pix_size is set to 0.0." % particles_fp)
            pix_size = 0.0

        info_f = open(os.path.join(data_output_dir, 'info.txt'), 'w')
        info_f.write('Number of Particles: %d\n' % num_particles)
        info_f.write('Number of Micrographs: %d\n' % num_mics)
        info_f.write('Voltage: %d\n' % voltage)
        info_f.write('Spherical Aberration (CS): %g\n' % cs)
        info_f.write('Amplitude Contrast: %g\n' % amp_cont)
        info_f.write('$\n') #'$' will be used as the delimiter between sections 
        info_f.write('Missing Micrographs\n')

        data_f = open(os.path.join(data_output_dir, 'data.txt'), 'w')
        # write particle metadata to data file on disk
        data_f.write('Voltage %d\n' % voltage)
        data_f.write('CS %g\n' % cs)
        data_f.write('AmpContrast %g\n' % amp_cont)
        data_f.write('PixelSize %g\n' % pix_size)
        data_f.write('$\n') #'$' will be used as the delimiter between sections 

        for mic in micrographs:
            mic_name = os.path.basename(mic)
            # save/copy over the necessary micrographs to disk
            # By default, assume that the Relion project folder is two directories above the STAR file being parsed
            # and the script is ran at the same file system level (how parse_particles.py is used in the GUI)
            mic_path = os.path.normpath(os.path.join(os.path.abspath(particles_fp), os.path.join('../../../', mic)))
            if os.path.isfile(mic_path):
                if copy_mics:
                    copyfile(mic_path, mics_output_dir)
                else:
                    # Create a symbolic link to the actual micrograph
                    # This should be default behavior to save disk space
                    if not os.path.isfile(os.path.join(mics_output_dir, mic_name)):
                        os.symlink(mic_path, os.path.join(mics_output_dir, mic_name))
            else:
                # issue a warning that a particular micrograph does not exist
                # record missing micrographs in the info file
                warnings.warn("WARNING: The micrograph '%s' cannot be found. It will not be stored in the database." % mic_name)
                info_f.write("%s\n" % mic_name)

            data_f.write('Micrograph %s\n' % mic_name)
            # write all the particles (x, y locations) belonging to this micrograph
            for i in range(num_particles):
                if data_dict['rlnMicrographName'][i] == mic:
                    data_f.write('%f %f\n' % (data_dict['rlnCoordinateX'][i], data_dict['rlnCoordinateY'][i]))
            data_f.write('$\n')

        info_f.close()
        data_f.close()

    elif ext == '.cs':
        data_dict = parse_csparc(particles_fp)
        
        num_particles = len(data_dict['location/center_x_frac'])
        micrographs = set(data_dict['location/micrograph_path'])
        num_mics = len(micrographs)

        # The metadata can usually be parsed from the CS file
        # If it doesn't exist, the user can input value within the GUI
        try:
            voltage = data_dict['ctf/accel_kv']
        except:
            voltage = 0
        try:
            cs = data_dict['ctf/cs_mm']
        except:
            cs = 0.0
        try:
            amp_cont = data_dict['ctf/amp_contrast']
        except:
            amp_cont = 0.0
        try:
            pix_size = data_dict['blob/psize_A']
        except:
            pix_size = 0.0

        info_f = open(os.path.join(data_output_dir, 'info.txt'), 'w')
        info_f.write('Number of Particles: %d\n' % num_particles)
        info_f.write('Number of Micrographs: %d\n' % num_mics)
        info_f.write('Voltage: %d\n' % voltage)
        info_f.write('Spherical Aberration (CS): %g\n' % cs)
        info_f.write('Amplitude Contrast: %g\n' % amp_cont)
        info_f.write('$\n') #'$' will be used as the delimiter between sections 
        info_f.write('Missing Micrographs\n')

        data_f = open(os.path.join(data_output_dir, 'data.txt'), 'w')
        # write particle metadata to data file on disk
        data_f.write('Voltage %d\n' % voltage)
        data_f.write('CS %g\n' % cs)
        data_f.write('AmpContrast %g\n' % amp_cont)
        data_f.write('PixelSize %g\n' % pix_size)
        data_f.write('$\n') #'$' will be used as the delimiter between sections 
        
        
        # write the training data to disk, organized by micrograph
        for mic in micrographs:
            mic_name = os.path.basename(mic.decode('utf-8'))
            # save/copy over the necessary micrographs to disk
            mic_path = os.path.normpath(os.path.join(particles_fp, os.path.join('../', mic.decode('utf-8'))))
            if os.path.isfile(mic_path):
                if copy_mics:
                    copyfile(mic_path, mics_output_dir)
                else:
                    # Create a symbolic link to the actual micrograph
                    # This should be default behavior to save disk space
                    if not os.path.isfile(os.path.join(mics_output_dir, mic_name)):
                        os.symlink(mic_path, os.path.join(mics_output_dir, mic_name))

            else:
                # issue a warning that a particular micrograph does not exist
                # record missing micrographs in info.txt
                print(mic_path)
                warnings.warn("WARNING: The micrograph '%s' cannot be found. It will not be copied over." % mic_name)
                info_f.write('%s\n' % mic_name) 

            data_f.write('Micrograph %s\n' % mic_name)
            # write all the particles (x, y locations) belonging to this micrograph
            for i in range(num_particles):
                if data_dict['location/micrograph_path'][i] == mic:
                    x_coord = data_dict['location/center_x_frac'][i] * data_dict['location/micrograph_shape'][i][0].astype(np.int)
                    y_coord = data_dict['location/center_y_frac'][i] * data_dict['location/micrograph_shape'][i][1].astype(np.int)
                    data_f.write('%f %f\n' % (x_coord, y_coord))
            data_f.write('$\n')

        info_f.close()
        data_f.close()


                
if __name__ == '__main__':
    main()





