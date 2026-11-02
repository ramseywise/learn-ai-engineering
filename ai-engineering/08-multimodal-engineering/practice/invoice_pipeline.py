# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "pillow", "reportlab", "pypdf", "pypdfium2", "rapidocr-onnxruntime", "matplotlib"]
# ///
"""A runnable invoice pipeline for notes/02: generated PDFs and scans, two extractors, checks, field F1, cost per document.

Run from this folder (a few minutes on a laptop CPU, downloads no data):
    uv run invoice_pipeline.py

Everything in the documents is generated from a seed. No vision-language model is called: the image route is a real
open OCR engine, and the prices are stated assumptions, printed with the results. Writes docs-invoice-route-cost.png.
"""
# %%
import random
import re
import tempfile
import time
from decimal import Decimal as D
from pathlib import Path

import numpy as np
import pandas as pd
import pypdfium2
from PIL import Image, ImageFilter
from pypdf import PdfReader
from rapidocr_onnxruntime import RapidOCR
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import chartstyle as cs
import matplotlib.pyplot as plt

SEED, N_PER_CELL = 7, 20
KINDS = ["born digital", "scan", "poor scan"]
LAYOUTS = ["label beside value", "label over value", "two columns"]
FIELDS = ["vendor", "number", "issued", "due", "subtotal", "tax", "total", "iban"]
CPU_PER_HOUR, REVIEW_MINUTES, REVIEW_PER_HOUR = 0.10, 3, 30.0     # stated assumptions, in one currency unit
pd.set_option("display.width", 140)


# %% Generate invoices
def money(x, style):
    s = f"{x:,.2f}"
    return s if style == "dot" else s.replace(",", "_").replace(".", ",").replace("_", ".")


def invoice(r):
    stem = "".join(r.choice("bro ka lin mor ven ta sel dru fen hal".split()) for _ in range(2)).capitalize()
    vendor = f"{stem} {r.choice(['Joinery', 'Freight', 'Print', 'Timber'])} {r.choice(['Ltd', 'GmbH', 'BV'])}"
    items = [(r.randint(1, 9), D(r.randint(500, 90000)) / 100) for _ in range(r.randint(2, 6))]
    subtotal = sum(q * u for q, u in items)
    rate = r.choice([D("0.07"), D("0.19"), D("0.21")])
    tax = (subtotal * rate).quantize(D("0.01"))
    day, month = r.randint(1, 28), r.randint(1, 10)
    return dict(vendor=vendor, number=f"{r.randint(100000, 999999)}", issued=f"2026-{month:02d}-{day:02d}",
                due=f"2026-{month + 1:02d}-{day:02d}", vendor_key=squeeze(vendor), items=items, rate=rate, subtotal=subtotal, tax=tax, total=subtotal + tax,
                iban="XX" + "".join(str(r.randint(0, 9)) for _ in range(18)), style=r.choice(["dot", "comma"]))


def draw(doc, layout, path):
    """One page. Each label and value is its own text operation, as a PDF producer would emit them."""
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, h - 60, doc["vendor"])
    c.setFont("Helvetica", 10)
    fmt = lambda v: money(v, doc["style"])
    meta = [("Invoice no", doc["number"]), ("Invoice date", doc["issued"]), ("Due date", doc["due"]), ("IBAN", doc["iban"])]
    sums = [("Subtotal", fmt(doc["subtotal"])), (f"VAT {int(doc['rate'] * 100)}%", fmt(doc["tax"])), ("Total due", fmt(doc["total"]))]
    y0 = h - 110
    if layout == "label beside value":
        for i, (k, v) in enumerate(meta):
            c.drawString(50, y0 - 16 * i, k + ":")
            c.drawString(150, y0 - 16 * i, v)
    elif layout == "label over value":
        xs = [50, 170, 280, 390]
        for x, (k, v) in zip(xs, meta):
            c.drawString(x, y0, k)
        for x, (k, v) in zip(xs, meta):                      # values are drawn in a second pass, so drawing order splits them
            c.drawString(x, y0 - 14, v)
    else:
        for i, (k, v) in enumerate(meta[2:]):                # the right column is drawn first, on purpose
            c.drawString(320, y0 - 16 * i, k + ":")
            c.drawString(390, y0 - 16 * i, v)
        for i, (k, v) in enumerate(meta[:2]):
            c.drawString(50, y0 - 16 * i, k + ":")
            c.drawString(130, y0 - 16 * i, v)
    y = y0 - 90
    c.setFont("Helvetica-Bold", 10)
    for x, t in zip((50, 300, 370, 460), ("Description", "Qty", "Unit", "Amount")):
        c.drawString(x, y, t)
    c.setFont("Helvetica", 10)
    for i, (q, u) in enumerate(doc["items"]):
        y -= 16
        for x, t in zip((50, 300, 370, 460), (f"Item {i + 1}", str(q), fmt(u), fmt(q * u))):
            c.drawString(x, y, t)
    y -= 34
    for k, v in sums:
        c.drawString(370, y, k)
        c.drawString(460, y, v)
        y -= 16
    c.save()


