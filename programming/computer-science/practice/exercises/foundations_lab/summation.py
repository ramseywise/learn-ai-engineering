"""Compensated summation. Chapter 4."""


def neumaier_sum(values):
    """Sum floats while carrying the low-order bits each addition drops.

    Plain Kahan fails when an addend is larger than the running total. Handle that case too.
    """
    raise NotImplementedError
