"""An open-addressing table with the compact layout and probe sequence CPython's dict uses. Chapter 2."""

FREE = -1
DUMMY = -2
PERTURB_SHIFT = 5


class CompactDict:
    def __init__(self, hash_fn=hash):
        self._hash = hash_fn
        self._indices = [FREE] * 8  # slot -> position in _entries, FREE or DUMMY
        self._entries = []  # (hash, key, value) in insertion order; None once deleted
        self._used = 0
        self.probes = 0

    def __len__(self):
        return self._used

    def _usable(self):
        return len(self._indices) * 2 // 3

    def _slots(self, h):
        mask = len(self._indices) - 1
        perturb = h & (2**64 - 1)  # treat negative hashes as unsigned, as the C code does
        i = perturb & mask
        while True:
            yield i
            perturb >>= PERTURB_SHIFT
            i = (i * 5 + perturb + 1) & mask

    def _find(self, key, h):
        """Returns (slot holding the key or None, first slot an insert could use)."""
        reuse = None
        for slot in self._slots(h):
            self.probes += 1
            position = self._indices[slot]
            if position == FREE:
                return None, slot if reuse is None else reuse
            if position == DUMMY:
                if reuse is None:
                    reuse = slot
                continue
            eh, ek, _ = self._entries[position]
            if eh == h and (ek is key or ek == key):
                return slot, None

    def __setitem__(self, key, value):
        h = self._hash(key)
        slot, empty = self._find(key, h)
        if slot is not None:
            self._entries[self._indices[slot]] = (h, key, value)
            return
        if len(self._entries) >= self._usable():
            self._rebuild()
            _, empty = self._find(key, h)
        self._indices[empty] = len(self._entries)
        self._entries.append((h, key, value))
        self._used += 1

    def __getitem__(self, key):
        slot, _ = self._find(key, self._hash(key))
        if slot is None:
            raise KeyError(key)
        return self._entries[self._indices[slot]][2]

    def __delitem__(self, key):
        slot, _ = self._find(key, self._hash(key))
        if slot is None:
            raise KeyError(key)
        self._entries[self._indices[slot]] = None
        self._indices[slot] = DUMMY  # not FREE: other keys' probe sequences may run through here
        self._used -= 1

    def __contains__(self, key):
        return self._find(key, self._hash(key))[0] is not None

    def __iter__(self):
        for entry in self._entries:
            if entry is not None:
                yield entry[1]

    def _rebuild(self):
        """Grow from the live count, dropping every deleted entry and dummy slot."""
        live = [e for e in self._entries if e is not None]
        size = 8
        while size * 2 // 3 <= self._used * 3:
            size *= 2
        self._indices = [FREE] * size
        self._entries = live
        for position, (h, _, _) in enumerate(live):
            for slot in self._slots(h):
                if self._indices[slot] == FREE:
                    self._indices[slot] = position
                    break
