"""Keyset pagination with a signed cursor. Chapter 1."""
import base64
import hashlib
import hmac
import json


class BadCursor(ValueError):
    """The cursor was malformed or has been tampered with."""


def encode_cursor(key: bytes, last: tuple) -> str:
    """Sign the sort position of the last row returned, as a URL-safe string."""
    body = json.dumps(list(last), separators=(",", ":")).encode()
    mac = hmac.new(key, body, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac + body).decode().rstrip("=")


def decode_cursor(key: bytes, cursor: str) -> tuple:
    """Return the position, or raise BadCursor. Compare in constant time."""
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
    except ValueError as err:
        raise BadCursor("not base64") from err
    mac, body = raw[:32], raw[32:]
    if not hmac.compare_digest(mac, hmac.new(key, body, hashlib.sha256).digest()):
        raise BadCursor("bad signature")
    return tuple(json.loads(body))


def paginate(rows: list[dict], key: bytes, size: int, cursor: str | None = None) -> tuple[list[dict], str | None]:
    """Return one page of rows and the next cursor, or None on the last page.

    Rows sort by (created, id) descending; id breaks ties. Each row has both
    fields. Fetch size + 1 so you know whether another page exists without
    counting. `rows` stands for a table and need not be sorted.
    """
    ordered = sorted(rows, key=lambda r: (r["created"], r["id"]), reverse=True)
    if cursor is not None:
        position = decode_cursor(key, cursor)
        ordered = [r for r in ordered if (r["created"], r["id"]) < position]
    fetched = ordered[: size + 1]
    page = fetched[:size]
    if len(fetched) > size:
        return page, encode_cursor(key, (page[-1]["created"], page[-1]["id"]))
    return page, None
