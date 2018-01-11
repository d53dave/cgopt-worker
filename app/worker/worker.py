
import numpy as np

from numba.cuda.random import create_xoroshiro128p_states
from typing import Dict, Any

from .modulegenerator import ModuleGenerator

# TODO: add this to the model documentation
# Numba(like cuRAND) uses the Box - Muller transform 
# <https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform> to generate 
# normally distributed random numbers from a uniform generator. However,
# Box - Muller generates pairs of random numbers, and the current implementation
# only returns one of them. As a result, generating normally distributed values
# is half the speed of uniformly distributed values.


class Worker():
    def __init__(self, conf: Dict[str, Any]) -> None:
        self.gen = ModuleGenerator(template_file=conf['cuda.template_path'])
        self.cuda = None

    async def run(self, model: Dict[str, Any]):
        opt_configuration = self._extract_opt_configuration(model)
        self.gen.cuda_module(opt_configuration)
        rng_states = create_xoroshiro128p_states(3, seed=1)
        cuda = self.gen.cuda_module(opt_configuration)

        print('Generated module: {} =\n{}'.format(cuda, dir(cuda)))

        states = np.array([(0.0, 0.0, 0.0)] * 3, dtype=np.float32)  # TODO: fix this, how?
        cuda.simulated_annealing[1, 3](100, 100, 3, rng_states, states)

    def _extract_opt_configuration(self, model: Dict[str, Any]) -> Dict[str, str]:
        opt_configuration = {}

        random_distribution = model['distribution']

        if random_distribution == 'uniform':
            opt_configuration['random_gen_type'] = 'xoroshiro128p_uniform_'
        elif random_distribution == 'normal':
            opt_configuration['random_gen_type'] = 'xoroshiro128p_normal_'
        else:
            raise AssertionError('Unknown random distribution type: ' + random_distribution)

        opt_configuration['precision'] = model['precision']
        opt_configuration['dim'] = str(model['dimensions'])
        opt_configuration['cool'] = model['functions']['cool']
        opt_configuration['initialize'] = model['functions']['initialize']
        opt_configuration['generate_next'] = model['functions']['generate_next']
        opt_configuration['evaluate'] = model['functions']['evaluate']
        opt_configuration['acceptance_func'] = model['functions']['ce_func']

        return opt_configuration
        
