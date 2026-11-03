"""Keyset pagination with a signed cursor. Chapter 1."""
import base64
import hashlib
import hmac
import json

class BadCursor(ValueError):
    """The cursor was malformed or has been tampered with."""

def encode_cursor(key: bytes, last: tuple) -> str:
    """Sign the sort position of the last row returned, as a URL-safe string."""
    raise NotImplementedError()

def decode_cursor(key: bytes, cursor: str) -> tuple:
    """Return the position, or raise BadCursor. Compare in constant time."""
    raise NotImplementedError()

def paginate(rows: list[dict], key: bytes, size: int, cursor: str | None=None) -> tuple[list[dict], str | None]:
    """Return one page of rows and the next cursor, or None on the last page.

    Rows sort by (created, id) descending; id breaks ties. Each row has both
    fields. Fetch size + 1 so you know whether another page exists without
    counting. `rows` stands for a table and need not be sorted.
    """
    raise NotImplementedError()
