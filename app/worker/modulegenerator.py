import os
import sys
import imp
import numpy as np

from numba.cuda.random import create_xoroshiro128p_states
#from numba.cuda.random import xoroshiro128p_uniform_float32
#from numba.cuda.random import xoroshiro128p_uniform_float64
#from numba.cuda.random import xoroshiro128p_normal_float32
#from numba.cuda.random import xoroshiro128p_normal_float64
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
            return Template(opt_template).substitute(func_strings)

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

    def cuda_module(self, func_strings: Dict[str, str]) -> any:
        source = self._render_template(func_strings)

        cuda_opt = self._create_module('cuda_opt', source)

        return cuda_opt


if __name__ == '__main__':
    # TODO: check that precision is either float32 or float64 (float vs double)
    # TODO: rename func_strings to something more general
    # TODO: validate that random_distribution is either uniform or normal

    template_path = sys.argv[1]
    print('Running modulegen with {}'.format(template_path))
    gen = ModuleGenerator(template_file=template_path)

    func_strings = {}
    func_strings['precision'] = 'float32'
    func_strings['random_distribution'] = 'uniform'

    if func_strings['random_distribution'] == 'uniform':
        func_strings['random_gen_type'] = 'xoroshiro128p_uniform_'

    if func_strings['random_distribution'] == 'normal':
       func_strings['random_gen_type'] = 'xoroshiro128p_normal_'

    func_strings['dim'] = """3"""

    func_strings['cool'] = """def cool(old_temp): return old_temp * .97"""

    func_strings['initialize'] = """def initialize(state, randoms): return (0.0, 0.0, 0.0)"""

    func_strings['generate_next'] = \
        """def generate_next(state, randoms): return (state[0] + randoms[0], state[1] + randoms[1], state[2] + randoms[2])"""

    func_strings['evaluate'] = \
        """def evaluate(state): return 0.42"""

    func_strings['acceptance_func'] = \
        """def acceptance_func(e1, e2, temp): return math.exp(-(e2 - e1) / temp)"""

    cuda = gen.cuda_module(func_strings)

    print('Generated module: {} =\n{}'.format(cuda, dir(cuda)))
    states = np.array([(0.0, 0.0, 0.0)] * 3, dtype=np.float32)
    rng_states = create_xoroshiro128p_states(3, seed=1)

    cuda.simulated_annealing[1, 3](100, 100, 3, rng_states, states)
    print(states)
