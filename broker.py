import dramatiq
import os
import msgpack
import msgpack_numpy

from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

msgpack_numpy.patch()


def is_pytest_run():
    return os.environ.get('UNIT_TESTS') == '1'


class MsgPackEncoder(dramatiq.Encoder):
    # MessageData = typing.Dict[str, typing.Any]
    def encode(self, data: dramatiq.encoder.MessageData) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    def decode(self, data: bytes) -> dramatiq.encoder.MessageData:
        return msgpack.unpackb(data, raw=False)


if is_pytest_run():
    broker = StubBroker()
    broker.emit_after('process_boot')
else:
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = os.environ.get('REDIS_PORT', 6379)
    pwd = os.environ.get('REDIS_PWD')
    broker = RedisBroker(host=host, port=port, password=pwd)
    broker.add_middleware(
        Results(backend=RedisBackend(client=broker.client, encoder=MsgPackEncoder())))

dramatiq.set_broker(broker)
dramatiq.set_encoder(MsgPackEncoder())
