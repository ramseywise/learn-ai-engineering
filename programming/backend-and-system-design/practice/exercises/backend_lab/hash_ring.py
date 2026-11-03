"""Consistent hashing with virtual nodes. Chapter 4."""
import bisect
import hashlib

def stable_hash(text: str) -> int:
    """A hash that is the same in every process. Python's hash() isn't, for strings."""
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], 'big')

class HashRing:

    def __init__(self, nodes: list[str], vnodes: int=100) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def add(self, node: str) -> None:
        """Place `vnodes` points for this node on the ring."""
        raise NotImplementedError()

    def remove(self, node: str) -> None:
        """Take this node's points off the ring."""
        raise NotImplementedError()

    def owner(self, key: str) -> str:
        """The first node clockwise from the key. Raise LookupError on an empty ring."""
        raise NotImplementedError()

    def replicas(self, key: str, n: int) -> list[str]:
        """The first n distinct nodes clockwise from the key (a preference list)."""
        raise NotImplementedError()
