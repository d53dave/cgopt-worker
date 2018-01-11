#!/usr/bin/env python3
import click
import asyncio
from typing import Dict, Any
from asyncio.selector_events import BaseSelectorEventLoop
from app.messagequeue.queueclient import QueueClient


async def send_heartbeat(client: QueueClient):
    while True:
        await asyncio.sleep(1)
        await client._send_one('csaopt.')


async def run_client(loop: BaseSelectorEventLoop, config: Dict[str, Any]):
    client = await QueueClient.create(loop, config)
    await client._consume()


@click.command()
@click.option('--kafka',
              default='localhost:9092',
              help='Kafka endpoints in the format host1:port1,...')
@click.option('--multi-gpu',
              is_flag=True,
              help='Turns on multi-gpu mode')
def run_worker(ctx, kafka, multi_gpu):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_client(loop, {}))
    loop.stop()


if __name__ == '__main__':
    print('Running CSAOpt')
    run_worker()
