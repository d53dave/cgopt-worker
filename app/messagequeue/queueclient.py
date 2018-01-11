import logging
import msgpack
import asyncio
import psutil
import GPUtil

from typing import Dict, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from asyncio.selector_events import BaseSelectorEventLoop as EventLoop

from app.jobs import Job
from . import Worker

log = logging.getLogger(__name__)


class QueueClient:

    @classmethod
    async def create(cls, ioloop: EventLoop, conf: Dict[str, Any], worker: Worker):
        management_recv_topic = conf['kafka.topics.management_recv']
        data_recv_topic = conf['kafka.topics.data_recv']
        management_send_topic = conf['kafka.topics.management_send']

        consumer = AIOKafkaConsumer(
            [management_recv_topic, data_recv_topic],
            loop=ioloop, bootstrap_servers=conf['kafka.servers'],
            group_id=conf['kafka.consumer_group'],
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
        asyncio.Task(self._send_heartbeat())

        return self

    def __init__(self,
                 management_recv_topic: str,
                 management_send_topic: str,
                 data_recv_topic: str,
                 consumer: AIOKafkaConsumer,
                 producer: AIOKafkaProducer) -> None:
        self.workers: Dict[str, Worker] = {}
        self.management_recv_topic: str = management_recv_topic
        self.management_send_topic = management_send_topic
        self.data_recv_topic: str = data_recv_topic
        self.consumer = consumer
        self.producer = producer

    async def _send_heartbeat(self, heartbeat_time_seconds):
        while(True):
            await self._send_one()
            await asyncio.sleep(heartbeat_time_seconds)

    async def _periodic_send_stats(self):
        while True:
            print('periodic')
            await asyncio.sleep(2)
            await self._send_one('csaopt.stats.in.t', value={
                'cpu': psutil.cpu_percent(interval=1),
                'mem': psutil.virtual_memory(),
                'gpu': GPUtil.showUtilization()
            })

    async def _consume(self):
        try:
            # Consume messages
            async for msg in self.consumer:
                log.debug("consumed: ", msg.topic, msg.partition, msg.offset,
                          msg.key, msg.value, msg.timestamp)
                if msg.topic == self.management_recv_topic:
                    pass
                if msg.topic == self.data_recv_topic:
                    pass
                print(msg)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()
            await self.producer.stop()

    async def _send_one(self, topic, key=None, value=None):
        try:
            # Produce message
            await self.producer.send(topic, key=key, value=value)
        finally:
            # Wait for all pending messages to be delivered or expire.
            pass

    async def submit_job(self, job: Job):
        # self.submitted[job.id] = job
        pass

    def get_results(id):
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
