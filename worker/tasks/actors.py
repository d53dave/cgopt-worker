import psutil
import GPUtil
import logging

from enum import Enum
from pyhocon import ConfigTree, ConfigFactory
from dramatiq import GenericActor

from ..cuda.opt_worker import OptimizationWorker

log = logging.getLogger(__name__)

class WorkerCommand(Enum):
    DeployModel = 'deploy_model'
    RunOptimization = 'run_optimization'
    Shutdown = 'shutdown'

class PingActor(GenericActor):
    class Meta:
        queue_name = 'default'

    def set_name(self, name_prefix: str, worker_id: str) -> None:
        self.name = name_prefix + worker_id

    def get_task_name(self) -> str:
        return self.name

    def perform(self):
        return 'pong'


class StatsActor(GenericActor):
    class Meta:
        queue_name = 'default'

    def __init__(self):
        self.worker_id = ''

    def set_name(self, name_prefix: str, worker_id: str) -> None:
        self.name = name_prefix + worker_id

    def get_task_name(self) -> str:
        return self.name

    def perform(self):
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'mem': psutil.virtual_memory(),
            'gpu': GPUtil.showUtilization()
        }


class WorkerActor(GenericActor):
    class Meta:
        queue_name = 'default'

    def __init__(self):
        self.conf = {}

    def init_opt_worker(self, conf: ConfigTree):
        self.conf = conf
        self.opt_worker = OptimizationWorker(conf)

    def get_task_name(self):
        return self.conf.get('tasks.worker.prefix', '') + str(self.opt_worker.id)

    def perform(self, cmd, payload):
        print('WorkerActor called with cmd={} and payload={}'.format(cmd, payload))
        if cmd == WorkerCommand.DeployModel.value:
            self.opt_worker.compile_model(payload)
        elif cmd == WorkerCommand.RunOptimization.value:
            self.opt_worker.run(payload)
        elif cmd == WorkerCommand.Shutdown.value:
            self.conf['worker.should_run'] = False
        else:
            raise AttributeError('Command does not exist: ' + str(cmd))


internal_config = ConfigFactory.parse_file('worker/internal/internal.conf')

WorkerActor.init_opt_worker(internal_config)
log.info('Created worker actor "%s"', WorkerActor.get_task_name())
StatsActor.set_name(internal_config.get(
    'tasks.stats.prefix', ''), WorkerActor.opt_worker.id)
log.info('Created stats actor "%s"', StatsActor.get_task_name())
PingActor.set_name(internal_config.get(
    'tasks.ping.prefix', ''), WorkerActor.opt_worker.id)
log.info('Created ping actor "%s"', PingActor.get_task_name())
