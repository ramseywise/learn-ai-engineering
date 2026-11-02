"""A growable array, instrumented, so that growth policies can be compared. Chapters 1 and 2.

Keep `resizes` (how many times storage was replaced) and `copies` (how many elements were moved).
Use a plain Python list as the fixed-size storage; don't call its append or pop.
"""


class DynamicArray:
    def __init__(self, grow=lambda capacity: capacity * 2):
        """`grow` maps the current capacity to a larger one. Start at capacity 1."""
        self.resizes = 0
        self.copies = 0
        raise NotImplementedError

    @property
    def capacity(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, i):
        """Raise IndexError outside 0..len-1."""
        raise NotImplementedError

    def append(self, value):
        raise NotImplementedError

    def pop(self):
        """Remove and return the last value. Shrink so that pop/append at a boundary can't thrash."""
        raise NotImplementedError
