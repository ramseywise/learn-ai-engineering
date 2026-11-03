"""A small log-structured store: log, memtable, sorted tables, compaction. Chapter 9."""
import bisect
import json
import os
from pathlib import Path

class MiniKV:

    def __init__(self, folder: str | Path, memtable_limit: int=4) -> None:
        """Open a store, reloading tables and replaying the log.

        A torn last log line is ignored: it was never acknowledged. The tests
        read two attributes: `memtable`, a dict, and `tables`, a list of
        (sorted keys, values) pairs, oldest first.
        """
        raise NotImplementedError()

    def put(self, key: str, value: str) -> None:
        """Log first, then the memtable; flush when it's full."""
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        """Write a tombstone (None), since older tables may hold the key."""
        raise NotImplementedError()

    def get(self, key: str) -> str | None:
        """Memtable, then tables newest first. A tombstone means not found."""
        raise NotImplementedError()

    def flush(self) -> None:
        """Write the memtable as a sorted table, then empty the log."""
        raise NotImplementedError()

    def compact(self) -> None:
        """Major compaction: merge all tables, newest wins, and drop tombstones."""
        raise NotImplementedError()

    def close(self) -> None:
        """Close the log file."""
        raise NotImplementedError()
