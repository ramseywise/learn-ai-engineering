"""09 — SQL from Python (standard library only).

Run from programming/sql/practice:  python3 exercises/09_sql_from_python.py
Each function has asserts underneath; the file passes when it prints "all good".
"""
import sqlite3
from contextlib import closing
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "clubdata.db"


def connect(path=DB) -> sqlite3.Connection:
    """Given. Open a connection whose rows behave like dicts (row["surname"])."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def members_joined_since(conn, date: str) -> list[str]:
    """Q1. Surnames of members who joined on/after `date`, oldest join first.
    Pass `date` as a parameter — never format it into the SQL string."""
    raise NotImplementedError


def find_member(conn, surname: str) -> list[int]:
    """Q2. memids for an exact surname. Must be safe against injection."""
    raise NotImplementedError


def slots_by_facility(conn) -> dict[str, int]:
    """Q3. {facility name: total slots}. Aggregate in SQL, not in Python."""
    raise NotImplementedError


def load_ratings(conn, ratings: list[tuple[int, int, int]]) -> int:
    """Q4. Create ratings(memid, facid, stars 1–5) and insert all rows in ONE transaction
    with executemany. If any row is invalid, nothing is inserted. Return the row count."""
    raise NotImplementedError


if __name__ == "__main__":
    with closing(connect()) as conn:
        assert members_joined_since(conn, "2012-09-18")[:3] == ["Purview", "Tupperware", "Hunt"]
        assert find_member(conn, "Smith") == [1, 2, 14, 37]
        assert find_member(conn, "x' OR '1'='1") == []
        totals = slots_by_facility(conn)
        assert len(totals) == 9 and totals["Massage Room 1"] == 1404

    with closing(sqlite3.connect(":memory:")) as mem:
        mem.executescript((DB.parent / "clubdata.sql").read_text())
        mem.row_factory = sqlite3.Row
        assert load_ratings(mem, [(1, 0, 5), (2, 4, 3)]) == 2
        try:
            load_ratings(mem, [(3, 1, 4), (4, 1, 9)])  # 9 stars violates the CHECK
        except sqlite3.IntegrityError:
            pass
        assert mem.execute("SELECT count(*) FROM ratings").fetchone()[0] == 2  # rolled back

    print("all good")
