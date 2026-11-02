"""An open-addressing table with the compact layout and probe sequence CPython's dict uses. Chapter 2.

Two arrays: `_indices`, a power-of-two table of positions, and `_entries`, (hash, key, value) tuples in
insertion order. Probe with i = (i * 5 + perturb + 1) & mask, where perturb starts as the hash, is treated
as unsigned, and is shifted right by 5 before each step. Keep the table at most two-thirds used.
Count every slot you look at in `self.probes`.
"""

FREE = -1
DUMMY = -2
PERTURB_SHIFT = 5


class CompactDict:
    def __init__(self, hash_fn=hash):
        self._hash = hash_fn
        self._indices = [FREE] * 8
        self._entries = []
        self._used = 0
        self.probes = 0

    def __len__(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __delitem__(self, key):
        """Why can't the slot simply go back to FREE?"""
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError

    def __iter__(self):
        """Yield keys in insertion order, skipping deleted ones."""
        raise NotImplementedError
