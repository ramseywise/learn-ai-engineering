"""A growable array, instrumented, so that growth policies can be compared. Chapters 1 and 2."""


class DynamicArray:
    def __init__(self, grow=lambda capacity: capacity * 2):
        """`grow` maps the current capacity to a larger one."""
        self._grow = grow
        self._slots = [None]
        self._size = 0
        self.resizes = 0
        self.copies = 0

    @property
    def capacity(self):
        return len(self._slots)

    def __len__(self):
        return self._size

    def __getitem__(self, i):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._slots[i]

    def _resize(self, capacity):
        fresh = [None] * capacity
        for i in range(self._size):
            fresh[i] = self._slots[i]
        self.copies += self._size
        self.resizes += 1
        self._slots = fresh

    def append(self, value):
        if self._size == self.capacity:
            capacity = self._grow(self.capacity)
            if capacity <= self.capacity:
                raise ValueError("grow must return a larger capacity")
            self._resize(capacity)
        self._slots[self._size] = value
        self._size += 1

    def pop(self):
        if not self._size:
            raise IndexError("pop from empty array")
        self._size -= 1
        value, self._slots[self._size] = self._slots[self._size], None
        # Shrink at a quarter full, not at half: an append right after a pop must not resize again.
        if self.capacity > 1 and self._size <= self.capacity // 4:
            self._resize(max(1, self.capacity // 2))
        return value
