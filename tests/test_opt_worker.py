import pytest
import os

from pyhocon import ConfigFactory
from context import OptimizationWorker, test_model_dict

internal_config = ConfigFactory.parse_file('worker/internal/internal.conf')


def test_run_opt_without_deploy():
    worker = OptimizationWorker(conf=internal_config)
    opt_result = worker.run({
        'initial_temp': 100.0,
        'max_steps': 1000,
        'thread_count': 100
    })

    opt_result_dict = opt_result.to_dict()

    assert type(opt_result_dict) is dict
    assert 'failure' in opt_result_dict
    assert opt_result_dict['values'] is None
    assert opt_result_dict['states'] is None


@pytest.mark.skipif(not os.getenv('NUMBA_ENABLE_CUDASIM') == '1',
                    reason='CUDA Simulator is disabled, test_run_opt_on_cpu skipped because it would fail.')
def test_run_opt_on_cpu():
    worker = OptimizationWorker(conf=internal_config)
    worker.compile_model(test_model_dict)
    opt_result = worker.run({
        'initial_temp': 100.0,
        'max_steps': 1000,
        'thread_count': 100
    })

    assert opt_result.values is not None
    assert len(opt_result.values) == 1
    assert opt_result.values[0] == pytest.approx(-5.1256, 1e-3)


@pytest.mark.skipif(os.getenv('NUMBA_ENABLE_CUDASIM') == '1',
                    reason='CUDA Simulator enabled, test_run_opt_on_gpu skipped because it would fail.')
def test_run_opt_on_gpu():
    worker = OptimizationWorker(conf=internal_config)
    worker.compile_model(test_model_dict)
    opt_result = worker.run({
        'initial_temp': 100.0,
        'max_steps': 1000,
        'thread_count': 100
    })

    assert opt_result.values is not None
    assert len(opt_result.values) == 100
    for value in opt_result.values:
        assert value == pytest.approx(-5.1256, 1e-2)