def render(path, dpi):
    return pypdfium2.PdfDocument(str(path))[0].render(scale=dpi / 72).to_pil().convert("L")


QUALITY = {"scan": dict(blur=.5, noise=12), "poor scan": dict(blur=.9, noise=40)}


def scan(path, r, dpi, blur, noise):
    """Rasterise at dpi, then a slight skew, blur and sensor noise, as a document scanner would."""
    im = render(path, dpi)
    im = im.rotate(r.uniform(-.8, .8), fillcolor=255, resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur * dpi / 100))
    arr = np.asarray(im, dtype=float) + np.random.default_rng(r.randint(0, 1 << 30)).normal(0, noise, im.size[::-1])
    return np.clip(arr, 0, 255).astype("uint8")


# %% Two ways into tokens: the text layer and OCR. A token is (text, x, y) with y growing downwards.
def text_layer(path):
    page, out = PdfReader(str(path)).pages[0], []

    def visit(text, cm, tm, *_):
        if text.strip():
            out.append((text.strip(), float(tm[4]), 842 - float(tm[5])))
    page.extract_text(visitor_text=visit)
    return out


ocr = RapidOCR()


def ocr_tokens(image, dpi):
    result, _ = ocr(image)
    return [(t, float(b[0][0]) * 72 / dpi, float(b[0][1]) * 72 / dpi) for b, t, _ in (result or [])]


# %% Two extractors over the same tokens
AMOUNT = r"\d{1,3}(?:[.,]\d{3})*[.,]\d{2}"
PATTERN = {"number": r"\b\d{6}\b", "issued": r"\d{4}-\d{2}-\d{2}", "due": r"\d{4}-\d{2}-\d{2}", "iban": r"XX\d{18}",
           "subtotal": AMOUNT, "tax": AMOUNT, "total": AMOUNT}
KEY = {"number": r"invoice\s*no", "issued": r"invoice\s*date", "due": r"due\s*date", "iban": r"iban",
       "subtotal": r"subtotal", "tax": r"vat", "total": r"total\s*due"}


def text_only(tokens):
    """Forget the positions and read the tokens as one string, the way a prompt with the extracted text would."""
    text = " ".join(t for t, _, _ in tokens)
    out = {"vendor": tokens[0][0] if tokens else None}
    for f, key in KEY.items():
        m = re.search(key + r"[^0-9A-Za-z]*(?:\d+%)?[^0-9A-Za-z]*(" + PATTERN[f] + ")", text, re.I)
        out[f] = m.group(1) if m else None
    return out


def with_layout(tokens):
    """Use the positions: a value lies to the right of its label on the same row, or directly below it."""
    out = {"vendor": min(tokens, key=lambda t: t[2])[0] if tokens else None}
    for f, key in KEY.items():
        out[f] = None
        for t, x, y in tokens:
            if not re.search(key, t, re.I):
                continue
            inline = re.search(PATTERN[f] + "$", t)
            if inline:
                out[f] = inline.group()
                break
            right = [(a - x, s) for s, a, b in tokens if abs(b - y) < 6 and a > x and re.fullmatch(PATTERN[f], s.strip())]
            below = [(b - y, s) for s, a, b in tokens if abs(a - x) < 14 and 4 < b - y < 24 and re.fullmatch(PATTERN[f], s.strip())]
            if right or below:
                out[f] = min(right or below)[1]
                break
    return out


