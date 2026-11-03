import pytest

from cursor import BadCursor, decode_cursor, encode_cursor, paginate

KEY = b"k" * 32
ROWS = [{"id": i, "created": 100 - i // 3} for i in range(10)]  # many ties on created


def walk(rows, size):
    seen, cursor = [], None
    while True:
        page, cursor = paginate(rows, KEY, size, cursor)
        seen += page
        if cursor is None:
            return seen


def test_round_trip():
    assert decode_cursor(KEY, encode_cursor(KEY, (5, 7))) == (5, 7)


@pytest.mark.parametrize("size", [1, 2, 3, 5, 10, 11])
def test_every_row_once_across_ties(size):
    assert [r["id"] for r in walk(ROWS, size)] == [r["id"] for r in sorted(
        ROWS, key=lambda r: (r["created"], r["id"]), reverse=True)]


def test_last_page_has_no_cursor_when_size_divides_exactly():
    page, cursor = paginate(ROWS, KEY, 5)
    page2, cursor2 = paginate(ROWS, KEY, 5, cursor)
    assert len(page) == len(page2) == 5 and cursor2 is None


def test_insert_at_the_top_does_not_shift_later_pages():
    page, cursor = paginate(ROWS, KEY, 4)
    newer = ROWS + [{"id": 99, "created": 500}]
    next_page, _ = paginate(newer, KEY, 4, cursor)
    assert next_page == paginate(ROWS, KEY, 4, cursor)[0]
    assert not {r["id"] for r in page} & {r["id"] for r in next_page}


def test_tampered_cursor_rejected():
    good = encode_cursor(KEY, (5, 7))
    flipped = ("A" if good[10] != "A" else "B").join([good[:10], good[11:]])
    with pytest.raises(BadCursor):
        decode_cursor(KEY, flipped)


def test_wrong_key_rejected():
    with pytest.raises(BadCursor):
        decode_cursor(b"z" * 32, encode_cursor(KEY, (5, 7)))
