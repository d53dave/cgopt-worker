import sys
import logging
import types

from string import Template
from pyhocon import ConfigTree
from typing import Dict, Any

log = logging.getLogger(__name__)


class ModuleGenerator():
    def __init__(self, conf: ConfigTree) -> None:
        template_file = str(conf['template_path'])
        with open(template_file, 'r') as f:
            self.opt_template = f.read()

    def _render_template(self, model: Dict[str, str]) -> str:
        return Template(self.opt_template).substitute(model)

    def _create_module(self, name: str, source: str) -> Any:
        module = types.ModuleType(name)
        log.debug('Compiled numba/cuda module:\n{}'.format(source))
        exec(source, module.__dict__)
        sys.modules[name] = module

        return module

    def cuda_module(self, model: Dict[str, str]) -> Any:
        source = self._render_template(model)
        cuda_opt = self._create_module('csaopt_cuda_opt', source)

        return cuda_opt

    @staticmethod
    def extract_opt_configuration(model: Dict[str, Any]) -> Dict[str, str]:
        opt_configuration = {}

        random_distribution = model['distribution']

        if random_distribution == 'uniform':
            opt_configuration['random_gen_type'] = 'xoroshiro128p_uniform_'
        elif random_distribution == 'normal':
            opt_configuration['random_gen_type'] = 'xoroshiro128p_normal_'
        else:
            raise AssertionError(
                'Unknown random distribution type: ' + random_distribution)

        opt_configuration['name'] = model['name']
        opt_configuration['precision'] = model['precision']
        opt_configuration['dim'] = str(model['dimensions'])
        opt_configuration['globals'] = model['globals']
        opt_configuration['cool'] = model['functions']['cool']
        opt_configuration['initialize'] = model['functions']['initialize']
        opt_configuration['generate_next'] = model['functions']['generate_next']
        opt_configuration['evaluate'] = model['functions']['evaluate']
        opt_configuration['acceptance_func'] = model['functions']['acceptance_func']
        opt_configuration['empty_state'] = model['functions']['empty_state']

        return opt_configuration
