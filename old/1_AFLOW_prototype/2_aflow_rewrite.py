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
SYMPREC = 0.01
MERGE_TOL = 0.01
CIF_LOC = f"../0_retrieve_icsd_data/final_cifs_for_aflow/testing/"
IN_DIR =  f"{CIF_LOC}1_succ_oxi/"
OUTDIR =  f'{CIF_LOC}2_succ_rewrite_aflow/'
OUTDIR_FAIL = f'{CIF_LOC}2_fail_rewrite_aflow/'
TEST_MODE = 0
TEST_SIZE = 100 #300
############################################################################



def write_struc(struc, path, symprec=None, comment=None):
    """Writes Pymatgen structure as CIF"""
    cw = CifWriter(struc, symprec=symprec)
    cw.write_file(path)
    del cw
    if comment:
        with open(path) as f:
            lines = f.readlines()
            lines[0] = f"#{comment}{lines[0]}"
        with open(path, "w") as f:
            f.writelines(lines)
            
            
def parse_struc(path, primitive=False):
    try:
        struc = Structure.from_file(path, primitive=primitive, merge_tol=MERGE_TOL)
    except ValueError:
        struc = Structure.from_file(path, primitive=primitive)
    except Exception as e:
        print(f'Failed to parse {path}\t{e}')
        return None
    return struc


def add_label(path, prototype, species):
    path_ls = path.split('/')
#     elements = [Specie(spec).symbol for spec in species]
    labeled_name = f'{path_ls[-1][:-4]}--{prototype}--{"_".join(species)}.cif'
    path_ls[-1] = labeled_name
    return '/'.join(path_ls)


def remove_label(path):
    path_ls = path.split('/')
    name = path_ls[-1].split('--')[0] + '.cif'
    path_ls[-1] = name
    return '/'.join(path_ls)


# Retrieve files
print(IN_DIR)
files = list(glob.glob(IN_DIR + "*.cif"))
print(f'Found {len(files)} files')
if TEST_MODE: files = files[::len(files)//TEST_SIZE]
# print(files)
filenames = [file.split('/')[-1] for file in files]
print(f'Loaded {len(files)} files')
print(f'First: {files[0]}')
print(f'Last:  {files[-1]}')
success_locs = [f'{OUTDIR}{filename}' for filename in filenames] 
failure_locs = [f'{OUTDIR_FAIL}{filename}' for filename in filenames] 
log_loc_1 = f"{CIF_LOC}log_2_rewrite_aflow.txt"


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


        
# Create arguments for parallelized bulk rewriting      
if not os.path.exists(OUTDIR):
    os.mkdir(OUTDIR)
if not os.path.exists(OUTDIR_FAIL):
    os.mkdir(OUTDIR_FAIL)

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

# Copy raw versions of errored files over 
# failed_files = list(glob.glob(OUTDIR_FAIL + "*.cif"))
# failed_filenames = [file.split('/')[-1] for file in failed_files]
# for fname in failed_filenames:
#     shutil.copy(f'{CIF_LOC}raw/{fname}', f'{OUTDIR_FAIL}raw-{fname}')
