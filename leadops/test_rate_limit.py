from rate_limit import RateLimiter


def test_rate_limit_blocks_after_threshold():
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("client")
    assert limiter.allow("client")
    assert not limiter.allow("client")
