"""02 — HTTP with urllib, against a local server so it runs offline. Run: python3 02_http.py"""

from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


def fetch_text(url: str, timeout: float = 5) -> str:
    """Q1. GET url with a 'User-Agent: learn-python/1.0' header and a timeout; return the
    body decoded as utf-8."""
    raise NotImplementedError


def fetch_status(url: str) -> int:
    """Q2. Return the HTTP status code; a 404 must return 404, not raise."""
    raise NotImplementedError


def build_url(base: str, params: dict[str, str | int]) -> str:
    """Q3. base + '?' + the encoded params. Spaces and '&' in values must be escaped."""
    raise NotImplementedError


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and (href := dict(attrs).get("href")):
            self.hrefs.append(href)


def absolute_links(html: str, page_url: str) -> list[str]:
    """Q4. Every <a href> in html, resolved against page_url (relative links become absolute)."""
    raise NotImplementedError


if __name__ == "__main__":
    import tempfile
    import threading
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from pathlib import Path

    with tempfile.TemporaryDirectory() as root:
        Path(root, "docs").mkdir()
        Path(root, "docs", "index.html").write_text(
            '<h1>Docs</h1><a href="page2.html">next</a> <a href="/about.html">about</a>'
            ' <a href="https://example.org/">ext</a>',
            encoding="utf-8",
        )

        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=root))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            page = f"{base}/docs/index.html"
            html = fetch_text(page)
            assert html.startswith("<h1>Docs</h1>")
            assert fetch_status(page) == 200 and fetch_status(f"{base}/missing") == 404
            assert absolute_links(html, page) == [f"{base}/docs/page2.html", f"{base}/about.html", "https://example.org/"]
        finally:
            server.shutdown()

    assert build_url("https://api.example.org/search", {"q": "ann arbor & co", "limit": 5}) == (
        "https://api.example.org/search?q=ann+arbor+%26+co&limit=5"
    )
    print("all good")
