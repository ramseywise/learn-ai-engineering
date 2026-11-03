from retry_budget import Breaker, RetryBudget


def test_ratio_holds_under_total_failure():
    budget = RetryBudget(ratio=0.1, floor=0)
    retries = 0
    for _ in range(10_000):
        budget.request()
        if budget.allow_retry():
            retries += 1
    assert 990 <= retries <= 1001


def test_floor_allows_retries_at_low_traffic():
    budget = RetryBudget(ratio=0.1, floor=3)
    assert [budget.allow_retry() for _ in range(4)] == [True, True, True, False]


def test_budget_refills_as_requests_arrive():
    budget = RetryBudget(ratio=1.0, floor=0)
    assert not budget.allow_retry()
    budget.request()
    assert budget.allow_retry()
    assert not budget.allow_retry()
    budget.request()
    assert budget.allow_retry()


def trip(breaker, now=0.0):
    for _ in range(breaker.threshold):
        assert breaker.allow(now)
        breaker.record(False, now)


def test_opens_after_threshold_in_a_row():
    b = Breaker(threshold=3, cool_down=30)
    trip(b)
    assert not b.allow(1.0)


def test_a_success_resets_the_run():
    b = Breaker(threshold=3)
    for ok in (False, False, True, False, False):
        b.record(ok, 0.0)
    assert b.allow(0.0)


def test_half_open_allows_exactly_one_trial():
    b = Breaker(threshold=3, cool_down=30)
    trip(b)
    assert not b.allow(29.9)
    assert b.allow(30.0)
    assert not b.allow(30.0)


def test_successful_trial_closes():
    b = Breaker(threshold=3, cool_down=30)
    trip(b)
    assert b.allow(30.0)
    b.record(True, 30.1)
    assert b.allow(30.1) and b.allow(30.2)


def test_failed_trial_reopens_for_a_full_cool_down():
    b = Breaker(threshold=3, cool_down=30)
    trip(b)
    assert b.allow(30.0)
    b.record(False, 31.0)
    assert not b.allow(60.9)
    assert b.allow(61.0)
