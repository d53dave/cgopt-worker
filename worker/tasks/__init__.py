import psutil
import GPUtil

from enum import Enum
from dramatiq import GenericActor

from ..cuda.opt_worker import OptimizationWorker

class WorkerCommand(Enum):
    DeployModel: 'deploy_model'
    RunOptimization: 'run_optimization'

class StatsActor(GenericActor):
    class Meta:
        queue_name = "csaopt_stats"

    def __init__(self, name):
        self.id = id

    def get_task_name(self):
        return self.name

    def perform(self):
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'mem': psutil.virtual_memory(),
            'gpu': GPUtil.showUtilization()
        }
    

class WorkerActor(GenericActor):
    class Meta:
        queue_name = "csaopt"

    def __init__(self, conf):
        self.conf = conf
        self.opt_worker = OptimizationWorker(conf)

    def get_task_name(self):
        return self.conf.get('tasks.worker.prefix', '') + str(self.opt_worker.id)

    def perform(self, cmd, payload):
        if cmd == WorkerCommand.DeployModel.value:
            self.opt_worker.compile_model(payload)
        elif cmd == WorkerCommand.RunOptimization.value:
            self.opt_worker.run(payload)
        


