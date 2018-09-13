# flake8: noqa

import os
import sys
from distutils import dir_util

sys.path.insert(0, os.path.abspath('.'))

os.environ['NUMBA_ENABLE_CUDASIM'] = '1'
os.environ['WORKER_QUEUE_ID'] = 'test_queue'

from broker import broker
from worker.cuda.modulegenerator import ModuleGenerator
from worker.cuda.opt_worker import OptimizationWorker, OptResult
from worker.tasks.actors import OptimizationActor, WorkerCommand, PingActor, StatsActor

test_model_dict = {
    'name': 'test_opt',
    'dimensions': 2,
    'distribution': 'normal',
    'precision': 'float32',
    'state_shape': 2,
    'globals': '\nm = 5\nc = (1, 2, 5, 2, 3)\nA = ((3, 5), (5, 2), (2, 1), (1, 4), (7, 9))\n',
    'functions': {
        'distribution': 'def distribution() -> RandomDistribution:\n    return RandomDistribution.Normal\n',
        'precision': 'def precision() -> Precision:\n    return Precision.Float32\n',
        'dimensions': 'def dimensions() -> int:\n    return 2\n',
        'initialize': 'def initialize(state: MutableSequence, randoms: Sequence[float]) -> None:\n    for i in range(len(randoms)):\n        state[i] = randoms[i]\n    return\n',
        'generate_next': 'def generate_next(state: Sequence, new_state: MutableSequence, randoms: Sequence[float]) -> Any:\n    for i in range(len(state)):\n        new_state[i] = clamp(0, 0.2 * (state[i] + randoms[i]), 10)\n    return\n',
        'cool': 'def cool(initial_temp: float, old_temp: float, step: int) -> float:\n    return initial_temp * math.pow(0.97, step)\n',
        'evaluate': 'def evaluate(state: Sequence) -> float:\n    result = 0.0\n    for i in range(m):  # sum from 0 to m-1\n        t2 = 0.0\n        for j in range(2):  # sum from 0..-1\n            s_j = state[j]\n            a_ij = A[i][j]\n            t2 += (s_j - a_ij)**2\n        t2 = -(1 / pi) * t2\n        t3 = 0.0\n        for j in range(2):  # sum from 0..d-1\n            t3 += (state[j] - A[i][j])**2\n        t3 = pi * t3\n        result += c[i] * math.exp(t2) * math.cos(t3)\n    return -result\n',
        'acceptance_func': 'def acceptance_func(e1: float, e2: float, temp: float, rnd: float) -> bool:\n    x = clamp(-88.7227, -(e2 - e1) / temp, 88.7227)\n    return math.exp(x) > rnd',
        'empty_state': 'def empty_state() -> Tuple:\n    return (0.0, 0.0)\n',
    }
}
