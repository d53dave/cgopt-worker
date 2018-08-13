import sys
import imp
import logging

from string import Template

from typing import Dict, Any

log = logging.getLogger(__name__)


class ModuleGenerator():
    def __init__(self, **conf: Dict[str, Any]) -> None:
        template_file = conf['template_file']
        with open(template_file, 'r') as f:
            self.opt_template = f.read()

    def _render_template(self, model: Dict[str, str]) -> str:
        return Template(self.opt_template).substitute(model)

    def _create_module(self, name: str, source: str) -> any:
        module = imp.new_module(name)
        log.debug('Compiled numba/cuda module:\n{}'.format(source))
        exec(source, module.__dict__)
        sys.modules[name] = module

        return module

    def cuda_module(self, model: Dict[str, str]) -> any:
        source = self._render_template(model)
        cuda_opt = self._create_module('cuda_opt', source)

        return cuda_opt
