---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 12 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
  - "MDN, An overview of HTTP — https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview"
concepts: [http, sockets, urllib, http-status-codes, web-scraping, html-parsing]
cleaned: 2026-10-29
---
# 2 — Networks and HTTP

> HTTP is text over a socket: a request line and headers go out, and a status line, headers, a blank line and a body come back. Every web API is built on that.

---

## What's on the wire

```text
GET /page1.htm HTTP/1.1          ← request line: method, path, version
Host: data.example.org           ← headers
                                 ← blank line ends the request
HTTP/1.1 200 OK                  ← status line
Content-Type: text/html; charset=utf-8
Content-Length: 70
                                 ← blank line separates headers from the body
<h1>The First Page</h1> …
```

py4e starts with a raw `socket` to show that nothing is magic. In practice, use a client library.

| Status | Meaning |
|---|---|
| 2xx | Success (`200 OK`, `201 Created`, `204 No Content`) |
| 3xx | Redirect: follow the `Location` header |
| 4xx | Your mistake (`400` bad request, `401`/`403` auth, `404` not found, `429` too many requests) |
| 5xx | Their mistake. Usually worth retrying with backoff |

## `urllib` (standard library)

```python
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urljoin

url = "https://api.example.org/search?" + urlencode({"q": "ann arbor", "limit": 5})
req = Request(url, headers={"User-Agent": "learn-python/1.0"})
with urlopen(req, timeout=10) as resp:       # raises HTTPError for 4xx/5xx
    body = resp.read().decode("utf-8")       # bytes → str
```

- **Always set a timeout.** Without one, a stalled server hangs your program forever.
- `urlencode` escapes query values. Never build a query string by pasting values together.
- `urljoin(base, "../a.html")` resolves relative links the way a browser does.

In real projects, use **`httpx`** or **`requests`**: `httpx.get(url, params={...}, timeout=10).raise_for_status().json()`. `httpx` also supports `async` ([Python 03 · note 07](../../03-language-for-engineers/notes/07-concurrency.md)).

## Scraping HTML

```python
from html.parser import HTMLParser       # stdlib; BeautifulSoup (bs4) is friendlier

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a" and (href := dict(attrs).get("href")):
            self.links.append(href)
```

Scrape politely: check `robots.txt` and the terms of service, add a delay between requests, cache what you've fetched, and use an API when one exists.

---

## Exercises

[`practice/exercises/02_http.py`](../practice/exercises/02_http.py) starts a local HTTP server in a thread, so it runs offline: fetch with `urllib`, handle a 404, and parse links.
