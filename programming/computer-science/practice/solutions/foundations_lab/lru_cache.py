"""A bounded cache that evicts the least recently used key, built on a dict and a linked list. Chapter 2."""


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None


class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.hits = self.misses = self.evictions = 0
        self._map = {}
        self._newest = _Node()  # two sentinels, so that no operation has an edge case
        self._oldest = _Node()
        self._newest.next, self._oldest.prev = self._oldest, self._newest

    def __len__(self):
        return len(self._map)

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_newest(self, node):
        node.prev, node.next = self._newest, self._newest.next
        node.next.prev = node.prev.next = node

    def get(self, key, default=None):
        node = self._map.get(key)
        if node is None:
            self.misses += 1
            return default
        self.hits += 1
        self._unlink(node)
        self._push_newest(node)
        return node.value

    def put(self, key, value):
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_newest(node)
            return
        if len(self._map) == self.capacity:
            victim = self._oldest.prev
            self._unlink(victim)
            del self._map[victim.key]
            self.evictions += 1
        node = _Node(key, value)
        self._map[key] = node
        self._push_newest(node)

    def keys_newest_first(self):
        out, node = [], self._newest.next
        while node is not self._oldest:
            out.append(node.key)
            node = node.next
        return out
