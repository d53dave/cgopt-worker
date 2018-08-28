from context import PingActor


def test_ping():
    result = PingActor()

    assert result == 'pong'
