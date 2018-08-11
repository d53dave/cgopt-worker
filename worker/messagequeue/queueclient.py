import logging
import msgpack
import msgpack_numpy
import asyncio
import psutil
import GPUtil

from typing import Dict, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from asyncio.selector_events import BaseSelectorEventLoop as EventLoop

from . import Job
from ..cuda.opt_worker import OptimizationWorker

log = logging.getLogger(__name__)

# Loading queueclient.py will cause msgpack_numpy to monkeypatch msgpack, 
# so that it can handle numerical and array data types provided by numpy
msgpack_numpy.patch()

class QueueClient:

    @classmethod
    async def create(cls, ioloop: EventLoop, conf: Dict[str, Any], worker: OptimizationWorker):
        management_recv_topic = conf['kafka.topics.management_recv']
        data_recv_topic = conf['kafka.topics.data_recv']
        management_send_topic = conf['kafka.topics.management_send']
        heartbeat_time_seconds = conf['kafka.heartbeat_time_seconds']

        consumer = AIOKafkaConsumer(
            [management_recv_topic, data_recv_topic],
            loop=ioloop, bootstrap_servers=conf['kafka.servers'],
            group_id=worker.id,
            key_deserializer=QueueClient._KeyDeserializer(),
            value_deserializer=QueueClient._ValueDeserializer())

        producer = AIOKafkaProducer(
            loop=ioloop, bootstrap_servers=conf['kafka.servers'],
            key_serializer=QueueClient._KeySerializer(),
            value_serializer=QueueClient._ValueSerializer())

        self = QueueClient(
            management_recv_topic,
            management_send_topic,
            data_recv_topic,
            consumer,
            producer
        )

        await self.consumer.start()
        await self.producer.start()

        asyncio.Task(self._periodic_send_stats())
        asyncio.Task(self._send_heartbeat(heartbeat_time_seconds))

        return self

    def __init__(self,
                 management_recv_topic: str,
                 management_send_topic: str,
                 data_recv_topic: str,
                 consumer: AIOKafkaConsumer,
                 producer: AIOKafkaProducer) -> None:
        self.worker: OptimizationWorker = {}
        self.management_recv_topic: str = management_recv_topic
        self.management_send_topic = management_send_topic
        self.data_recv_topic: str = data_recv_topic
        self.consumer = consumer
        self.producer = producer
        self.send_heartbeat = True
        self.deployed_model = None

    async def _send_heartbeat(self, heartbeat_time_seconds):
        while(self.send_heartbeat):
            await self._send_one(self.management_send_topic, key='heartbeat', value='')
            await asyncio.sleep(heartbeat_time_seconds)

    async def _periodic_send_stats(self):
        while True:
            print('periodic')
            await asyncio.sleep(2)
            await self._send_one('csaopt.stats.in.t', key='stats', value={
                'cpu': psutil.cpu_percent(interval=1),
                'mem': psutil.virtual_memory(),
                'gpu': GPUtil.showUtilization()
            })

    async def _consume(self):
        try:
            # Consume messages
            async for msg in self.consumer:
                log.debug('consumed: {} {} {} {} {} {}'.format(msg.topic, msg.partition, msg.offset,
                          msg.key, msg.value, msg.timestamp))
                if msg.topic == self.management_recv_topic:
                    if msg.key == 'model':
                        self._handle_model_deploy(msg.value)
                elif msg.topic == self.data_recv_topic:
                    if msg.key == 'job':
                        if 'worker_id' in msg.value and msg.value['worker_id'] not in self.workers:
                            pass  # Skip if worker_id is specified and we don't have that worker
                        else:
                            self._handle_job(msg.value)
                print(msg)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            self.send_heartbeat = False
            await self.consumer.stop()
            await self.producer.stop()

    def _handle_job(self, job):
        pass
            
    def _handle_model_deploy(self, model):
        self.deployed_model = model

    async def wait_for_model(self):
        while(self.deployed_model is None):
            asyncio.sleep(0.2)
        return self.deployed_model

    async def _send_one(self, topic, key=None, value=None):
        try:
            # Produce message
            await self.producer.send(topic, key=key, value=value)
        finally:
            # Wait for all pending messages to be delivered or expire.
            pass

    def get_results(self, id):
        pass

    class _KeySerializer:
        def __call__(self, key: str) -> bytes:
            return key.encode(encoding='utf_8') if key is not None else b''

    class _ValueSerializer:
        def __call__(self, value: object) -> bytes:
            return msgpack.packb(value, use_bin_type=True)

    class _KeyDeserializer:
        def __call__(self, keyBytes: bytes) -> str:
            return keyBytes.decode(encoding='utf-8') if bytes is not None else ''

    class _ValueDeserializer:
        def __call__(self, valueBytes: bytes) -> object:
            return msgpack.unpackb(valueBytes)
