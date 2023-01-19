from aflow_xtalfinder_python_patched_tweaked import XtalFinder

from os.path import expanduser
home = expanduser("~")
import os
import shutil
from datetime import datetime, timedelta

from pprint import pprint

import glob
import multiprocessing as mp
import time
import numpy as np

#from pymatgen.core.structure import Structure
#from pymatgen.io.cif import CifWriter
#from pymatgen.core.periodic_table import Species, Element
#from pymatgen.analysis.local_env import ValenceIonicRadiusEvaluator
#from pymatgen.analysis.bond_valence import BVAnalyzer

### CONSTANTS ##############################################################
#SYMPREC = 0.01
#MERGE_TOL = 0.01
CIF_LOC = f"../0_retrieve_icsd_data/final_cifs_for_aflow/testing/2_succ_rewrite_aflow"
TEST_MODE = 0
TEST_SIZE = 100 #300
############################################################################

# Retrieve files
print(CIF_LOC)
files = list(glob.glob(CIF_LOC + "/*.cif"))
print(f'Found {len(files)} files')
if TEST_MODE: files = files[::len(files)//TEST_SIZE]
# print(files)
filenames = [file.split('/')[-1] for file in files]
print(f'Loaded {len(files)} files')
print(f'First: {files[0]}')
print(f'Last:  {files[-1]}')
log_loc_1 = f"log_3_aflow_proto.log"


def rewrite_aflow(xf, input_path, success_path, failure_path):
    try:
        struc_dict = xf.get_prototype_label(input_path, options='--print_element_names')
    except Exception as e:
#         print(input_path)
        print(f"{input_path.split('/')[-1]}\tFailed prototyping: {e}\n")
        with open(log_loc_1, "a+") as file:
            file.write(f"{input_path.split('/')[-1]}\tFailed prototyping: {e}\n")
        shutil.copy(input_path, failure_path)
        return
    try:
        cif_str = xf.generate_structure(struc_dict['aflow_prototype_label'], 
                                        ','.join([str(param) for param in struc_dict['aflow_prototype_params_values']]), 
                                        decoration=':'.join(struc_dict['element_names']), options='--cif')
        # Append prototype label to file name
        elements = [Species.from_string(species).element.symbol for species in struc_dict['element_names']]
        labeled_path = add_label(success_path, struc_dict['aflow_prototype_label'], elements) 
        with open(labeled_path, 'w+') as file:
            file.write(cif_str)
    except Exception as e:
        print(f"Failed AFLOW gen: {input_path.split('/')[-1]}\t{e}")
        with open(log_loc_1, "a+") as file:
            file.write(f"{input_path.split('/')[-1]}\tFailed struc gen: {e}\n")
        shutil.copy(input_path, failure_path)


xf = XtalFinder()

args = zip([xf]*len(files), files, success_locs, failure_locs)
# print(f'Sample argument: {list(args)[0]}')

# Rewrite the files in parallel
start = time.time()
timestamp = datetime.fromtimestamp(start)
with open(log_loc_1, "a+") as file:
    file.write(f"\n### {timestamp}\n")
with mp.Pool(processes=mp.cpu_count()-1) as pool:
    pool.starmap(rewrite_aflow, args)
print(f'rewrite files w AFLOW: {timedelta(seconds=(time.time()-start))}')

print(f'Successes: {len([name for name in os.listdir(OUTDIR) if os.path.isfile(OUTDIR+name)])}')
print(f'Failures:  {len([name for name in os.listdir(OUTDIR_FAIL) if os.path.isfile(OUTDIR_FAIL+name)])}')
