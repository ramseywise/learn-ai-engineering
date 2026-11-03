import pytest

from token_budget import OverBudget, TokenBudget


def test_reserve_holds_the_worst_case():
    b = TokenBudget(limit=100, window=60)
    b.reserve("a", 10, 30, now=0)
    assert b.remaining("a", 0) == 60


def test_refusal_holds_nothing():
    b = TokenBudget(limit=100, window=60)
    b.reserve("a", 10, 80, now=0)
    with pytest.raises(OverBudget):
        b.reserve("a", 1, 10, now=0)
    assert b.remaining("a", 0) == 10


def test_exact_fit_is_allowed():
    b = TokenBudget(limit=100, window=60)
    b.reserve("a", 50, 50, now=0)
    assert b.remaining("a", 0) == 0


def test_settle_returns_the_unused_part():
    b = TokenBudget(limit=100, window=60)
    r = b.reserve("a", 10, 80, now=0)
    b.settle(r, 25)
    assert b.remaining("a", 0) == 75


def test_concurrent_reservations_cannot_overspend():
    b = TokenBudget(limit=100, window=60)
    held = [b.reserve("a", 10, 15, now=0) for _ in range(4)]
    with pytest.raises(OverBudget):
        b.reserve("a", 1, 0, now=0)
    for r in held:
        b.settle(r, 25)
    assert b.remaining("a", 0) == 0


def test_release_gives_everything_back():
    b = TokenBudget(limit=100, window=60)
    b.release(b.reserve("a", 10, 80, now=0))
    assert b.remaining("a", 0) == 100


def test_settling_twice_is_an_error():
    b = TokenBudget(limit=100, window=60)
    r = b.reserve("a", 10, 10, now=0)
    b.settle(r, 5)
    with pytest.raises(ValueError):
        b.settle(r, 5)
    with pytest.raises(ValueError):
        b.release(r)
    assert b.remaining("a", 0) == 95


def test_tenants_are_separate():
    b = TokenBudget(limit=100, window=60)
    b.reserve("a", 50, 50, now=0)
    assert b.remaining("b", 0) == 100


def test_window_resets_on_the_clock():
    b = TokenBudget(limit=100, window=60)
    b.settle(b.reserve("a", 50, 50, now=59.9), 100)
    assert b.remaining("a", 59.9) == 0
    assert b.remaining("a", 60.0) == 100


def test_a_response_finishing_in_the_next_window_counts_in_the_one_it_started():
    b = TokenBudget(limit=100, window=60)
    r = b.reserve("a", 10, 40, now=59)
    b.settle(r, 30)
    assert b.remaining("a", 60) == 100
    assert b.remaining("a", 59) == 70


def test_real_usage_above_the_hold_is_recorded():
    b = TokenBudget(limit=100, window=60)
    b.settle(b.reserve("a", 10, 10, now=0), 120)
    assert b.remaining("a", 0) == -20
    with pytest.raises(OverBudget):
        b.reserve("a", 1, 1, now=0)
