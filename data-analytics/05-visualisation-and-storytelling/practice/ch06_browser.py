# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "fastapi", "uvicorn", "playwright", "plotly", "dash", "matplotlib"]
# ///
"""Chapter 6, in a real browser: SVG versus WebGL drawing time, and the two finished dashboards.

Needs Google Chrome, and `npm install && npm run app` in js/ first. Run: uv run ch06_browser.py"""
# %% setup
import gzip
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright

import chartstyle as cs
import segments

HERE = Path(__file__).resolve().parent
PLOTLY = HERE / "js/node_modules/plotly.js-dist-min/plotly.min.js"
table = segments.build_table()
DRAW = """async ({type, n, xs, ys}) => {
  const box = document.createElement('div');
  document.body.replaceChildren(box);
  const start = performance.now();
  await Plotly.newPlot(box, [{type, mode: 'markers', x: xs.slice(0, n), y: ys.slice(0, n), marker: {size: 4}}],
                       {width: 800, height: 500});
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return performance.now() - start;
}"""


def record_bytes(page):
    """Sum what a page fetches, raw and as gzip level 6 would send it, so the two apps compare fairly."""
    bodies = {}

    def keep(response):
        try:
            bodies[response.url] = response.body()
        except Exception:
            pass
    page.on("response", keep)
    return bodies


def report_bytes(name, bodies):
    raw = sum(len(b) for b in bodies.values())
    packed = sum(len(gzip.compress(b, 6)) for b in bodies.values())
    print(f"{name}: {len(bodies)} files, {raw / 1024:,.0f} KB, {packed / 1024:,.0f} KB if gzipped")


def wait_for(url, seconds=30):
    for _ in range(seconds * 4):
        try:
            return urllib.request.urlopen(url)
        except OSError:
            time.sleep(.25)
    raise RuntimeError(f"{url} never answered")


# %% draw-times
rng = np.random.default_rng(1)
many = 400_000
xs = np.resize(table.x.values, many) + rng.normal(0, .02, many)
ys = np.resize(table.y.values, many) + rng.normal(0, .02, many)
xs, ys = xs.round(3).tolist(), ys.round(3).tolist()

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True, args=["--use-angle=default", "--enable-gpu"])
    print("chrome", browser.version)
    page = browser.new_page()
    page.goto("about:blank")
    page.add_script_tag(path=str(PLOTLY))
    print("plotly.js", page.evaluate("Plotly.version"), "| WebGL renderer:", page.evaluate("""() => {
        const gl = document.createElement('canvas').getContext('webgl');
        const info = gl && gl.getExtension('WEBGL_debug_renderer_info');
        return info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : 'none'; }"""))
    print(f"{'points':>9}{'SVG scatter ms':>16}{'WebGL scattergl ms':>20}")
    for n in (1_000, 10_000, 50_000, 200_000, 400_000):
        row = {}
        for kind in ("scatter", "scattergl"):
            if kind == "scatter" and n > 50_000:
                row[kind] = None
                continue
            page.evaluate(DRAW, dict(type=kind, n=min(n, 1000), xs=xs, ys=ys))  # warm the code path
            row[kind] = sorted(page.evaluate(DRAW, dict(type=kind, n=n, xs=xs, ys=ys)) for _ in range(3))[1]
        svg = f"{row['scatter']:,.0f}" if row["scatter"] else "not run"
        print(f"{n:>9,}{svg:>16}{row['scattergl']:>20,.0f}")

    # %% react-dashboard
    env = dict(os.environ, PYTHONPATH=str(HERE))
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "segments_api:app", "--port", "8123", "--log-level", "warning"], cwd=HERE, env=env)
    try:
        wait_for("http://127.0.0.1:8123/index.html")
        sizes = {}
        page = browser.new_page(viewport={"width": 940, "height": 860})
        page.on("response", lambda r: sizes.__setitem__(r.url.split("8123")[-1], r.headers.get("content-length")))
        react_bytes = record_bytes(page)
        page.goto("http://127.0.0.1:8123/?key=demo-analyst-key", wait_until="networkidle")
        print("React page sent:", {k: v for k, v in sizes.items() if v})
        report_bytes("React page, first load", react_bytes)
        print("table rows:", page.locator("tbody tr").count(), "|", page.locator("tbody tr").first.inner_text().replace("\t", " | "))
        page.screenshot(path=cs.IMAGES / "viz-segments-react-dashboard.png")
        page.select_option("select", "Wales")
        page.wait_for_timeout(500)
        print("Wales:", page.locator("tbody tr").first.inner_text().replace("\t", " | "))
        page.goto("http://127.0.0.1:8123/?key=wrong", wait_until="networkidle")
        print("wrong key:", page.locator("[role=alert]").inner_text())
    finally:
        server.terminate()

    # %% dash-dashboard
    server = subprocess.Popen([sys.executable, "segments_dash.py"], cwd=HERE, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for("http://127.0.0.1:8050/")
        page = browser.new_page(viewport={"width": 940, "height": 860})
        calls = []
        dash_bytes = record_bytes(page)
        page.on("request", lambda r: calls.append(r.url) if "_dash-update" in r.url else None)
        page.goto("http://127.0.0.1:8050/", wait_until="networkidle")
        page.wait_for_selector(".main-svg")
        print("Dash traces:", page.evaluate("document.querySelector('.js-plotly-plot').data.map(t => t.name)"))
        print("Dash callback requests so far:", len(calls))
        report_bytes("Dash page, first load", dash_bytes)
        page.screenshot(path=cs.IMAGES / "viz-segments-dash-dashboard.png")
    finally:
        server.terminate()
    browser.close()
