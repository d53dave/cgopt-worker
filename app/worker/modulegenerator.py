import os
import imp

from string import Template

from typing import Dict

@contextmanager
def temp_open(path, mode):
    # if this fails there is nothing left to do anyways
    file = open(path, mode)

    try:
        yield file
    finally:
        file.close()
        os.remove(path)

class ModuleGenerator():
    def __init__(self, **conf):
        self.template_file = conf['template_file']

    def _render_template(self, func_strings: Dict[str, str]) -> str:
        opt_template: str = ''
        with open(self.template_file, 'r') as f:
            tempopt_templatelate = f.read().replace('\n', '')
        
        return opt_template.template()

    def _load_module(self, name: str) -> any:
        f, filename, description = imp.find_module('cuda_opt')
        cuda_opt = imp.load_module('cuda_opt', f, filename, description)

        assert cuda_opt is not None

        return cuda_opt
        
    def cuda_module(self, func_strings: Dict[str, str]) -> any:
        file_content = self._render_template(func_strings)
        
        with temp_open('cuda_opt.py', 'w') as cuda_file:
            cuda_file.write(file_content)

            cuda_opt = self._load_module('cuda_opt')

            return cuda_opt
