"""Compensated summation. Chapter 4."""


def neumaier_sum(values):
    """Sum floats while carrying the low-order bits each addition drops.

    Unlike Kahan's version, this also survives an addend larger than the running total.
    """
    total = carry = 0.0
    for x in values:
        t = total + x
        if abs(total) >= abs(x):
            carry += (total - t) + x
        else:
            carry += (x - t) + total
        total = t
    return total + carry
