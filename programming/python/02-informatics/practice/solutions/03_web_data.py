"""03 — JSON, XML and paginated APIs. Run: python3 03_web_data.py"""

import json
import xml.etree.ElementTree as ET
from collections.abc import Callable

API_RESPONSE = """{
  "results": [
    {"name": "University of Michigan", "location": {"lat": 42.2780, "lng": -83.7382},
     "types": ["university", "establishment"]},
    {"name": "Ann Arbor District Library", "location": {"lat": 42.2785, "lng": -83.7457},
     "types": ["library"]}
  ],
  "status": "OK"
}"""

ROSTER_XML = """<roster>
  <member role="instructor"><name>Chuck</name><course>si106</course></member>
  <member role="learner"><name>Ada</name><course>si106</course></member>
  <member role="learner"><name>Linus</name><course>si110</course></member>
  <member><name>Grace</name><course>si110</course></member>
</roster>"""


def places(raw: str) -> list[tuple[str, float, float]]:
    """Q1. Parse the API response into (name, lat, lng) tuples. If status isn't 'OK',
    raise ValueError with the status in the message."""
    data = json.loads(raw)
    if data.get("status") != "OK":
        raise ValueError(f"bad status: {data.get('status')}")
    return [(r["name"], r["location"]["lat"], r["location"]["lng"]) for r in data["results"]]


def roster(xml_text: str) -> list[dict[str, str]]:
    """Q2. One dict per <member>: name, course and role (role defaults to 'learner')."""
    root = ET.fromstring(xml_text)
    return [
        {"name": m.find("name").text, "course": m.find("course").text, "role": m.get("role", "learner")}
        for m in root.findall("member")
    ]


def fetch_all(get_page: Callable[[str | None], dict]) -> list[int]:
    """Q3. get_page(cursor) returns {'items': [...], 'next': cursor-or-None}. Start with
    cursor None and follow 'next' until it is None; return every item in order."""
    items: list[int] = []
    cursor = None
    while True:
        page = get_page(cursor)
        items.extend(page["items"])
        cursor = page.get("next")
        if cursor is None:
            return items


def to_json_lines(records: list[dict]) -> str:
    """Q4. JSON Lines: one compact JSON object per line, keys sorted, trailing newline."""
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in records)


if __name__ == "__main__":
    assert places(API_RESPONSE) == [
        ("University of Michigan", 42.278, -83.7382),
        ("Ann Arbor District Library", 42.2785, -83.7457),
    ]
    try:
        places('{"results": [], "status": "OVER_QUERY_LIMIT"}')
        raise AssertionError("expected ValueError")
    except ValueError as err:
        assert "OVER_QUERY_LIMIT" in str(err)
    r = roster(ROSTER_XML)
    assert r[0] == {"name": "Chuck", "course": "si106", "role": "instructor"}
    assert [m["role"] for m in r] == ["instructor", "learner", "learner", "learner"]
    pages = {None: {"items": [1, 2], "next": "a"}, "a": {"items": [3], "next": "b"}, "b": {"items": [], "next": None}}
    assert fetch_all(lambda c: pages[c]) == [1, 2, 3]
    assert to_json_lines([{"b": 1, "a": [1, 2]}, {"x": None}]) == '{"a":[1,2],"b":1}\n{"x":null}\n'
    print("all good")
