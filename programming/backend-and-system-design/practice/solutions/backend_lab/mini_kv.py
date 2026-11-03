"""A small log-structured store: log, memtable, sorted tables, compaction. Chapter 9."""
import bisect
import json
import os
from pathlib import Path


class MiniKV:
    def __init__(self, folder: str | Path, memtable_limit: int = 4) -> None:
        """Open a store, reloading tables and replaying the log.

        A torn last log line is ignored: it was never acknowledged. The tests
        read two attributes: `memtable`, a dict, and `tables`, a list of
        (sorted keys, values) pairs, oldest first.
        """
        self.folder, self.limit = Path(folder), memtable_limit
        self.memtable: dict[str, str | None] = {}
        self.tables: list[tuple[list[str], list[str | None]]] = []
        self.paths = sorted(self.folder.glob("table-*.json"), key=lambda p: int(p.stem.split("-")[1]))
        for path in self.paths:
            self.tables.append(self._load(path))
        self.seq = int(self.paths[-1].stem.split("-")[1]) if self.paths else 0
        self.wal_path = self.folder / "wal.log"
        self._replay()
        self.wal = open(self.wal_path, "a")

    @staticmethod
    def _load(path: Path) -> tuple[list[str], list[str | None]]:
        items = json.loads(path.read_text())
        return [k for k, _ in items], [v for _, v in items]

    def _replay(self) -> None:
        if not self.wal_path.exists():
            return
        for line in self.wal_path.read_text().splitlines():
            try:
                key, value = json.loads(line)
            except json.JSONDecodeError:
                break
            self.memtable[key] = value

    def _log(self, key: str, value: str | None) -> None:
        self.wal.write(json.dumps([key, value]) + "\n")
        self.wal.flush()
        os.fsync(self.wal.fileno())
        self.memtable[key] = value
        if len(self.memtable) >= self.limit:
            self.flush()

    def put(self, key: str, value: str) -> None:
        """Log first, then the memtable; flush when it's full."""
        self._log(key, value)

    def delete(self, key: str) -> None:
        """Write a tombstone (None), since older tables may hold the key."""
        self._log(key, None)

    def get(self, key: str) -> str | None:
        """Memtable, then tables newest first. A tombstone means not found."""
        if key in self.memtable:
            return self.memtable[key]
        for keys, values in reversed(self.tables):
            i = bisect.bisect_left(keys, key)
            if i < len(keys) and keys[i] == key:
                return values[i]
        return None

    def _write_table(self, items: list) -> Path:
        self.seq += 1
        path = self.folder / f"table-{self.seq}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(items))
        os.replace(tmp, path)
        return path

    def flush(self) -> None:
        """Write the memtable as a sorted table, then empty the log."""
        if not self.memtable:
            return
        self.paths.append(self._write_table(sorted(self.memtable.items())))
        self.tables.append(self._load(self.paths[-1]))
        self.memtable = {}
        self.wal.close()
        self.wal = open(self.wal_path, "w")

    def compact(self) -> None:
        """Major compaction: merge all tables, newest wins, and drop tombstones."""
        merged: dict[str, str | None] = {}
        for keys, values in self.tables:
            merged.update(zip(keys, values))
        path = self._write_table(sorted((k, v) for k, v in merged.items() if v is not None))
        for old in self.paths:
            old.unlink()
        self.paths, self.tables = [path], [self._load(path)]

    def close(self) -> None:
        """Close the log file."""
        self.wal.close()
