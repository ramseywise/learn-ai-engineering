---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 13 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
  - "Python docs, json and xml.etree.ElementTree — https://docs.python.org/3/library/json.html"
concepts: [json, xml, elementtree, rest-apis, api-keys, serialization]
cleaned: 2026-10-29
---
# 3 — Web Data: JSON, XML and APIs

> Programs exchange data as text in an agreed format. JSON won for APIs. XML is still around in feeds, office files and enterprise systems. Parse either into Python objects, then work with dicts and lists.

---

## JSON

```python
import json

data = json.loads('{"name": "Ada", "langs": ["py", "ts"], "active": true, "manager": null}')
data["langs"][0]                  # 'py'
json.dumps(data, indent=2)        # back to text
with open("out.json", "w", encoding="utf-8") as fh:
    json.dump(data, fh)
```

| JSON | Python |
|---|---|
| object `{}` | `dict` |
| array `[]` | `list` |
| string, number | `str`, `int`/`float` |
| `true`/`false`/`null` | `True`/`False`/`None` |

`json.loads` raises `json.JSONDecodeError` on malformed input. Parsing JSON gives you dicts of *anything*, so validate the shape before you trust it. Pydantic does that ([Python 03 · note 05](../../03-language-for-engineers/notes/05-types-and-dataclasses.md)).

## XML

```python
import xml.etree.ElementTree as ET

root = ET.fromstring("""<stuff><users>
  <user x="2"><id>001</id><name>Chuck</name></user>
  <user x="7"><id>009</id><name>Brent</name></user>
</users></stuff>""")
for user in root.findall("users/user"):
    print(user.find("name").text, user.get("x"))
```

`find` returns the first match or `None`, and `findall` returns a list. Both take a simple path syntax. For untrusted XML, use `defusedxml`.

## Calling an API

1. Read the docs for the base URL, authentication, rate limits and pagination.
2. Build the URL with `urlencode`, and put the key in a header (`Authorization: Bearer …`) or a parameter.
3. Check the status, then parse the JSON.
4. Follow the pagination (a `next` link or cursor) until it runs out.
5. Cache responses during development, so you don't spend your quota re-fetching.

**Keep keys out of code.** Read them from the environment (`os.environ["API_KEY"]`) and keep `.env` files out of git.

---

## Exercises

[`practice/exercises/03_web_data.py`](../practice/exercises/03_web_data.py): flatten a nested JSON API response, read XML records, and follow pagination over fake pages.
