from context import StatsActor


def test_get_stats():
    result = StatsActor()
    assert type(result) == dict
    assert type(result['cpu']) == float
    assert type(result['mem']) is not None
    assert type(result['gpu']) is not None