# %% Normalise, check, score
def norm_amount(s):
    if not s:
        return None
    digits = re.sub(r"[.,]", "", s)
    return D(digits) / 100


def squeeze(s):
    return re.sub(r"\s+", "", s).casefold() if s else None


def normalise(pred):
    out = dict(pred)
    out["vendor_raw"], out["vendor"] = pred.get("vendor"), squeeze(pred.get("vendor"))
    for f in ("subtotal", "tax", "total"):
        out[f] = norm_amount(pred.get(f))
    return out


def checks(p):
    """The document's own arithmetic and required fields. Same idea as reconcile() in the chapter."""
    bad = [f for f in FIELDS if not p.get(f)]
    if bad:
        return ["missing " + ",".join(bad)]
    if p["subtotal"] + p["tax"] != p["total"]:
        return ["subtotal + tax != total"]
    if p["due"] < p["issued"]:
        return ["due before issued"]
    return []


def truth(doc, f):
    return doc["vendor_key"] if f == "vendor" else doc[f]


def field_counts(p, doc):
    """Exact match per field after normalising number format, and spaces and case in the name.
    A missing value costs recall, a wrong one costs both."""
    rows = []
    for f in FIELDS:
        gold, got = truth(doc, f), p.get(f)
        rows.append(dict(field=f, tp=int(got == gold), fp=int(got is not None and got != gold), fn=int(got != gold)))
    return rows


def f1(rows):
    d = pd.DataFrame(rows)
    tp, fp, fn = d.tp.sum(), d.fp.sum(), d.fn.sum()
    return 2 * tp / max(2 * tp + fp + fn, 1)


# %% Run
r = random.Random(SEED)
runs, records = [], []
with tempfile.TemporaryDirectory() as tmp:
    docs = []
    for layout in LAYOUTS:
        for kind in KINDS:
            for _ in range(N_PER_CELL):
                doc = invoice(r)
                path = Path(tmp) / f"{len(docs)}.pdf"
                draw(doc, layout, path)
                docs.append((doc, layout, kind, path))
    print(f"{len(docs)} documents: {len(LAYOUTS)} layouts, {len(KINDS)} kinds of page, {N_PER_CELL} of each")

    for doc, layout, kind, path in docs:
        state = random.Random(doc["number"])
        low = np.asarray(render(path, 100)) if kind == "born digital" else scan(path, state, 100, **QUALITY[kind])
        t0 = time.perf_counter()
        ocr_read = ocr_tokens(low, 100)
        ocr_seconds = time.perf_counter() - t0
        if kind == "born digital":
            t0 = time.perf_counter()
            tokens = text_layer(path)
            first_seconds = time.perf_counter() - t0
        else:
            tokens, first_seconds = ocr_read, ocr_seconds
        ex_text, ex_layout = normalise(text_only(tokens)), normalise(with_layout(tokens))
        if checks(ex_layout) and kind != "born digital":                 # the expensive second attempt, only on failure
            high = scan(path, state, 200, **QUALITY[kind])
            t1 = time.perf_counter()
            retry = normalise(with_layout(ocr_tokens(high, 200)))
            retry_seconds = time.perf_counter() - t1
        else:
            retry, retry_seconds = None, 0.0
        records.append(dict(doc=doc, layout=layout, kind=kind, tokens=tokens, text=ex_text, lay=ex_layout, retry=retry,
                            ocr=normalise(with_layout(ocr_read)), ocr_seconds=ocr_seconds,
                            first=first_seconds, second=retry_seconds))

print("\nfield F1 by extractor, first attempt, exact match after normalising number format")
rows = []
for layout in LAYOUTS:
    for kind in KINDS:
        rs = [x for x in records if x["layout"] == layout and x["kind"] == kind]
        rows.append(dict(layout=layout, kind=kind,
                         text_only=f1([c for x in rs for c in field_counts(x["text"], x["doc"])]),
                         with_layout=f1([c for x in rs for c in field_counts(x["lay"], x["doc"])]),
                         fail_check=np.mean([bool(checks(x["lay"])) for x in rs]),
                         seconds=np.mean([x["first"] for x in rs])))
