import math

import pytest

from erlang import erlang_c, size_for, wait


def direct(c, a):
    """The textbook formula, usable for small c."""
    top = a**c / math.factorial(c) * c / (c - a)
    return top / (sum(a**k / math.factorial(k) for k in range(c)) + top)


@pytest.mark.parametrize("c,a", [(1, 0.5), (2, 1.0), (5, 3.5), (16, 12.8), (20, 19.0)])
def test_matches_the_direct_formula(c, a):
    assert erlang_c(c, a) == pytest.approx(direct(c, a))


def test_one_server_is_m_m_1():
    # M/M/1: P(wait) = rho, W = rho * s / (1 - rho).
    assert erlang_c(1, 0.8) == pytest.approx(0.8)
    assert wait(1, 80, 0.01) == pytest.approx(0.04)


def test_huge_pool_does_not_overflow():
    assert 0 <= erlang_c(5000, 4900.0) < 1


def test_overload():
    assert erlang_c(4, 4.0) == 1.0
    assert erlang_c(4, 9.0) == 1.0
    assert wait(4, 400, 0.01) == math.inf


def test_size_for_is_the_smallest_that_meets_the_target():
    n = size_for(1000, 0.01, 0.002)
    assert wait(n, 1000, 0.01) <= 0.002 < wait(n - 1, 1000, 0.01)


def test_size_for_light_load():
    assert size_for(1, 0.01, 1.0) == 1
