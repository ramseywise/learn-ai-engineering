"""Sizing a worker pool with Erlang C. Chapter 5."""
import math


def erlang_c(servers: int, offered: float) -> float:
    """Probability that an arrival waits in M/M/c; offered = arrival rate x service time.

    Use the Erlang B recurrence. Return 1.0 when offered >= servers.
    """
    if offered >= servers:
        return 1.0
    b = 1.0
    for k in range(1, servers + 1):
        b = offered * b / (k + offered * b)
    rho = offered / servers
    return b / (1 - rho + rho * b)


def wait(servers: int, arrival: float, service: float) -> float:
    """Mean time in the queue, in seconds. math.inf when the pool can't keep up."""
    offered = arrival * service
    if offered >= servers:
        return math.inf
    return erlang_c(servers, offered) * service / (servers - offered)


def size_for(arrival: float, service: float, target_wait: float) -> int:
    """The smallest worker count whose mean wait is at or under target_wait."""
    servers = max(1, math.floor(arrival * service) + 1)
    while wait(servers, arrival, service) > target_wait:
        servers += 1
    return servers
