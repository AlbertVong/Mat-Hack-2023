import json 
import subprocess 
import os 
 
class XtalFinder: 
 
    def __init__(self, aflow_executable='aflow'): 
        self.aflow_executable = aflow_executable 
 
    def aflow_command(self, cmd): 
        try: 
            return subprocess.check_output( 
                self.aflow_executable + cmd, 
                shell=True 
            ) 
        except subprocess.CalledProcessError: 
            raise OSError('aflow executable not found: ' + self.aflow_executable) 
 
 
    def check_path(self, path): 
        if type(path) == str: 
            if os.path.exists(path): 
                return os.path.realpath(path) 
            else: 
                raise OSError(path + ' not found') 
        elif type(path) == list: 
            for p in path: 
                if not os.path.exists(p): 
                    raise OSError(path + ' not found') 
            return ','.join(path) 
        else: 
            raise TypeError('The path to input file/files/directory must be a string or a list.') 
 
 
    def get_prototype_label(self, input_file, options=None): 
        fpath = self.check_path(input_file) 
        command = ' --prototype' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json < ' + f'"{fpath}"' 
        ) 
        
        # temporary fix for AFLOW V3.2.11 #DX20210819
        output = output.decode('utf-8')
        if 'element_names' in output:
            elements_orig = output.split('\"element_names\":[')[1].split(']')[0]
            if '\"' not in elements_orig or '\'' not in elements_orig:
                elements_fixed = ','.join([ '\"'+element+'\"' for element in elements_orig.split(',') ])
                output = output.replace(elements_orig, elements_fixed)

        res_json = json.loads(output) 
        return res_json 
 
    def compare_materials(self, input_files, options=None): 
        fpath = self.check_path(input_files) 
        command = ' --compare_materials=' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare_materials_directory(self, directory, options=None): 
        fpath = self.check_path(directory) 
        command = ' --compare_materials -D ' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare_materials_file(self, filename, options=None): 
        fpath = self.check_path(filename) 
        command = ' --compare_materials -F=' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare_structures(self, input_files, options=None): 
        fpath = self.check_path(input_files) 
        command = ' --compare_structures=' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare_structures_directory(self, directory, options=None): 
        fpath = self.check_path(directory) 
        command = ' --compare_structures -D ' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare_structures_file(self, filename, options=None): 
        fpath = self.check_path(filename) 
        command = ' --compare_structures -F=' + f'"{fpath}"' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare2database(self, input_file, options=None): 
        fpath = self.check_path(input_file) 
        command = ' --compare2database' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet < ' + f'"{fpath}"' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def compare2prototypes(self, input_file, options=None): 
        fpath = self.check_path(input_file) 
        command = ' --compare2prototypes' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json --screen_only --quiet < ' + f'"{fpath}"' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def get_isopointal_prototypes(self, input_file, options=None): 
        fpath = self.check_path(input_file) 
        command = ' --isopointal_prototype' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json < ' + f'"{fpath}"' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 
 
    def get_unique_atom_decorations(self, input_file, options=None): 
        fpath = self.check_path(input_file) 
        command = ' --unique_atom_decorations' 
        output = '' 
 
        if options: 
            command += ' ' + options 
 
        output = self.aflow_command( 
            command + ' --print=json < ' + f'"{fpath}"' 
        ) 
 
        res_json = json.loads(output) 
        return res_json 

### Kyle's addition

    def generate_structure(self, prototype_label, parameters, decoration=None,  options=None):
        command = f' --proto={prototype_label}'

        if decoration:
            command += f':{decoration}'

        command += f' --parameters={parameters}'

        if options:
            command += ' ' + options
        
        output = self.aflow_command(
            command 
        )
        return output.decode('utf-8')
