import dramatiq
import msgpack
import msgpack_numpy

from dramatiq.brokers.redis import RedisBroker


class MsgPackEncoder(dramatiq.Encoder):
    def __init__(self):
        msgpack_numpy.patch()

    # MessageData = typing.Dict[str, typing.Any]
    def encode(self, data: dramatiq.encoder.MessageData) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    def decode(self, data: bytes) -> dramatiq.encoder.MessageData:
        return msgpack.unpackb(data)


broker = RedisBroker(host='localhost', port=6379)

dramatiq.set_broker(broker)
dramatiq.set_encoder(MsgPackEncoder())
