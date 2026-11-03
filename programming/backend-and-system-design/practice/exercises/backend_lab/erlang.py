"""Sizing a worker pool with Erlang C. Chapter 5."""
import math

def erlang_c(servers: int, offered: float) -> float:
    """Probability that an arrival waits in M/M/c; offered = arrival rate x service time.

    Use the Erlang B recurrence. Return 1.0 when offered >= servers.
    """
    raise NotImplementedError()

def wait(servers: int, arrival: float, service: float) -> float:
    """Mean time in the queue, in seconds. math.inf when the pool can't keep up."""
    raise NotImplementedError()

def size_for(arrival: float, service: float, target_wait: float) -> int:
    """The smallest worker count whose mean wait is at or under target_wait."""
    raise NotImplementedError()
