import pytest

from pyhocon import ConfigFactory
from context import OptimizationWorker, test_model_dict

internal_config = ConfigFactory.parse_file('worker/internal/internal.conf')


def test_run_opt_on_cpu():
    worker = OptimizationWorker(conf=internal_config)
    worker.compile_model(test_model_dict)
    opt_result = worker.run({
        'initial_temp': 100.0,
        'max_steps': 1000,
        'blocks_per_grid': 1,
        'threads_per_block': 1
    })

    assert opt_result.values is not None
    assert len(opt_result.values) == 1
    assert opt_result.values[0] == pytest.approx(-5.1256, 1e-3)
