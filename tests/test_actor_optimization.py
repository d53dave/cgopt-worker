import pytest

from context import OptimizationActor, WorkerCommand, OptResult


class MockWorker():
    pass


@pytest.fixture
def worker(mocker):
    mw = MockWorker()
    mw.compile_model = mocker.Mock(return_value='model_deployed')
    mw.run = mocker.Mock(return_value=OptResult(values=[], states=[]))
    mw.model_compiled = False

    return mw


def test_deploy(worker):
    OptimizationActor.opt_worker = worker

    model = {}
    result = OptimizationActor(WorkerCommand.DeployModel.value, model)

    worker.compile_model.assert_called_once()
    assert result == 'model_deployed'


def test_run_opt(worker):
    worker.model_compiled = True
    OptimizationActor.opt_worker = worker

    result = OptimizationActor(WorkerCommand.RunOptimization.value, {
                               'params': {'optimization': {}}})

    worker.run.assert_called_once()
    assert type(result) == dict
    assert 'failure' not in result


def test_run_without_deploy(worker):
    OptimizationActor.opt_worker = worker
    with pytest.raises(AssertionError):
        OptimizationActor(WorkerCommand.RunOptimization.value, {})
