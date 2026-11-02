"""A bounded cache that evicts the least recently used key, built on a dict and a linked list. Chapter 2.

get and put must be constant time. Don't use OrderedDict here: the point is to see what it does for you.
"""


class LRUCache:
    def __init__(self, capacity):
        """Raise ValueError if capacity < 1. Keep `hits`, `misses` and `evictions` counters."""
        self.capacity = capacity
        self.hits = self.misses = self.evictions = 0
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def keys_newest_first(self):
        raise NotImplementedError
