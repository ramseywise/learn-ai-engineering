"""05 — Normalised ingest with sqlite3. Run: python3 05_databases.py"""

import sqlite3

TRACKS = [
    # (title, artist, album, plays)
    ("Another One Bites The Dust", "Queen", "Greatest Hits", 55),
    ("Bohemian Rhapsody", "Queen", "Greatest Hits", 63),
    ("Who Made Who", "AC/DC", "Who Made Who", 18),
    ("For Those About To Rock", "AC/DC", "Who Made Who", 12),
    ("Bohemian Rhapsody", "Queen", "Greatest Hits", 64),  # re-imported with an updated play count
]

SCHEMA = """
CREATE TABLE artist (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE album  (id INTEGER PRIMARY KEY, title TEXT UNIQUE NOT NULL,
                     artist_id INTEGER NOT NULL REFERENCES artist(id));
CREATE TABLE track  (id INTEGER PRIMARY KEY, title TEXT UNIQUE NOT NULL,
                     album_id INTEGER NOT NULL REFERENCES album(id), plays INTEGER NOT NULL);
"""


def connect() -> sqlite3.Connection:
    """Given. An in-memory database with the schema."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    return conn


def load(conn: sqlite3.Connection, rows: list[tuple[str, str, str, int]]) -> None:
    """Q1. Insert every row in ONE transaction. Each artist and album is stored once
    (get-or-create with INSERT OR IGNORE + SELECT id); a repeated track title updates plays.
    Use ? parameters."""
    raise NotImplementedError


def plays_by_artist(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    """Q2. (artist, total plays) for every artist, most-played first. Needs two joins."""
    raise NotImplementedError


if __name__ == "__main__":
    conn = connect()
    load(conn, TRACKS)
    assert conn.execute("SELECT count(*) FROM artist").fetchone()[0] == 2
    assert conn.execute("SELECT count(*) FROM album").fetchone()[0] == 2
    assert conn.execute("SELECT count(*) FROM track").fetchone()[0] == 4
    assert conn.execute("SELECT plays FROM track WHERE title = 'Bohemian Rhapsody'").fetchone()[0] == 64
    assert plays_by_artist(conn) == [("Queen", 119), ("AC/DC", 30)]
    load(conn, TRACKS)  # re-running the load must not duplicate anything
    assert conn.execute("SELECT count(*) FROM track").fetchone()[0] == 4
    print("all good")
