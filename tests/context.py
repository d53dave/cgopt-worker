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
    'globals': '\na = 20\nb = 0.2\nc = 2 * pi\nmax_steps = 20000\n',
    'functions': {
        'distribution': 'def distribution() -> RandomDistribution:\n    return RandomDistribution.Normal\n',
        'precision': 'def precision() -> Precision:\n    return Precision.Float32\n',
        'dimensions': 'def dimensions() -> int:\n    return 2\n',
        'initialize': 'def initialize(state: MutableSequence, randoms: Sequence[float]) -> None:\n    for i in range(len(randoms)):\n        state[i] = clamp(-32, 16 * randoms[i], 32)\n    return\n',
        'generate_next': 'def generate_next(state: Sequence, new_state: MutableSequence, randoms: Sequence[float], step) -> Any:\n    for i in range(len(state)):\n        \n        new_state[i] = clamp(-32, 8 * randoms[i], 32)\n    return\n',
        'cool': 'def cool(initial_temp: float, old_temp: float, step: int) -> float:\n    return initial_temp * math.pow(0.9, step)\n',
        'evaluate': 'def evaluate(state: Sequence) -> float:\n    d = 2\n    t1_sum = 0.0\n    t2_sum = 0.0\n\n    for i in range(d):\n        t1_sum += state[i] * state[i]\n        t2_sum += math.cos(c * state[i])\n\n    t1 = -a * math.exp(-b * math.sqrt(t1_sum / d))\n\n    t2 = math.exp(t2_sum / d)\n\n    return t1 - t2 + a + 2.71828182846\n',
        'acceptance_func': 'def acceptance_func(e_old: float, e_new: float, temp: float, rnd: float) -> bool:\n    x = clamp(-80, (e_old - e_new) / temp, 0.1)\n    return math.exp(x) > rnd',
        'empty_state': 'def empty_state() -> Tuple:\n    return (0.0, 0.0)\n',
    }
}
