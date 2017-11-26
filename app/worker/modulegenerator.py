import os
import sys
import imp
import numpy as np

from string import Template

from typing import Dict


class ModuleGenerator():
    def __init__(self, **conf):
        self.template_file = conf['template_file']
        print('template file = {}'.format(self.template_file))

    def _render_template(self, func_strings: Dict[str, str]) -> str:
        with open(self.template_file, 'r') as f:
            opt_template = f.read()

            print('Template string = {}'.format(opt_template))
            return Template(opt_template).substitute(initialize=func_strings['initialize'],
                                                     evaluate=func_strings['evaluate'],
                                                     generate_next=func_strings['generate_next'],
                                                     cool=func_strings['cool'],
                                                     acceptance_func=func_strings['acceptance_func'])

    def _create_module(self, name: str, source: str) -> any:
        module = imp.new_module(name)
        print('Executing source:\n{}'.format(source))
        exec(source, module.__dict__)
        sys.modules[name] = module

        return module

    def cuda_module(self, func_strings: Dict[str, str]) -> any:
        source = self._render_template(func_strings)

        cuda_opt = self._create_module('cuda_opt', source)

        return cuda_opt


if __name__ == '__main__':
    template_path = sys.argv[1]
    print('Running modulegen with {}'.format(template_path))
    gen = ModuleGenerator(template_file=template_path)

    func_strings = {}
    func_strings['cool'] = """def cool(old_temp): return old_temp * .97"""

    func_strings['initialize'] = """def initialize(randoms): return (1, 2, 3)"""

    func_strings['generate_next'] = \
        """def generate_next(state, randoms): return (state[0] + 1, state[1] + 1, state[2] + 1)"""

    func_strings['evaluate'] = \
        """def evaluate(state): return state[0] / state[1] / state[2]"""

    func_strings['acceptance_func'] = \
        """def acceptance_func(e1, e2, temp): return math.exp(-(e2 - e1) / temp)"""

    cuda = gen.cuda_module(func_strings)

    print('Generated module: {} =\n{}'.format(cuda, dir(cuda)))
    states = np.array([(0.0, 0.0, 0.0)] * 3)
    cuda.simulated_annealing[1, 3](100, 100, states)
    print(states)
