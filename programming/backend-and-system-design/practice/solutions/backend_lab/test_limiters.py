import pytest

from limiters import FixedWindow, LeakyBucket, SlidingCounter, SlidingLog, TokenBucket


def accepted(limiter, times):
    return [t for t in times if limiter.allow(t)]


def test_fixed_window_resets_and_allows_double_at_the_boundary():
    times = [59.9] * 5 + [60.0] * 5
    assert len(accepted(FixedWindow(5, 60), times)) == 10  # the documented flaw
    assert accepted(FixedWindow(2, 60), [1, 2, 3, 61]) == [1, 2, 61]


def test_sliding_log_has_no_boundary_burst():
    times = [59.9] * 5 + [60.0] * 5
    assert len(accepted(SlidingLog(5, 60), times)) == 5


def test_sliding_log_entry_leaves_at_exactly_one_window():
    limiter = SlidingLog(1, 60)
    assert limiter.allow(0)
    assert not limiter.allow(59.999)
    assert limiter.allow(60)


def test_sliding_counter_weights_the_previous_window():
    limiter = SlidingCounter(10, 60)
    assert len(accepted(limiter, [59] * 10)) == 10
    # 30 s into the next window, half of the previous 10 still counts.
    assert len(accepted(limiter, [90] * 10)) == 5


def test_sliding_counter_forgets_after_a_gap():
    limiter = SlidingCounter(2, 60)
    accepted(limiter, [1, 2])
    assert len(accepted(limiter, [125, 125, 125])) == 2


def test_token_bucket_burst_then_rate():
    limiter = TokenBucket(rate=1, burst=3)
    assert len(accepted(limiter, [0] * 5)) == 3
    assert limiter.allow(1.0)
    assert not limiter.allow(1.5)
    assert limiter.allow(2.0)


def test_token_bucket_does_not_grow_past_burst():
    limiter = TokenBucket(rate=1, burst=3)
    assert len(accepted(limiter, [1000] * 5)) == 3


def test_leaky_bucket_fills_and_drains():
    limiter = LeakyBucket(rate=2, burst=2)
    assert len(accepted(limiter, [0] * 4)) == 2
    assert limiter.allow(0.5)
    assert not limiter.allow(0.5)


@pytest.mark.parametrize("make", [
    lambda: FixedWindow(100, 60), lambda: SlidingLog(100, 60), lambda: SlidingCounter(100, 60),
])
def test_window_limiters_stay_near_the_limit_on_steady_traffic(make):
    limiter = make()
    got = accepted(limiter, [i / 10 for i in range(6000)])  # 10 per second for 600 s
    assert 900 <= len(got) <= 1100
