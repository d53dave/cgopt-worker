import os

from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker

def broker(**kwargs):
    if os.getenv('UNIT_TESTS') == '1':
        broker = StubBroker()
        broker.emit_after('process_boot')
    else:
        broker = RedisBroker(host=kwargs['host'], port=kwargs['port'], password=kwargs['password'])

    return broker
