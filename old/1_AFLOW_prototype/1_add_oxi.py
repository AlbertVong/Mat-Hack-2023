from pymatgen.io.cif import CifWriter
import glob
from pymatgen.core.structure import Structure
from pymatgen.core.periodic_table import Specie, Element
from pymatgen.analysis.local_env import ValenceIonicRadiusEvaluator
#import os.path
import os
home = os.path.expanduser('~')
import time
import multiprocessing as mp
import numpy as np
import sys
import shutil

SYMPREC = 0.01


def write_struc(struc, path, symprec=SYMPREC):
    """Writes Pymatgen structure as CIF
    """
    cw = CifWriter(struc, symprec=SYMPREC)
    cw.write_file(path)
    del cw


def _helper_decorate_structure(struct, symprec, success_loc, filename):
    """Helper function that decorates a single structure with oxidation states
    """
    vire = ValenceIonicRadiusEvaluator(structure=struct)
    struct = vire.structure
    #try:
    write_struc(struct, success_loc, symprec=SYMPREC)
    print('Predicted oxi states for ' + filename)
    #except Exception as e:
    #    print('Exception {} caused by file {}'.format(e, filename))
    #    file = open('log_add-oxi.txt', 'a+')
    #    file.write('Exception {} caused by file {}'.format(e, filename))
    #    file.close()
    del vire
    del struct


def decorate_structure(filepath, symprec=SYMPREC):
    directory = filepath.split('/')[:-1]
    filename = filepath.split('/')[-1]
    success_dir = '/'.join(directory + ['1_succ_oxi'])
    failure_dir = '/'.join(directory + ['1_fail_oxi'])
    if not os.path.exists(success_dir): os.mkdir(success_dir)
    if not os.path.exists(failure_dir): os.mkdir(failure_dir)

    try:
        struct = Structure.from_file(filepath)
        
        # If there are any element objects (missing oxi states) in the structure, predict
        if any(isinstance(site.species.elements[0], Element) for site in struct):
            _helper_decorate_structure(struct, symprec, f'{success_dir}/{filename}', filename)
            
        # If there are already oxidation states assigned to every site, check for zero oxi states
        else: #if all(isinstance(site.species.elements[0], Specie) for site in struct):
            zero_oxi = [spec.oxi_state == 0 for spec in struct.species]
            if any(zero_oxi): # if any site doesn't already have oxi state, predict oxi states
                _helper_decorate_structure(struct, symprec, f'{success_dir}/{filename}', filename)
            
        # If it's all good, just write it
            else:
                print('No work needed for ' + filename)
                write_struc(struct, f'{success_dir}/{filename}')
    
    # Copy structures which failed to a subdirectory
    except Exception as e:
        print('Exception {} caused by file {}'.format(e, filepath.split("/")[-1]))
        shutil.copy(filepath, f'{failure_dir}/{filename}')


if __name__ == "__main__":

    target_dirs = sys.argv[1:]
    print(f"Target directories = {target_dirs}")
    for target_dir in target_dirs:
        if target_dir[-1] != '/':
            target_dir += '/'
        files = list(glob.glob(f"{target_dir}*.cif"))

        # Parallel
        start = time.time()
        print(f"Starting calculations in {target_dir} using {mp.cpu_count()-1} parallel threads.")
        with mp.Pool(processes=mp.cpu_count()-1) as pool:
            results = pool.map(decorate_structure, files)
        end = time.time()
        print(f"Finished work in {target_dir}")
        file = open('log_add-oxi.txt', 'a+')
        file.write(f"Finished work in {target_dir}\nParallel time = {np.round((end-start)/60, 1)} minutes\n")
        file.close()
        print(f"Parallel time = {np.round(end-start, 3)} seconds")
        
        # # Serial (slow)
        # start = time.time()
        # for i, filepath in enumerate(files):
        #     if i % 10 == 0:
        #         print('On file {}/{}'.format(i, len(files)))
        #     print(filepath.split("/")[-1])
        #     decorate_structure(filepath)
        # end = time.time()
        # print(f"Serial time: {np.round(end-start, 3)} seconds")
