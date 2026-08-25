from app.services.retry_policy import RetryPolicy


def test_transient_status_is_retryable():
    policy = RetryPolicy()

    assert policy.should_retry(429) is True
    assert policy.should_retry(500) is True
    assert policy.should_retry(502) is True
    assert policy.should_retry(503) is True
    assert policy.should_retry(504) is True


def test_non_transient_status_is_not_retryable():
    policy = RetryPolicy()

    assert policy.should_retry(400) is False
    assert policy.should_retry(401) is False
    assert policy.should_retry(403) is False
    assert policy.should_retry(404) is False


def test_backoff_increases_exponentially():
    policy = RetryPolicy()

    assert policy.get_backoff(1) == 0.5
    assert policy.get_backoff(2) == 1.0
    assert policy.get_backoff(3) == 2.0
