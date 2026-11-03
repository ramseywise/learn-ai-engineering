"""Consistent hashing with virtual nodes. Chapter 4."""
import bisect
import hashlib


def stable_hash(text: str) -> int:
    """A hash that is the same in every process. Python's hash() isn't, for strings."""
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, nodes: list[str], vnodes: int = 100) -> None:
        self.vnodes = vnodes
        self.points: list[tuple[int, str]] = []
        for node in nodes:
            self.add(node)

    def add(self, node: str) -> None:
        """Place `vnodes` points for this node on the ring."""
        for i in range(self.vnodes):
            bisect.insort(self.points, (stable_hash(f"{node}#{i}"), node))

    def remove(self, node: str) -> None:
        """Take this node's points off the ring."""
        self.points = [p for p in self.points if p[1] != node]

    def owner(self, key: str) -> str:
        """The first node clockwise from the key. Raise LookupError on an empty ring."""
        return self.replicas(key, 1)[0]

    def replicas(self, key: str, n: int) -> list[str]:
        """The first n distinct nodes clockwise from the key (a preference list)."""
        if not self.points:
            raise LookupError("empty ring")
        start = bisect.bisect_left(self.points, (stable_hash(key), ""))
        found: list[str] = []
        for i in range(len(self.points)):
            node = self.points[(start + i) % len(self.points)][1]
            if node not in found:
                found.append(node)
                if len(found) == n:
                    break
        return found
