import sys
import imp

from string import Template

from typing import Dict, Any


class ModuleGenerator():
    def __init__(self, **conf: Dict[str, Any]) -> None:
        template_file = conf['template_file']
        with open(template_file, 'r') as f:
            self.opt_template = f.read()

    def _render_template(self, opt_configuration: Dict[str, str]) -> str:
        print('Template string = {}'.format(self.opt_template))
        return Template(self.opt_template).substitute(opt_configuration)

    def _create_module(self, name: str, source: str) -> any:
        module = imp.new_module(name)
        sourcelines = source.splitlines()
        print('Executing source:\n')
        i = 1
        for line in sourcelines:
            print('{} {}'.format(i, line))
            i += 1
        exec(source, module.__dict__)
        sys.modules[name] = module

        return module

    def cuda_module(self, opt_configuration: Dict[str, str]) -> any:
        source = self._render_template(opt_configuration)

        cuda_opt = self._create_module('cuda_opt', source)

        return cuda_opt
