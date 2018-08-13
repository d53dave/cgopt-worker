#!/usr/bin/env python3
import click
import asyncio

from typing import Dict, Any
from asyncio.selector_events import BaseSelectorEventLoop

from .worker.tasks import 


should_run = True

async def sleep_one():
    while should_run:
        await asyncio.sleep(1)

@click.command()
@click.option('--redishost',
              default='localhost:9092',
              help='Kafka endpoints in the format host1:port1,...')
@click.option('--port',
              default='localhost:9092',
              help='Kafka endpoints in the format host1:port1,...')
@click.option('--password',
              default='localhost:9092',
              help='Kafka endpoints in the format host1:port1,...')
def run_worker(ctx, host, port, password):
    try:
        # TODO create and start actors

        loop = asyncio.get_event_loop()
        loop.run_until_complete(sleep_one())
    except KeyboardInterrupt:
        global should_run
        should_run = False
    finally:
        loop.stop()
        print('Exiting')

if __name__ == '__main__':
    print('Running CSAOpt')
    run_worker()
