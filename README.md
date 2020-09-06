 # Online-Neural-Network
 
 The purpose of this code is to implement automated generation of training data from completed CryoEM projects. The parsed training data is stored in an intermediate text-based 
 form, which can then be fed towards popular particle picking neural network implementations like Cryolo and Topaz for easy and convenient training. In short, the scripts 
 implement  a complete pipeline from reconstructions to a trained model. It does this through 3 steps or components: (1) Parsing of CryoSparc and Relion projects, (2) Storage in 
 text-based intermediate database, and (3) Reformatting and pipelining for a specific neural network.  
 
## (1) Parsing of CryoSparc and Relion projects 
In CryoEM, the two most widely-used reconstruction programs are CryoSparc and Relion. The scripts in this collection allow for parsing of both CryoSparc and Relion projects. It parses a project directory to search for the following jobs that contain particle data that might be relevant and useful for training a neural network. It searches for the following jobs depending on project type.

CryoSparc: Homogenous Refinement, Heterogeneous Refinement, Select2D, ManualPick  
Relion: 3D auto-fine, 3D classification, 2D Classification, Manual Picking

The types of jobs we parse are actually identical in function, they just have different names due to differences between CryoSparc and Relion.

Relevant scripts: **parse_csparc.py** and **parse_relion.py** are the base scripts. **parse_particles.py** is a wrapper around the functions in those two scripts, with some additions. **file_crawler.py** is an automatic file crawler that recursively searches for CryoSparc and Relion project directories and parses them using functions from the 3 previous scripts. 

## (2) Storage in text-based intermediate database

A CryoEM project that has been parsed is stored in a hierarchical database format that serves as the intermediary before pipelining training data directly to Cryolo or Topaz.  
For example, a CryoSparc project that has a final homogeneous refinement job, two heterogenous refinements, one Select2D job and one ManualPick job will have the following file structure when parsed.

CryoSparc Project   
----- Micrographs (containing micrographs found for all parsed jobs)  
----- Particles  
  |-------------- Homo_J51  
  |-------------- Hetero_J50  
  |-------------- Hetero_J48  
  |-------------- Select2D_J24  
  |-------------- ManualPick_J20  
                    
Each job folder (such as Homo_J51 or Hetero_J50), will contain two text files: info.txt and data.txt. 'info.txt' contains metadata about this particular job entry: number of micrographs, number of particles, voltage, cs, psize, etc. 'data.txt' contains particle coordinates (x, y) arranged by micrograph name.

The need for an intermediary database format for training data is due to the fact that different NN particle picking software such as Cryolo and Topaz will have diffent input data formats. Having a singular database format for all parsed data will make it convenient to later reformat particle data from a general database into a format that suits whatever particle picking software it is pipelined to.

## (3) Reformatting and pipelining for a specific neural network

Relevant scripts: **cryolo_pipeline.py**, **topaz_pipeline.py**, **warp_pipeline.py**

The above three scripts contains functions for converting training data from the database into the input format required by the particular particle picking software. As of this moment, only cryolo_pipeline.py and topaz_pipeline.py are complete. It automatically generates Slurm scripts for both training and picking with these neural networks on the jiang cluster. The Slurm scripts may have to be modified to suit your needs if this changes (or you want to use different amounts of resources from the default).

## MISC

### New neural network implementation?
Currently, the code only parses particle data and pipelines it back into existing particle picking software. In the case that existing particle picking programs are not suitable for training models with hundreds of thousands to millions of particles, there may be a need to implement a new NN model from scratch to better accomodate the increased amount of training data.

### Executable scripts
Most of the various scripts have incomplete implementations for use as an executable script from the command-line. I have carried out testing mainly from a Python interpreter due to its convenience. However, adding command-line arguments and streamlining the experience for an end user as an executable script should not be too difficult or time-consuming. (Reference: https://docs.python.org/3/library/argparse.html)