print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.3f}"))

print("\nfield F1 per field, with layout, first attempt")
per = pd.DataFrame([dict(c, kind=x["kind"]) for x in records for c in field_counts(x["lay"], x["doc"])])
print(per.groupby(["field", "kind"]).apply(lambda g: f1(g.to_dict("records"))).unstack().reindex(FIELDS).round(3).to_string())
scans = [x for x in records if x["kind"] != "born digital"]
print(f"vendor read character for character on scans, spaces included: {np.mean([x['lay']['vendor_raw'] == x['doc']['vendor'] for x in scans]):.3f}")

caught = [(bool(checks(x["lay"])), any(x["lay"].get(f) != truth(x["doc"], f) for f in FIELDS)) for x in records]
wrong_docs = sum(w for _, w in caught)
print(f"\ndocuments with at least one wrong field, first attempt: {wrong_docs} of {len(records)}")
print(f"  of those the checks caught {sum(c and w for c, w in caught)}; the checks also failed {sum(c and not w for c, w in caught)} clean documents")
missed = [x for x in records if not checks(x["lay"]) and any(x["lay"].get(f) != truth(x["doc"], f) for f in FIELDS)]
print("  fields wrong on documents that passed:", pd.Series([f for x in missed for f in FIELDS if x["lay"].get(f) != truth(x["doc"], f)]).value_counts().to_dict())


def outcome(policy):
    """What each policy spends and what it ships. Reviewed documents are assumed corrected by the person."""
    rows, sec, reviewed, retried = [], [], 0, 0
    for x in records:
        p, s = x["lay"], x["first"]
        if policy == "text only, no checks":
            p = x["text"]
        elif policy == "OCR every page, layout":
            p, s = x["ocr"], x["ocr_seconds"]
        elif policy == "layout, no checks":
            pass
        else:
            if checks(p) and x["retry"] is not None and "retry" in policy:
                p, s = x["retry"], s + x["second"]
                retried += 1
            if checks(p) and "review" in policy:
                p = {f: truth(x["doc"], f) for f in FIELDS}
                reviewed += 1
        rows.extend(field_counts(p, x["doc"]))
        sec.append(s)
    n = len(records)
    cost_cpu = np.mean(sec) / 3600 * CPU_PER_HOUR
    cost_rev = reviewed / n * REVIEW_MINUTES / 60 * REVIEW_PER_HOUR
    return dict(policy=policy, f1=f1(rows), seconds=np.mean(sec), retried=retried / n, reviewed=reviewed / n,
                cost_cpu=cost_cpu, cost_review=cost_rev, cost_per_doc=cost_cpu + cost_rev)


print(f"\nassumptions: CPU {CPU_PER_HOUR} per hour, review {REVIEW_MINUTES} minutes at {REVIEW_PER_HOUR} per hour")
pol = pd.DataFrame([outcome(p) for p in ["text only, no checks", "OCR every page, layout", "layout, no checks", "layout, retry", "layout, review", "layout, retry, review"]])
print(pol.to_string(index=False, float_format=lambda v: f"{v:.6f}"))

# %% Figure
cs.apply()
fig, ax = plt.subplots()
for _, row in pol.iterrows():
    ax.scatter(row.cost_per_doc, row.f1, s=80, color=cs.ORANGE if row.reviewed else cs.BLUE, zorder=3)
    ax.annotate(row.policy, (row.cost_per_doc, row.f1), xytext=(8, -3), textcoords="offset points", color=cs.SECONDARY)
ax.set_xscale("symlog", linthresh=.01)
ax.set(xlabel="Cost per document on the stated assumptions (symmetric log scale)", ylabel="Field F1")
ax.grid(False, axis="x")
ax.set_title("Review buys the last errors, and it costs far more than compute")
cs.save(fig, "docs-invoice-route-cost.png")
