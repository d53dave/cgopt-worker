# pylint: disable=E1101

import sys
import traceback
import numpy as np
import uuid
import logging
import os

from numba.cuda.random import create_xoroshiro128p_states
from pyhocon import ConfigTree
from typing import Dict, Any, Tuple, Type, Optional

from .modulegenerator import ModuleGenerator


log = logging.getLogger(__name__)

Failure = Optional[
    Tuple[Optional[Type[BaseException]],
          Optional[BaseException],
          str]]


def _is_debug_run():
    return str(os.environ.get('NUMBA_ENABLE_CUDASIM')) == '1'


class OptResult():
    def __init__(self, values: np.ndarray, states: np.ndarray, failure: Failure=None) -> None:
        self.values: np.ndarray = values
        self.states: np.ndarray = states
        self.failure: Failure = failure

    def to_dict(self):
        data = {
            'values': self.values,
            'states': self.states
        }

        if self.failure is not None:
            data['failure'] = {
                'type': str(self.failure[0]),       # pylint: disable=E1136
                'exception': str(self.failure[1]),  # pylint: disable=E1136
                'message': self.failure[2]          # pylint: disable=E1136
            }

        return data

# TODO: add this to the model documentation
# Numba(like cuRAND) uses the Box - Muller transform
# <https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform> to generate
# normally distributed random numbers from a uniform generator. However,
# Box - Muller generates pairs of random numbers, and the current implementation
# only returns one of them. As a result, generating normally distributed values
# is half the speed of uniformly distributed values.


class OptimizationWorker():

    def __init__(self, conf: ConfigTree) -> None:
        self.conf = conf['optimization']
        self.gen = ModuleGenerator(conf['cuda'])
        self.opt_configuration: Dict[str, str] = {}
        self.model_compiled = False
        self.opt_module: object = None
        self.id = str(uuid.uuid4())

    def compile_model(self, model: Dict[str, Any]) -> str:
        try:
            self.opt_configuration = ModuleGenerator.extract_opt_configuration(
                model)
            self.opt_module = self.gen.cuda_module(  # type: ignore
                self.opt_configuration)
            log.info('Model "%s" was successfully loaded loaded as a module',
                     self.opt_configuration['name'])
            self.model_compiled = True
            return 'model_deployed'
        except Exception as e:
            log.exception(e)
            return str(e)

    def _get_blocks_per_grid(self, array_size: int, threads_per_block: int) -> int:
        return (array_size + (threads_per_block - 1)) // threads_per_block

    def run(self, opt_params) -> OptResult:
        try:
            assert self.opt_module is not None

            precision = np.float64 if self.opt_configuration['precision'] == 'float64' else np.float32

            max_steps = opt_params.get(
                'max_steps', self.conf['defaults.max_steps'])
            initial_temp = opt_params.get(
                'initial_temp', self.conf['defaults.initial_temp'])
            thread_count = opt_params.get(
                'thread_count', self.conf['defaults.thread_count'])
            threads_per_block = opt_params.get(
                'threads_per_block', self.conf['defaults.threads_per_block'])
            blocks_per_grid = opt_params.get(
                'blocks_per_grid')

            if blocks_per_grid is None:
                print('blocks_per_grid is None')
                blocks_per_grid = self._get_blocks_per_grid(
                    thread_count, threads_per_block)

            # if setting thread count < threads_per_block, the SA algorithm
            # will run out of bounds with the rngs, so we decrease block size
            if thread_count < threads_per_block:
                threads_per_block = thread_count

            empty_state = self.opt_module.empty_state()  # type: ignore

            result_size: int = thread_count
            values = np.array([0.0] * result_size, dtype=precision)
            states = np.array([empty_state] * result_size)  # type: ignore
            # TODO: pass seed in opt_params
            rng_states = create_xoroshiro128p_states(result_size, seed=1)

            self.opt_module.simulated_annealing[blocks_per_grid, threads_per_block](  # type: ignore
                max_steps, initial_temp, rng_states, states, values)

            return OptResult(values, states, None)
        except Exception as e:
            log.exception(e)
            type_, value_, traceback_ = sys.exc_info()
            return OptResult(None, None, (type_, value_, str(traceback.format_tb(traceback_))))
