import numpy as np
import warnings

def parse_csparc(fp):
    try:
        cs = np.load(fp)
    except:
        raise Exception("ERROR: cannot parse file")

    cs_dict = {}

    # Parse the necessary metadata
    metadata_list = ['ctf/accel_kv', 'ctf/cs_mm', 'ctf/amp_contrast', 'blob/psize_A']
    for metadata in metadata_list:
        if metadata not in cs.dtype.names:
            warnings.warn("CS file is missing metadata: %s" % metadata)
        else:
            cs_dict[metadata] = cs[metadata][0]

    # Parse the particle locations (x, y) and micrographs, and micrograph shape
    parameter_list = ['location/center_x_frac', 'location/center_y_frac', 'location/micrograph_path', 'location/micrograph_shape']
    assert(len(cs['location/center_x_frac']) == len(cs['location/center_y_frac']) == len(cs['location/micrograph_path'])) # sanity check
    for parameter in parameter_list:
        if parameter not in cs.dtype.names:
            raise Exception("CS file is missing necessary parameter: %s" % parameter)
        cs_dict[parameter] = cs[parameter]

    return cs_dict


    

    
