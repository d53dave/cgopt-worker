import os
import psutil
import GPUtil
import logging
import dramatiq

from enum import Enum
from pyhocon import ConfigTree, ConfigFactory
from dramatiq import GenericActor
from typing import Any, Dict, Union

from ..cuda.opt_worker import OptimizationWorker, OptResult

log = logging.getLogger(__name__)

queue_id = os.environ.get('WORKER_QUEUE_ID')
assert queue_id is not None


class WorkerCommand(Enum):
    DeployModel = 'deploy_model'
    RunOptimization = 'run_optimization'


class PingActor(GenericActor):
    class Meta:
        queue_name = queue_id
        store_results = True

    def get_task_name(self) -> str:
        return 'ping'

    def perform(self) -> str:
        return 'pong'


class StatsActor(GenericActor):
    class Meta:
        queue_name = queue_id
        store_results = True

    def get_task_name(self) -> str:
        return 'stats'

    def perform(self) -> Dict[str, Any]:
        try:
            gpu = GPUtil.getGPUs()
        except Exception as e:
            gpu = str(e)
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'mem': psutil.virtual_memory(),
            'gpu': gpu
        }


class OptimizationActor(GenericActor):
    class Meta:
        queue_name = queue_id
        store_results = True

    def init_opt_worker(self, conf: ConfigTree) -> None:
        self.conf = conf
        self.opt_worker = OptimizationWorker(conf)

    def get_task_name(self) -> str:
        return 'optimization'

    def perform(self, cmd, payload) -> Union[str, OptResult]:
        log.debug(
            'WorkerActor called with cmd={} and payload={}'.format(cmd, payload))
        if cmd == WorkerCommand.DeployModel.value:
            try:
                return self.opt_worker.compile_model(payload)
            except Exception as e:
                return str(e)
        elif cmd == WorkerCommand.RunOptimization.value:
            opt_result = self.opt_worker.run(payload)
            return opt_result.to_dict()
        else:
            raise AttributeError('Command does not exist: ' + str(cmd))


internal_config = ConfigFactory.parse_file('worker/internal/internal.conf')

# pylint: disable=E1120
OptimizationActor.init_opt_worker(internal_config)  # type: ignore

for actor in dramatiq.get_broker().get_declared_actors():
    log.info('Declared actor: %s', actor)
