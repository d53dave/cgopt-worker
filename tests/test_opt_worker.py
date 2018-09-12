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
        'max_steps': 200,
        'thread_count': 16,
    })

    assert opt_result.values is not None
    assert len(opt_result.values) == 16

    good_vals = []

    # We do not expect all threads to converge, but we do expect at least one
    for value in opt_result.values:
        print(value)
        if value == pytest.approx(-1.4, 1e-2):
            good_vals.append(value)

    assert len(good_vals) > 0


@pytest.mark.skipif(os.getenv('NUMBA_ENABLE_CUDASIM') == '1',
                    reason='CUDA Simulator enabled, test_run_opt_on_gpu skipped because it would fail.')
def test_run_opt_on_gpu():
    worker = OptimizationWorker(conf=internal_config)
    worker.compile_model(test_model_dict)
    opt_result = worker.run({
        'initial_temp': 100.0,
        'max_steps': 1000,
        'thread_count': 64
    })

    assert opt_result.values is not None
    assert len(opt_result.values) == 64
    for value in opt_result.values:
        assert value == pytest.approx(-1.4, 1e-2)
