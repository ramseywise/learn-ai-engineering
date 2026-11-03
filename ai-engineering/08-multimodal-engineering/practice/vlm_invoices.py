"""Generated invoices for the VLM lab: an image and the JSON a reader should return.

Nothing here comes from a real company. Vendors, numbers and amounts are drawn from a seeded generator, so the labels are
correct by construction, and a layout can be held out of training.
"""
import json
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FIELDS = ["vendor", "number", "issued", "total"]
LAYOUTS = ["beside", "over", "columns", "table"]
W, H = 768, 1024
STEMS, TRADES = "bro ka lin mor ven ta sel dru fen hal".split(), ["Joinery", "Freight", "Print", "Timber"]
NEW_STEMS, NEW_TRADES = "qui zo plu wex nor jav".split(), ["Glass", "Marine", "Cable", "Dairy"]  # never in training


def invoice(r, stems=STEMS, trades=TRADES):
    stem = "".join(r.choice(stems) for _ in range(2)).capitalize()
    subtotal = r.randint(5_000, 900_000)
    tax = subtotal * r.choice([7, 19, 21]) // 100
    month, day = r.randint(1, 10), r.randint(1, 28)
    return dict(vendor=f"{stem} {r.choice(trades)} {r.choice(['Ltd', 'GmbH', 'BV'])}",
                number=str(r.randint(100_000, 999_999)), issued=f"2026-{month:02d}-{day:02d}", due=f"2026-{month + 1:02d}-{day:02d}",
                subtotal=f"{subtotal / 100:.2f}", tax=f"{tax / 100:.2f}", total=f"{(subtotal + tax) / 100:.2f}")


def draw(doc, layout, r, big=30, small=24):
    page = Image.new("RGB", (W, H), "white")
    pen, title, body = ImageDraw.Draw(page), ImageFont.load_default(size=big + 6), ImageFont.load_default(size=small)
    lines = [("Invoice no", doc["number"]), ("Issued", doc["issued"]), ("Due", doc["due"]), ("Subtotal", doc["subtotal"]), ("Tax", doc["tax"]), ("Total", doc["total"])]
    x, y = 50 + r.randint(0, 20), 40 + r.randint(0, 20)
    pen.text((x, y), doc["vendor"], fill="black", font=title)
    y += 90
    if layout == "beside":
        for k, v in lines:
            pen.text((x, y), f"{k}: {v}", fill="black", font=body)
            y += 70
    elif layout == "over":
        for k, v in lines:
            pen.text((x, y), k, fill="#555555", font=body)
            pen.text((x, y + 30), v, fill="black", font=body)
            y += 95
    elif layout == "columns":
        for i, (k, v) in enumerate(lines):
            col, row = i % 2, i // 2
            pen.text((x + col * 340, y + row * 130), k, fill="#555555", font=body)
            pen.text((x + col * 340, y + row * 130 + 30), v, fill="black", font=body)
    else:  # a rule-lined table, with the amounts right-aligned: held out of training in the lab
        for k, v in lines:
            pen.line((x, y - 10, W - 50, y - 10), fill="#999999", width=2)
            pen.text((x, y), k, fill="black", font=body)
            pen.text((W - 60, y), v, fill="black", font=body, anchor="ra")
            y += 75
    return page


def degrade(page, r):
    """A scan: a small skew and a little blur."""
    return page.rotate(r.uniform(-1.5, 1.5), fillcolor="white", resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(r.uniform(0, .8)))


def answer(doc):
    return json.dumps({f: doc[f] for f in FIELDS})


def make(n, seed, layouts, stems=STEMS, trades=TRADES, big=30, small=24):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        doc = invoice(r, stems, trades)
        out.append((degrade(draw(doc, r.choice(layouts), r, big, small), r), doc))
    return out
