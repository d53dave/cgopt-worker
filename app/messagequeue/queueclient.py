import os

from aiokafka import AIOKafkaProducer
import asyncio

class QueueClient:

    @classmethod
    async def create(cls, ioloop, **conf):
        self = QueueClient()
        self.conf = conf
        self.consumer = AIOKafkaConsumer(
            *conf['kafka.topics'],
            loop=ioloop, bootstrap_servers=conf['kafka.servers'],
            group_id=conf['kafka.group'])

        self.producer = AIOKafkaProducer(
            loop=ioloop, bootstrap_servers=conf['kafka.servers'])

        await self.consumer.start()
        await self.producer.start()

        return self

    async def consume(self):
        try:
            # Consume messages
            async for msg in consumer:
                log.debug("consumed: ", msg.topic, msg.partition, msg.offset,
                    msg.key, msg.value, msg.timestamp)
                if(msg.topic == 'data')
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

    async def send_one(topic, msg):
        try:
            # Produce message
            await producer.send_and_wait(topic, msg)
        finally:
            # Wait for all pending messages to be delivered or expire.
            await producer.stop()
        
