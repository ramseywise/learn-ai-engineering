# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "pillow", "opencv-python", "rapidocr-onnxruntime", "matplotlib"]
# ///
"""Reading engineering drawings for notes/02: whole-page OCR against crop-first, typed fields, checks, review routing.

Run from this folder (about six minutes on a laptop CPU, downloads no data):
    uv run drawing_extraction_lab.py
    uv run drawing_extraction_lab.py --n 3      # fewer drawings per quality level, for a quick look

Every drawing is GENERATED from a seed: one part family, one layout, one font, symbols we drew ourselves. No vision model
is called. The reader is a real open OCR engine (RapidOCR). The region finder is real image processing that sees only
pixels, but its rule for naming a feature is hand-written for this one layout, and the review prices are assumptions.
So the numbers test this code on these drawings. They say nothing about real drawings, and the last section of the
output lists what they can't show. Writes docs-drawing-sample.png and docs-drawing-field-f1.png.
"""
# %%
import argparse
import math
import random
import re
import time
from dataclasses import dataclass, field, replace
from decimal import Decimal as D
from difflib import SequenceMatcher

import cv2
import numpy as np
import pandas as pd
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from rapidocr_onnxruntime import RapidOCR

import chartstyle as cs
import matplotlib.pyplot as plt

SEED, N_PER_QUALITY = 11, 20
PAGE_MM, SUPERSAMPLE = (297, 210), 2
QUALITY = {"clean": dict(dpi=150, blur=0, noise=0, skew=0),
           "scan": dict(dpi=150, blur=.6, noise=12, skew=.8),
           "poor scan": dict(dpi=100, blur=.7, noise=22, skew=1.5)}
ROUTES = ["page only", "page + regions", "crop-first", "crop, true regions"]
SCALE_LIMIT, INK_RATIO = .04, 1.4        # how far a line may disagree with its value, and how much unread ink is too much
# Stated assumptions, in one currency unit. Change them and the routing table moves.
REVIEW_MINUTES, FRAME_LOOK_MINUTES, REVIEW_PER_HOUR, COST_OF_WRONG_FIELD = 6, 1.5, 40.0, 150.0
pd.set_option("display.width", 170)

FONT = font_manager.findfont("DejaVu Sans")
TEXT_MM, SMALL_MM, LABEL_MM = 3.4, 2.4, 2.2  # em sizes on the page
DIGIT_EM = .636                               # DejaVu digit advance, used only by the ink check
FEATURES = ["len_overall", "seg1", "seg2", "seg3", "height_overall", "height_step", "edge_slant",
            "hole_x", "hole_pitch", "hole_y", "hole_dia"]
TITLE_FIELDS = ["part_no", "material", "scale", "units", "general_tol", "rev"]
LABELS = {"part_no": "PART NO", "title": "TITLE", "material": "MATERIAL", "scale": "SCALE", "units": "UNITS",
          "general_tol": "GENERAL TOL", "rev": "REV", "date": "DATE"}
FCF_DATUMS = {"position": "ABC", "flatness": "", "perpendicularity": "A", "parallelism": "A"}
# What a reader might plausibly print for a symbol. Anything else counts as not read.
SYMBOL_GUESSES = {"position": ["⊕", "⌖", "Φ", "φ", "+"], "flatness": ["▱", "/7", "□"],
                  "perpendicularity": ["⊥", "丄", "1", "T", "L"], "parallelism": ["//", "∥", "||", "ll", "11"]}


# %% Typed fields. A value without its tolerance is a different record, not a slightly worse one.
@dataclass
class Dim:
    nominal: D
    plus: D | None = None
    minus: D | None = None           # stored as a positive size: +0.10/-0.05 is plus 0.10, minus 0.05
    unit: str | None = None
    feature: str | None = None
    count: int | None = None
    partial: bool = False            # the reader found a sign that the parser could not complete


@dataclass
class Layout:
    """Where things are, in pixels of a deskewed image. Knows geometry and nothing about what the text says."""
    image: np.ndarray
    ppm: float
    lines: dict = field(default_factory=dict)        # feature -> (p1, p2)
    shelf: tuple | None = None
    fcf_cells: list = field(default_factory=list)    # rects, left to right
    title_cells: list = field(default_factory=list)
    holes: list = field(default_factory=list)        # measured diameters in page mm


@dataclass
class Extraction:
    dims: list = field(default_factory=list)
    title: dict = field(default_factory=dict)
    fcf: dict = field(default_factory=dict)
    symbol_raw: str = ""


# %% Generate a drawing: truth first, then pixels. Page coordinates are millimetres with y growing downwards.
def fmt(v, unit, tol=False):
    s = f"{v:.3f}" if unit == "in" else f"{v:.2f}"
    return s.lstrip("0") if unit == "in" and tol else s


def pick_tolerance(r, unit, force=False):
    sym = [D("0.005"), D("0.010"), D("0.002")] if unit == "in" else [D("0.05"), D("0.10"), D("0.20")]
    stack = [(D("0.005"), D("0.002")), (D("0.010"), D("0.005"))] if unit == "in" else [(D("0.10"), D("0.05")), (D("0.20"), D("0.10")), (D("0.05"), D("0.02"))]
    kind = r.choice(["sym", "stack"]) if force else r.choices(["none", "sym", "stack"], [.4, .35, .25])[0]
    if kind == "none":
        return None, None
    if kind == "sym":
        t = r.choice(sym)
        return t, t
    return r.choice(stack)


def make_drawing(r):
    unit = r.choice(["mm", "mm", "in"])
    page_per_unit, scale = r.choice([(1, "1:1"), (.5, "1:2"), (2, "2:1")] if unit == "mm" else [(25.4, "1:1"), (12.7, "1:2")])
    step = D("0.125") if unit == "in" else D("0.5")
    snap = lambda page_mm: (D(str(page_mm / page_per_unit)) / step).quantize(D(1)) * step
    a, b, c = snap(r.uniform(34, 50)), snap(r.uniform(60, 85)), snap(r.uniform(30, 42))
    L, H = a + b + c, snap(r.uniform(62, 85))
    low, drop = snap(float(H) * page_per_unit * r.uniform(.5, .72)), snap(r.uniform(20, 32))
    slant = D(str(math.hypot(c, drop))).quantize(D("0.001") if unit == "in" else D("0.01"))
    hole1 = a + snap(r.uniform(12, 16))
    pitch = snap(r.uniform(26, 32))
    room = float(a + b - hole1) * page_per_unit - 8
    n_holes = min(r.choice([2, 3]), 1 + int(room // (float(pitch) * page_per_unit)))
    hole_y = snap(r.uniform(28, .6 * float(H) * page_per_unit))
    dia = snap(r.uniform(6, 12))
    ox, oy = 45.0, 140.0                                     # where the part's bottom-left corner sits on the page

    def at(x, y):
        return ox + float(x) * page_per_unit, oy - float(y) * page_per_unit

    x0, x1, y0, y1 = at(0, 0)[0], at(L, 0)[0], at(0, 0)[1], at(0, H)[1]
    cut_start, cut_end = at(L - c, H), at(L, H - drop)
    length = math.hypot(cut_end[0] - cut_start[0], cut_end[1] - cut_start[1])
    nx, ny = (cut_end[1] - cut_start[1]) / length, -(cut_end[0] - cut_start[0]) / length   # outward, up and to the right
    spots = {"len_overall": (L, (x0, y0 + 24), (x1, y0 + 24)),
             "seg1": (a, (x0, y0 + 12), (at(a, 0)[0], y0 + 12)),
             "seg2": (b, (at(a, 0)[0], y0 + 12), (at(a + b, 0)[0], y0 + 12)),
             "seg3": (c, (at(a + b, 0)[0], y0 + 12), (x1, y0 + 12)),
             "height_overall": (H, (x1 + 28, y0), (x1 + 28, y1)),
             "height_step": (low, (x0 - 14, y0), (x0 - 14, at(0, low)[1])),
             "edge_slant": (slant, (cut_start[0] + 10 * nx, cut_start[1] + 10 * ny), (cut_end[0] + 10 * nx, cut_end[1] + 10 * ny)),
             "hole_x": (hole1, (x0, y1 - 12), (at(hole1, 0)[0], y1 - 12)),
             "hole_pitch": (pitch, (at(hole1, 0)[0], y1 - 12), (at(hole1 + pitch, 0)[0], y1 - 12)),
             "hole_y": (hole_y, (x1 + 14, y0), (x1 + 14, at(0, hole_y)[1]))}
    dims, lines = [], {}
    for name, (value, p1, p2) in spots.items():
        plus, minus = pick_tolerance(r, unit)
        dims.append(Dim(value, plus, minus, unit, name))
        lines[name] = (p1, p2)
    plus, minus = pick_tolerance(r, unit, force=True)        # a hole callout always states its tolerance
    dims.append(Dim(dia, plus, minus, unit, "hole_dia", n_holes))
    symbol = r.choice(list(FCF_DATUMS))
    fcf_tol = r.choice([D("0.002"), D("0.005")] if unit == "in" else [D("0.05"), D("0.10"), D("0.20")])
    drw = dict(unit=unit, scale=scale, page_per_unit=page_per_unit, dims=dims, lines=lines, step=step, title_layout=r.choice(["over", "beside"]),
               outline=[at(0, 0), at(L, 0), at(L, H - drop), at(L - c, H), at(a, H), at(a, low), at(0, low)],
               centres=[at(hole1 + i * pitch, hole_y) for i in range(n_holes)], radius=float(dia) * page_per_unit / 2,
               part_no=f"DRG-{r.randint(10000, 99999)}-{r.choice('ABCDEF')}", name=r.choice(["BRACKET PLATE", "MOUNT PLATE", "GUSSET", "END CAP"]),
               material=r.choice(["AL 6061-T6", "S355J2", "AISI 304", "C45E", "Ti-6Al-4V"]),
               general_tol=D("0.010") if unit == "in" else r.choice([D("0.2"), D("0.3")]), rev=r.choice("ABCDEF"),
               date=f"2026-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}", fcf_symbol=symbol, fcf_tol=fcf_tol, fcf_datums=FCF_DATUMS[symbol],
               fcf_dia=symbol == "position")
    return drw


class Pen:
    """Draws in page millimetres at a supersampled resolution."""

    def __init__(self, dpi):
        self.k = dpi * SUPERSAMPLE / 25.4
        self.im = Image.new("L", (round(PAGE_MM[0] * self.k), round(PAGE_MM[1] * self.k)), 255)
        self.d = ImageDraw.Draw(self.im)

    def line(self, p, q, w=.25):
        self.d.line([p[0] * self.k, p[1] * self.k, q[0] * self.k, q[1] * self.k], fill=0, width=max(1, round(w * self.k)))

    def rect(self, x, y, w, h, stroke=.35):
        self.d.rectangle([x * self.k, y * self.k, (x + w) * self.k, (y + h) * self.k], outline=0, width=max(1, round(stroke * self.k)))

    def font(self, mm):
        return ImageFont.truetype(FONT, round(mm * self.k))

    def text(self, x, y, s, mm=TEXT_MM):
        self.d.text((x * self.k, y * self.k), s, font=self.font(mm), fill=0)

    def width(self, s, mm=TEXT_MM):
        return self.d.textlength(s, font=self.font(mm)) / self.k

    def arrow(self, tip, toward):
        n = math.hypot(toward[0] - tip[0], toward[1] - tip[1])
        ux, uy = (toward[0] - tip[0]) / n, (toward[1] - tip[1]) / n
        base = (tip[0] + 3 * ux, tip[1] + 3 * uy)
        pts = [tip, (base[0] - .55 * uy, base[1] + .55 * ux), (base[0] + .55 * uy, base[1] - .55 * ux)]
        self.d.polygon([(a * self.k, b * self.k) for a, b in pts], fill=0)

    def label(self, d, prefix="", suffix=""):
        """A dimension's text on its own transparent strip, so that it can be rotated with the line."""
        k, unit = self.k, d.unit
        main = prefix + fmt(d.nominal, unit)
        sym = d.plus is not None and d.plus == d.minus
        if sym:
            main += " ±" + fmt(d.plus, unit, tol=True)
        main_w = self.width(main)
        stacked = d.plus is not None and not sym
        tol_w = max(self.width("+" + fmt(d.plus, unit, tol=True), SMALL_MM), self.width("-" + fmt(d.minus, unit, tol=True), SMALL_MM)) + .7 if stacked else 0
        suffix_w = self.width(" " + suffix) if suffix else 0
        w, h = main_w + tol_w + suffix_w + 1, 7.0
        strip = Image.new("L", (round(w * k), round(h * k)), 255)
        s = ImageDraw.Draw(strip)
        s.text((.2 * k, 1.8 * k), main, font=self.font(TEXT_MM), fill=0)
        if stacked:
            s.text(((main_w + .7) * k, .2 * k), "+" + fmt(d.plus, unit, tol=True), font=self.font(SMALL_MM), fill=0)
            s.text(((main_w + .7) * k, 3.2 * k), "-" + fmt(d.minus, unit, tol=True), font=self.font(SMALL_MM), fill=0)
        if suffix:
            s.text(((main_w + tol_w + .2) * k, 1.8 * k), " " + suffix, font=self.font(TEXT_MM), fill=0)
        return strip, w, h

    def paste_rotated(self, strip, centre, degrees):
        rot = strip.rotate(degrees, expand=True, fillcolor=255, resample=Image.BICUBIC)
        at = (round(centre[0] * self.k - rot.width / 2), round(centre[1] * self.k - rot.height / 2))
        self.im.paste(Image.composite(rot, self.im.crop((at[0], at[1], at[0] + rot.width, at[1] + rot.height)), rot.point(lambda v: 255 if v < 200 else 0)), at)


def symbol_marks(pen, kind, x, y, s=8):
    """The characteristic symbol, drawn as strokes. It is a shape on the page: no font and no character code."""
    cx, cy, w = x + s / 2, y + s / 2, .35
    if kind == "position":
        pen.d.ellipse([(cx - 1.7) * pen.k, (cy - 1.7) * pen.k, (cx + 1.7) * pen.k, (cy + 1.7) * pen.k], outline=0, width=round(w * pen.k))
        pen.line((cx - 2.6, cy), (cx + 2.6, cy), w)
        pen.line((cx, cy - 2.6), (cx, cy + 2.6), w)
    elif kind == "flatness":
        pts = [(cx - 2.6, cy + 1.4), (cx + 1.3, cy + 1.4), (cx + 2.6, cy - 1.4), (cx - 1.3, cy - 1.4), (cx - 2.6, cy + 1.4)]
        for p, q in zip(pts, pts[1:]):
            pen.line(p, q, w)
    elif kind == "perpendicularity":
        pen.line((cx - 2.6, cy + 2.2), (cx + 2.6, cy + 2.2), w)
        pen.line((cx, cy + 2.2), (cx, cy - 2.4), w)
    else:
        for off in (-1.2, 1.2):
            pen.line((cx - 1.3 + off, cy + 2.2), (cx + 1.3 + off, cy - 2.2), w)


def title_block():
    """Cells as (field, x, y, w, h). The block sits in the corner of the frame."""
    x, y, rows = 187, 168, [(("part_no", 50), ("title", 50)), (("material", 40), ("scale", 30), ("units", 30)), (("general_tol", 40), ("rev", 30), ("date", 30))]
    cells = []
    for i, row in enumerate(rows):
        cx = x
        for name, w in row:
            cells.append((name, cx, y + i * 32 / 3, w, 32 / 3))
            cx += w
    return cells


def render(drw, dpi):
    """Draw the page, and report the ground-truth regions in page millimetres beside it."""
    pen = Pen(dpi)
    pen.rect(10, 10, 277, 190, .5)
    pts = drw["outline"] + drw["outline"][:1]
    for p, q in zip(pts, pts[1:]):
        pen.line(p, q, .7)
    r0 = drw["radius"]
    for cx, cy in drw["centres"]:
        pen.d.ellipse([(cx - r0) * pen.k, (cy - r0) * pen.k, (cx + r0) * pen.k, (cy + r0) * pen.k], outline=0, width=round(.5 * pen.k))
        pen.line((cx - 1.2, cy), (cx + 1.2, cy), .18)
        pen.line((cx, cy - 1.2), (cx, cy + 1.2), .18)
    x_min, y_max = drw["outline"][0]
    y_top = min(p[1] for p in drw["outline"])
    x_max = max(p[0] for p in drw["outline"])
    by = {d.feature: d for d in drw["dims"]}
    ext = lambda p, q: pen.line(p, q, .18)
    for name, (p1, p2) in drw["lines"].items():
        pen.line(p1, p2)
        pen.arrow(p1, p2)
        pen.arrow(p2, p1)
        strip, _, h = pen.label(by[name])
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        if dx < 0 or (abs(dx) < 1e-6 and dy > 0):
            dx, dy = -dx, -dy
        n = math.hypot(dx, dy)
        dx, dy = dx / n, dy / n
        up = (dy, -dx)
        mid = ((p1[0] + p2[0]) / 2 + up[0] * (.6 + h / 2), (p1[1] + p2[1]) / 2 + up[1] * (.6 + h / 2))
        pen.paste_rotated(strip, mid, math.degrees(math.atan2(-dy, dx)))
    for name in ("len_overall", "seg1", "seg2", "seg3"):
        p1, p2 = drw["lines"][name]
        ext((p1[0], y_max + 1), (p1[0], p1[1] + 1.5))
        ext((p2[0], y_max + 1), (p2[0], p2[1] + 1.5))
    for name in ("hole_x", "hole_pitch"):
        p1, p2 = drw["lines"][name]
        ext((p2[0], p2[1] - 1.5), (p2[0], next(c[1] for c in drw["centres"] if abs(c[0] - p2[0]) < .01) - r0 - 1))
    p1 = drw["lines"]["hole_x"][0]
    ext((p1[0], p1[1] - 1.5), (p1[0], drw["outline"][-1][1] - 1))
    p1, p2 = drw["lines"]["height_overall"]
    ext((x_max + 1, y_max), (p1[0] + 1.5, y_max))
    ext((drw["outline"][3][0] + 1, y_top), (p2[0] + 1.5, y_top))
    p1, p2 = drw["lines"]["height_step"]
    ext((x_min - 1, y_max), (p1[0] - 1.5, y_max))
    ext((x_min - 1, p2[1]), (p2[0] - 1.5, p2[1]))
    p1, p2 = drw["lines"]["hole_y"]
    ext((x_max + 1, y_max), (p1[0] + 1.5, y_max))
    last = drw["centres"][-1]
    ext((last[0] + r0 + 1, last[1]), (p2[0] + 1.5, last[1]))
    # Hole callout on a shelf, with the frame under it
    hole = by["hole_dia"]
    strip, w, h = pen.label(hole, f"{hole.count}X Ø", "THRU")
    sx, sy = drw["centres"][0][0] + 8, 26.0
    pen.im.paste(strip, (round(sx * pen.k), round((sy - h - .3) * pen.k)))
    pen.line((sx, sy), (sx + w + 1, sy))
    edge = (drw["centres"][0][0] + r0 * .71, drw["centres"][0][1] - r0 * .71)
    pen.line((sx, sy), edge)
    pen.arrow(edge, (sx, sy))
    fx, fy = sx + 3, sy + 2.0
    tol_text = ("Ø" if drw["fcf_dia"] else "") + fmt(drw["fcf_tol"], drw["unit"], tol=True)
    widths = [8, max(16, pen.width(tol_text) + 3)] + [8] * len(drw["fcf_datums"])
    fcf_cells, cx = [], fx
    for w_cell in widths:
        pen.rect(cx, fy, w_cell, 8)
        fcf_cells.append((cx, fy, w_cell, 8))
        cx += w_cell
    symbol_marks(pen, drw["fcf_symbol"], fx, fy)
    pen.text(fx + 8 + 1.5, fy + 2, tol_text)
    for i, letter in enumerate(drw["fcf_datums"]):
        pen.text(fx + 8 + widths[1] + 8 * i + 2.8, fy + 2, letter)
    # Title block
    values = dict(part_no=drw["part_no"], title=drw["name"], material=drw["material"], scale=drw["scale"], units="INCH" if drw["unit"] == "in" else "MM",
                  general_tol="±" + (fmt(drw["general_tol"], "in", tol=True) if drw["unit"] == "in" else str(drw["general_tol"])), rev=drw["rev"], date=drw["date"])
    title_cells = []
    for name, x, y, w, h in title_block():
        pen.rect(x, y, w, h)
        title_cells.append((x, y, w, h))
        if drw["title_layout"] == "over":
            pen.text(x + 1.2, y + .7, LABELS[name], LABEL_MM)
            pen.text(x + 1.2, y + 4.3, values[name], TEXT_MM)
        else:
            pen.text(x + 1.2, y + 3.8, LABELS[name], LABEL_MM)
            pen.text(x + 1.8 + pen.width(LABELS[name], LABEL_MM), y + 3.1, values[name], TEXT_MM)
    small = pen.im.resize((round(PAGE_MM[0] * dpi / 25.4), round(PAGE_MM[1] * dpi / 25.4)), Image.LANCZOS)
    return small, dict(lines=drw["lines"], shelf=((sx, sy), (sx + w + 1, sy)), fcf_cells=fcf_cells, title_cells=title_cells)


def degrade(im, r, dpi, blur, noise, skew):
    """A scanner: a slight skew, blur and sensor noise. Returns the image and the true skew."""
    angle = r.uniform(-skew, skew) if skew else 0.0
    if angle:
        im = im.rotate(angle, fillcolor=255, resample=Image.BICUBIC)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(im, dtype=float)
    if noise:
        arr = arr + np.random.default_rng(r.randint(0, 1 << 30)).normal(0, noise, arr.shape)
    return np.clip(arr, 0, 255).astype("uint8"), angle


# %% Finding regions from pixels, with no access to the generator
def rotate_image(image, degrees):
    h, w = image.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), degrees, 1)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=255)


def binarise(image):
    return (cv2.GaussianBlur(image, (3, 3), 0) < 205).astype("uint8")


def estimate_skew(image, ppm):
    """The drawing frame and long edges are nearly axis-aligned, so their median tilt is the page's."""
    segs = cv2.HoughLinesP(binarise(image) * 255, 1, np.pi / 1800, threshold=int(60 * ppm), minLineLength=int(90 * ppm), maxLineGap=int(1 * ppm))
    if segs is None:
        return 0.0
    tilts = []
    for x1, y1, x2, y2 in segs.reshape(-1, 4):
        a = math.degrees(math.atan2(y2 - y1, x2 - x1))
        if abs(a) < 5:
            tilts.append(a)
        elif abs(abs(a) - 90) < 5:
            tilts.append(a - math.copysign(90, a))
    return -float(np.median(tilts)) if tilts else 0.0


def width_profile(b, p, q, band_px):
    """How much ink sits across a line at each point along it, so that arrowheads show up as bumps."""
    n = int(math.hypot(q[0] - p[0], q[1] - p[1]))
    if n < 2:
        return np.zeros(1)
    ux, uy = (q[0] - p[0]) / n, (q[1] - p[1]) / n
    ts, ss = np.arange(n + 1)[:, None], np.arange(-band_px, band_px + 1)[None, :]
    xs = np.clip(np.rint(p[0] + ts * ux - ss * uy).astype(int), 0, b.shape[1] - 1)
    ys = np.clip(np.rint(p[1] + ts * uy + ss * ux).astype(int), 0, b.shape[0] - 1)
    return b[ys, xs].sum(axis=1)


def dimension_segments(b, ppm):
    """Thin straight lines, split where arrowheads are. Returns dimension lines, and arrowless thin lines for the shelf."""
    segs = cv2.HoughLinesP(b * 255, 1, np.pi / 720, threshold=int(9 * ppm), minLineLength=int(14 * ppm), maxLineGap=int(1.2 * ppm))
    if segs is None:
        return [], []
    groups = []                                              # one entry per straight line, however many pieces Hough found
    for x1, y1, x2, y2 in segs.reshape(-1, 4).astype(float):
        angle = math.atan2(y2 - y1, x2 - x1) % math.pi
        if angle > math.pi - math.radians(3) or angle < math.radians(3):
            angle = 0.0
        elif abs(angle - math.pi / 2) < math.radians(3):
            angle = math.pi / 2
        rho = (x1 + x2) / 2 * math.sin(angle) - (y1 + y2) / 2 * math.cos(angle)
        for g in groups:
            if min(abs(g["angle"] - angle), math.pi - abs(g["angle"] - angle)) < math.radians(2.5) and abs(g["rho"] - rho) < 1.2 * ppm:
                g["pts"] += [(x1, y1), (x2, y2)]
                g["rhos"].append(rho)
                break
        else:
            groups.append(dict(angle=angle, rho=rho, rhos=[rho], pts=[(x1, y1), (x2, y2)]))
    band, dims, plain, thin = max(2, round(.9 * ppm)), [], [], max(.75 * ppm, 3.5)
    for g in groups:
        c, s = math.cos(g["angle"]), math.sin(g["angle"])
        ts, rho = [x * c + y * s for x, y in g["pts"]], float(np.median(g["rhos"]))
        if max(ts) - min(ts) > 200 * ppm:                    # the drawing frame
            continue
        p, q = (min(ts) * c + rho * s, min(ts) * s - rho * c), (max(ts) * c + rho * s, max(ts) * s - rho * c)
        w = width_profile(b, p, q, band)
        n = max(len(w) - 1, 1)
        point = lambda t: (p[0] + (q[0] - p[0]) * t / n, p[1] + (q[1] - p[1]) * t / n)
        base = np.median(w)
        bump = (cv2.blur(w.astype("float32").reshape(-1, 1), (1, 3)).ravel() >= max(base + 1.5, .55 * ppm)).astype(int)
        edges = np.flatnonzero(np.diff(np.r_[0, bump, 0]))
        heads = [[a, b_] for a, b_ in zip(edges[::2], edges[1::2])     # an arrowhead along the line, not one lying across it
                 if 1.0 * ppm <= b_ - a <= 7 * ppm and np.median(w[a:b_]) <= 1.7 * ppm]
        joined = []                                          # two arrowheads tip to tip, where a chain of dimensions meets
        for head in heads:
            if joined and head[0] - joined[-1][1] < 5 * ppm:
                joined[-1][1] = head[1]
            else:
                joined.append(head)
        ends_are_arrows = len(joined) >= 2 and joined[0][0] < 3 * ppm and n - joined[-1][1] < 3 * ppm
        if not ends_are_arrows:
            if base <= thin:
                plain.append((p, q))
            continue
        # An interior stop must be two arrowheads. Mark it at the extension line that crosses there, the widest point.
        inner = [(a, b_) for a, b_ in joined[1:-1] if b_ - a >= 3.5 * ppm]
        stops = [0] + [a + int(np.argmax(w[a:b_] - .02 * np.abs(np.arange(a, b_) - (a + b_) / 2))) for a, b_ in inner] + [n]
        for t1, t2 in zip(stops, stops[1:]):
            if t2 - t1 >= 14 * ppm and np.median(w[int(t1):int(t2)]) <= thin:   # the outline is too heavy to be a dimension
                dims.append((point(t1), point(t2)))
    return dims, plain


def name_features(segments, ppm):
    """Which line is which. This rule knows this one layout: a real drawing has no such rule, and this is a stated limit of the lab."""
    def kind(p, q):
        a = math.degrees(math.atan2(abs(q[1] - p[1]), abs(q[0] - p[0])))
        return "h" if a < 3 else "v" if a > 87 else "s"
    hs = [(p, q) if p[0] < q[0] else (q, p) for p, q in segments if kind(p, q) == "h"]
    vs = [(p, q) if p[1] > q[1] else (q, p) for p, q in segments if kind(p, q) == "v"]
    out = {}
    slant = [(p, q) for p, q in segments if kind(p, q) == "s"]
    if slant:
        out["edge_slant"] = max(slant, key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
    if not hs or not vs:
        return out
    length = lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1])
    overall = max(hs, key=length)
    out["len_overall"] = overall
    bottom = overall[0][1] - 24 * ppm
    chain = sorted([s for s in hs if s is not overall and s[0][1] > bottom], key=lambda s: s[0][0])
    top = sorted([s for s in hs if s[0][1] < bottom - 40 * ppm], key=lambda s: s[0][0])
    out.update(zip(["seg1", "seg2", "seg3"], chain))
    out.update(zip(["hole_x", "hole_pitch"], top))
    right = sorted([s for s in vs if s[0][0] > overall[1][0]], key=lambda s: s[0][0])
    left = [s for s in vs if s[0][0] < overall[0][0]]
    if right:
        out["height_overall"] = right[-1]
        out.update(zip(["hole_y"], right[:-1]))
    if left:
        out["height_step"] = left[0]
    return out


def find_regions(image, ppm):
    deskew = estimate_skew(image, ppm)
    fixed = rotate_image(image, -deskew) if abs(deskew) > .02 else image
    b = binarise(fixed)
    segments, plain = dimension_segments(b, ppm)
    layout = Layout(fixed, ppm, lines=name_features(segments, ppm))
    closed = cv2.morphologyEx(b, cv2.MORPH_CLOSE, np.ones((2, 2), "uint8"))
    contours, tree = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    h_img, w_img = b.shape
    fcf, title = [], []
    for c, node in zip(contours, tree[0] if tree is not None else []):
        if node[3] == -1:                                    # keep the insides of closed shapes
            continue
        x, y, w, h = cv2.boundingRect(c)
        wm, hm, area = w / ppm, h / ppm, cv2.contourArea(c)
        if area > .75 * w * h and 4.5 <= hm < 9.5 and 3.5 <= wm <= 40 and y < .4 * h_img:
            fcf.append((x, y, w, h))
        elif area > .75 * w * h and 8.5 <= hm <= 13 and 15 <= wm <= 60 and x > .55 * w_img and y > .7 * h_img:
            title.append((x, y, w, h))
        else:
            _, radius = cv2.minEnclosingCircle(c)
            if area > .8 * math.pi * radius ** 2 and 2.5 <= radius / ppm <= 8:
                layout.holes.append(2 * math.sqrt(area / math.pi) / ppm + .5)   # inner edge to stroke centre
    # A frame is a row of touching cells of one height. Take the longest such row.
    rows = [[c for c in fcf if abs(c[1] - seed[1]) < 1.5 * ppm and abs(c[3] - seed[3]) < 1.5 * ppm] for seed in fcf]
    layout.fcf_cells = sorted(max(rows, key=len), key=lambda c: c[0]) if rows else []
    layout.title_cells = title
    top_of_frame = min((c[1] for c in layout.fcf_cells), default=None)
    shelves = [(p, q) for p, q in plain if abs(p[1] - q[1]) < .6 * ppm and 15 * ppm < abs(q[0] - p[0]) < 85 * ppm and 12 * ppm < p[1] < 40 * ppm]
    if top_of_frame is not None:                             # the frame's top edge is also a thin line: the shelf is the one above it
        above = [s for s in shelves if s[0][1] < top_of_frame - .4 * ppm]
        shelves = above or shelves
    if shelves:
        shelf = min(shelves, key=lambda s: s[0][1])
        layout.shelf = shelf if shelf[0][0] < shelf[1][0] else shelf[::-1]
    return layout


def true_regions(image, angle, regions, drw, ppm):
    """The same Layout, built from the generator. This is the generous case: a perfect detector."""
    fixed = rotate_image(image, -angle) if angle else image
    px = lambda p: (p[0] * ppm, p[1] * ppm)
    box = lambda r: tuple(int(round(v * ppm)) for v in r)
    return Layout(fixed, ppm, lines={k: (px(a), px(b)) for k, (a, b) in regions["lines"].items()}, shelf=tuple(px(p) for p in regions["shelf"]),
                  fcf_cells=[box(c) for c in regions["fcf_cells"]], title_cells=[box(c) for c in regions["title_cells"]],
                  holes=[drw["radius"] * 2] * len(drw["centres"]))


# %% Reading: a token is (text, along, up, height), in millimetres in the frame of the region it came from
ocr = RapidOCR()
BAND_FLOOR = .75                                             # millimetres above the line where the text band starts
ZOOM = 10                                                    # crop pixels per page millimetre, whatever the scan resolution was


def frame(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    if dx < 0 or (abs(dx) < 1e-6 and dy > 0) or (abs(dx) < .05 * abs(dy) and dy > 0):
        dx, dy = -dx, -dy
    n = math.hypot(dx, dy) or 1.0
    d = (dx / n, dy / n)
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), d, (d[1], -d[0])


def zone_size(p1, p2, ppm):
    return min(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / ppm / 2 + 1, 26.0), 8.8      # half width along the line, top of the band above it


def aligned_crop(image, p1, p2, ppm):
    """Cut out the band above a line, leaving out the line and its arrowheads, and turn it level. This is the rotation normalisation."""
    mid, d, up = frame(p1, p2)
    half, height = zone_size(p1, p2, ppm)
    W, Hh, scale = int(2 * half * ZOOM), int((height - BAND_FLOOR) * ZOOM), ppm / ZOOM
    M = np.array([[d[0] * scale, -up[0] * scale, mid[0] - half * ZOOM * d[0] * scale + height * ZOOM * up[0] * scale],
                  [d[1] * scale, -up[1] * scale, mid[1] - half * ZOOM * d[1] * scale + height * ZOOM * up[1] * scale]])
    return cv2.warpAffine(image, M, (W, Hh), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderValue=255), half, height


def read_crop(crop, half=0.0, height=0.0):
    padded = cv2.copyMakeBorder(crop, 12, 12, 12, 12, cv2.BORDER_CONSTANT, value=255)
    result, _ = ocr(padded)
    tokens = []
    for box, text, _ in result or []:
        xs, ys = [p[0] - 12 for p in box], [p[1] - 12 for p in box]
        tokens.append((text, np.mean(xs) / ZOOM - half, height - np.mean(ys) / ZOOM, (max(ys) - min(ys)) / ZOOM))
    return tokens


def read_line(crop):
    """Recognition alone, for a cell too small for the text detector to see."""
    padded = cv2.copyMakeBorder(crop, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=255)
    result, _ = ocr(padded, use_det=False, use_cls=False)
    return " ".join(r[0] for r in (result or []))


def cell_crop(image, rect, ppm):
    x, y, w, h = rect
    m = max(1, round(.5 * ppm))
    cut = image[y + m:y + h - m, x + m:x + w - m]
    return cv2.resize(cut, None, fx=ZOOM / ppm, fy=ZOOM / ppm, interpolation=cv2.INTER_CUBIC) if cut.size else None


def page_tokens(image, ppm):
    """Whole-page OCR. Returns each token's text, centre in page pixels, and height."""
    result, _ = ocr(image)
    out = []
    for box, text, _ in result or []:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        out.append((text, float(np.mean(xs)), float(np.mean(ys)), (max(ys) - min(ys)) / ppm))
    return out


def tokens_in_zone(tokens, p1, p2, ppm):
    mid, d, up = frame(p1, p2)
    half, height = zone_size(p1, p2, ppm)
    out = []
    for text, x, y, h in tokens:
        along = ((x - mid[0]) * d[0] + (y - mid[1]) * d[1]) / ppm
        rise = ((x - mid[0]) * up[0] + (y - mid[1]) * up[1]) / ppm
        if abs(along) <= half and 0 <= rise <= height:
            out.append((text, along, rise, h))
    return out


# %% Parsing: from characters to a typed record
NUM = r"\d*\.\d+|\d+"


def clean(text):
    for a, b in [("土", "±"), ("十", "+"), ("—", "-"), ("–", "-"), ("−", "-"), ("~", "-"), ("，", "."), (",", ".")]:
        text = text.replace(a, b)
    return text


def parse_dim(tokens, unit=None, feature=None):
    """Join the tokens in reading order, then read count, nominal and tolerance. Returns None without a nominal."""
    text = clean(" ".join(t[0] for t in sorted(tokens, key=lambda t: t[1])))
    count = re.search(r"(\d+)\s*[Xx×]", text)
    rest = text[count.end():] if count else text
    nominal = re.search(r"(?<![+\-±.\d])[ØøΦφO⌀]?\s*(\d*\.\d+)", rest)
    if not nominal:
        return None
    after = rest[:nominal.start()] + " " + rest[nominal.end():]
    d = Dim(D(nominal.group(1)), unit=unit, feature=feature, count=int(count.group(1)) if count else None)
    sym = re.search(r"±\s*(" + NUM + ")", after)
    plus, minus = re.search(r"\+\s*(" + NUM + ")", after), re.search(r"-\s*(" + NUM + ")", after)
    if sym:
        d.plus = d.minus = D(sym.group(1))
    elif plus and minus:
        d.plus, d.minus = D(plus.group(1)), D(minus.group(1))
    elif plus or minus:
        d.partial = True                                     # half a tolerance is not a tolerance: don't guess the other half
    return d


def parse_title_cell(name, text, out):
    t = text.strip()
    if name == "part_no":
        m = re.search(r"[A-Z]{2,4}-?\d{5}-?[A-Z0-9]", t.replace(" ", ""))
        out[name] = m.group() if m else (t or None)
    elif name == "material":
        out[name] = t or None
    elif name == "scale":
        m = re.search(r"\d+\s*:\s*\d+", t)
        out[name] = m.group().replace(" ", "") if m else None
    elif name == "units":
        m = re.search(r"\b(MM|INCH)\b", t.upper())
        out[name] = {"MM": "mm", "INCH": "in"}[m.group(1)] if m else None
    elif name == "general_tol":
        m = re.search(NUM, clean(t))
        out[name] = D(m.group()) if m else None
    elif name == "rev":
        m = re.fullmatch(r"\s*([A-Z])\s*", t)
        out[name] = m.group(1) if m else None


def best_label(text):
    """Which title cell a read belongs to, by its printed label. Returns the field and what is left of the text."""
    upper, best, score = text.upper(), None, 0.0
    for name, label in LABELS.items():
        window = upper[:len(label) + 2]
        s = SequenceMatcher(None, window, label).find_longest_match().size / len(label)
        if s > score:
            best, score = name, s
    if score < .6:
        return None, text
    m = SequenceMatcher(None, upper, LABELS[best]).find_longest_match()
    return best, (text[:m.a] + " " + text[m.a + m.size + len(LABELS[best]) - m.size:]).strip(" :")


def parse_title(reads):
    out = {}
    for text in reads:
        name, rest = best_label(text)
        if name in TITLE_FIELDS:
            parse_title_cell(name, rest, out)
    return out


def parse_fcf(cells):
    """cells is the raw read per cell, left to right: symbol, tolerance, then datum letters."""
    out = dict(symbol=None, tolerance=None, datums=None)
    if not cells:
        return out
    symbol_text = cells[0].strip()
    for kind, guesses in SYMBOL_GUESSES.items():
        if symbol_text in guesses:
            out["symbol"] = kind
    if len(cells) > 1:
        m = re.search(r"\d*\.\d+", clean(cells[1]))
        out["tolerance"] = D(m.group()) if m else None
        if m and len(m.group()) > 1 and cells[1].strip().startswith(("0", "O")) and re.match(r"[0O]0\.\d+", cells[1].strip()):
            out["tolerance"] = D(m.group()[1:])              # a diameter sign read as a zero
    out["datums"] = "".join(c.strip() for c in cells[2:]) if all(re.fullmatch(r"\s*[A-Z]\s*", c) for c in cells[2:]) else None
    return out


# %% The four routes. Same parser everywhere. They differ in where the regions and the characters come from.
def whole_page(tokens):
    """The naive route: read each token alone, with no geometry. It can't stitch a stacked tolerance and can't name a line."""
    ordered = sorted(tokens, key=lambda t: (round(t[2] / 20), t[1]))
    flat = " ".join(t[0] for t in ordered)
    title = {}
    for name in TITLE_FIELDS:
        m = re.search(re.escape(LABELS[name]).replace(r"\ ", r"\s*") + r"\s*:?\s*(\S+(?:\s\S+)?)", flat, re.I)
        if m:
            parse_title_cell(name, m.group(1), title)
    dims, tols, letters = [], [], []
    for t in ordered:
        text = t[0].strip()
        if re.fullmatch(r"[A-Z]", text):
            letters.append(text)
        if text.startswith(("+", "-", "±")) or not re.search(r"\d\.\d|\.\d", text):
            continue
        d = parse_dim([(text, 0, 0, 0)], unit=title.get("units"))
        if not d:
            continue
        if d.nominal < 1 and d.plus is None:                 # too small for a dimension here: take it for the frame's tolerance
            tols.append(d.nominal)
            continue
        if d.count or text[:1] in "Ø⌀":
            d.feature = "hole_dia"
        dims.append(d)
    return Extraction(dims, title, dict(symbol=None, tolerance=tols[0] if tols else None, datums="".join(letters[:3]) or None), "")


def read_regions(layout, tokens=None):
    """Read every region the layout names. tokens=None crops and OCRs each region; otherwise it takes page OCR tokens that fall inside."""
    units_title, title_reads = {}, []
    for rect in layout.title_cells:
        if tokens is None:
            crop = cell_crop(layout.image, rect, layout.ppm)
            title_reads.append(" ".join(t[0] for t in read_crop(crop)) if crop is not None else "")
        else:
            x, y, w, h = rect
            inside = sorted([t for t in tokens if x <= t[1] <= x + w and y <= t[2] <= y + h], key=lambda t: (round(t[2] / (2 * layout.ppm)), t[1]))
            title_reads.append(" ".join(t[0] for t in inside))
    units_title = parse_title(title_reads)
    unit = units_title.get("units")
    dims = []
    zones = list(layout.lines.items()) + ([("hole_dia", layout.shelf)] if layout.shelf else [])
    for name, (p1, p2) in zones:
        if tokens is None:
            crop, half, height = aligned_crop(layout.image, p1, p2, layout.ppm)
            found = read_crop(crop, half, height)
        else:
            found = tokens_in_zone(tokens, p1, p2, layout.ppm)
        d = parse_dim(found, unit=unit, feature=name)
        if d:
            dims.append(d)
    cells = []
    for rect in layout.fcf_cells:
        if tokens is None:
            crop = cell_crop(layout.image, rect, layout.ppm)
            cells.append(read_line(crop) if crop is not None else "")
        else:
            x, y, w, h = rect
            cells.append(" ".join(t[0] for t in tokens if x <= t[1] <= x + w and y <= t[2] <= y + h))
    return Extraction(dims, units_title, parse_fcf(cells), cells[0].strip() if cells else "")


# %% Checks that don't trust the reader. Each compares a read against arithmetic or against the line it labels.
def ink_width(layout, p1, p2):
    """How long the text above a line is, measured in pixels, read by nobody."""
    crop, half, height = aligned_crop(layout.image, p1, p2, layout.ppm)
    ink = cv2.GaussianBlur(crop, (5, 5), 0) < 150
    cols = ink.sum(axis=0)
    cols[cols > .6 * ink.shape[0]] = 0                       # an extension line crossing the band is not text
    xs = np.flatnonzero(cols >= 2)
    if not len(xs):
        return 0.0
    clusters = np.split(xs, np.flatnonzero(np.diff(xs) > 2.2 * ZOOM) + 1)
    return (max(c[-1] - c[0] for c in clusters)) / ZOOM


def expected_width(d):
    """Width of the characters that were read, in this font. On a real drawing, calibrate this from the digits themselves."""
    chars = lambda v: (len(str(v)) - .5) * DIGIT_EM
    text = 5.5 * DIGIT_EM * TEXT_MM if d.nominal < 100 else 6.5 * DIGIT_EM * TEXT_MM
    if d.plus is None:
        return text
    if d.plus == d.minus:
        return text + (chars(d.plus) + 2 * DIGIT_EM) * TEXT_MM
    return text + max(chars(d.plus), chars(d.minus)) * SMALL_MM + 2


def measure(layout):
    """What the pixels say, once per drawing, before anyone reads anything."""
    return dict(line_mm={k: math.hypot(q[0] - p[0], q[1] - p[1]) / layout.ppm for k, (p, q) in layout.lines.items()},
                ink={k: ink_width(layout, p, q) for k, (p, q) in layout.lines.items()},
                holes=list(layout.holes), n_lines=len(layout.lines), has_shelf=layout.shelf is not None,
                n_frame=len(layout.fcf_cells))


def checks(x, m):
    """Names of the checks this extraction fails. Empty means it goes through without a person."""
    fails, by = [], {d.feature: d for d in x.dims if d.feature}
    needed = [f for f in FEATURES if f != "hole_dia"]
    if len(by) < len(FEATURES) or any(f not in by for f in needed) or not m["has_shelf"]:
        fails.append("complete")
    if not all(x.title.get(f) is not None for f in TITLE_FIELDS):
        fails.append("title complete")
    if any(k in by for k in ("seg1", "seg2", "seg3", "len_overall")):
        if all(k in by for k in ("seg1", "seg2", "seg3", "len_overall")):
            if by["seg1"].nominal + by["seg2"].nominal + by["seg3"].nominal != by["len_overall"].nominal:
                fails.append("chain sum")
    ratios = {f: float(by[f].nominal) / m["line_mm"][f] for f in by if f in m["line_mm"] and m["line_mm"][f] > 0}
    if len(ratios) >= 3:
        mid = float(np.median(list(ratios.values())))
        if any(abs(v / mid - 1) > SCALE_LIMIT for v in ratios.values()):
            fails.append("line agrees with value")
        stated = x.title.get("scale")
        unit = x.title.get("units")
        if stated and unit:
            a, b = stated.split(":")
            expected = (float(b) / float(a)) / (25.4 if unit == "in" else 1)
            if abs(mid / expected - 1) > SCALE_LIMIT:
                fails.append("title scale and units")
    hole = by.get("hole_dia")
    if hole is not None and m["holes"]:
        if hole.count != len(m["holes"]):
            fails.append("hole count")
        if ratios:
            page_mm = float(hole.nominal) / float(np.median(list(ratios.values())))
            if abs(page_mm / float(np.median(m["holes"])) - 1) > .1:
                fails.append("hole size")
    if any(d.partial for d in x.dims):
        fails.append("half a tolerance")
    for d in x.dims:
        if d.plus is not None and (d.plus > d.nominal * D("0.05") or d.minus > d.nominal * D("0.05")):
            fails.append("tolerance size")
            break
    for f, d in by.items():
        if f in m["ink"] and m["ink"][f] > INK_RATIO * expected_width(d):
            fails.append("unread ink")
            break
    if m["n_frame"] and (x.fcf.get("tolerance") is None or x.fcf.get("datums") is None):
        fails.append("frame incomplete")
    return fails


# %% Score: per field. A dropped tolerance is a miss. It doesn't earn partial credit for being a short string.
def align(preds, truth):
    """Pair each true dimension with the prediction of the same nominal, preferring the same feature. Each prediction is used once."""
    free, pairs = list(preds), {}
    for want_feature in (True, False):
        for t in truth:
            if t.feature in pairs:
                continue
            for p in free:
                if p.nominal == t.nominal and (not want_feature or p.feature == t.feature):
                    pairs[t.feature] = p
                    free.remove(p)
                    break
    return pairs, free


def tol_key(d):
    return d.plus, d.minus


def score(x, drw):
    rows = []
    add = lambda name, ok, predicted: rows.append(dict(field=name, tp=int(ok), fp=int(predicted and not ok), fn=int(not ok)))
    pairs, spare = align(x.dims, drw["dims"])
    for t in drw["dims"]:
        p = pairs.get(t.feature)
        add("value", p is not None, p is not None)
        if t.plus is not None:
            add("tolerance", p is not None and tol_key(p) == tol_key(t), p is not None and p.plus is not None)
        elif p is not None and p.plus is not None:
            rows.append(dict(field="tolerance", tp=0, fp=1, fn=0))
        add("unit", p is not None and p.unit == t.unit, p is not None and p.unit is not None)
        add("feature", p is not None and p.feature == t.feature, p is not None and p.feature is not None)
        whole = p is not None and tol_key(p) == tol_key(t) and p.unit == t.unit and p.feature == t.feature and (t.count is None or p.count == t.count)
        add("whole dimension", whole, p is not None)
        if t.count is not None:
            add("hole count", p is not None and p.count == t.count, p is not None and p.count is not None)
    for _ in spare:
        rows.append(dict(field="value", tp=0, fp=1, fn=0))
    gold = dict(part_no=drw["part_no"], material=drw["material"], scale=drw["scale"], units=drw["unit"], general_tol=drw["general_tol"], rev=drw["rev"])
    for name, want in gold.items():
        got = x.title.get(name)
        same = got == want if name not in ("part_no", "material") else (got or "").replace(" ", "").casefold() == str(want).replace(" ", "").casefold()
        add("title " + name, same, got is not None)
    add("frame tolerance", x.fcf.get("tolerance") == drw["fcf_tol"], x.fcf.get("tolerance") is not None)
    add("frame datums", (x.fcf.get("datums") or "") == drw["fcf_datums"] and x.fcf.get("datums") is not None, x.fcf.get("datums") is not None)
    add("frame symbol", x.fcf.get("symbol") == drw["fcf_symbol"], x.fcf.get("symbol") is not None)
    return rows


def f1(rows):
    tp, fp, fn = sum(c["tp"] for c in rows), sum(c["fp"] for c in rows), sum(c["fn"] for c in rows)
    return 2 * tp / max(2 * tp + fp + fn, 1)


FIELD_ORDER = ["value", "tolerance", "unit", "feature", "whole dimension", "hole count", "title part_no", "title material", "title scale",
               "title units", "title general_tol", "title rev", "frame tolerance", "frame datums", "frame symbol"]


def wrong_fields(x, drw):
    return [c["field"] for c in score(x, drw) if c["fn"] and c["field"] != "whole dimension"]


# %% A perfect read of the truth, for testing the checks with no OCR in the way
def perfect_read(drw):
    return Extraction([replace(d) for d in drw["dims"]], dict(part_no=drw["part_no"], material=drw["material"], scale=drw["scale"], units=drw["unit"],
                                                                general_tol=drw["general_tol"], rev=drw["rev"]),
                      dict(symbol=drw["fcf_symbol"], tolerance=drw["fcf_tol"], datums=drw["fcf_datums"]), "")


def alter_digit(v, position):
    """Change one digit of a value, as a misread would, keeping its format."""
    s, seen = str(v), 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            if seen == position:
                return D(s[:i] + str((int(ch) + 3) % 10 or 1) + s[i + 1:])
            seen += 1
    return v


def corrupt(x, kind, drw):
    """One known misread, on a copy."""
    y = Extraction([replace(d) for d in x.dims], dict(x.title), dict(x.fcf), "")
    by = {d.feature: d for d in y.dims}
    explicit = [d for d in y.dims if d.plus is not None]
    if kind == "first digit of a segment":
        by["seg2"].nominal = alter_digit(by["seg2"].nominal, 0)
    elif kind == "last digit of a segment":
        by["seg2"].nominal = by["seg2"].nominal + drw["step"]
    elif kind == "first digit of hole position":
        by["hole_y"].nominal = alter_digit(by["hole_y"].nominal, 0)
    elif kind == "last digit of hole position":
        by["hole_y"].nominal = by["hole_y"].nominal + drw["step"]
    elif kind == "decimal point moved":
        by["height_overall"].nominal = by["height_overall"].nominal / 10
    elif kind == "tolerance dropped":
        explicit[0].plus = explicit[0].minus = None
    elif kind == "tolerance digit wrong":
        explicit[0].plus = explicit[0].plus + (D("0.001") if drw["unit"] == "in" else D("0.01"))
    elif kind == "tolerance ten times too big":
        explicit[0].plus = explicit[0].minus = explicit[0].plus * 100
    elif kind == "hole count wrong":
        by["hole_dia"].count += 1
    elif kind == "hole size first digit":
        by["hole_dia"].nominal = alter_digit(by["hole_dia"].nominal, 0)
    elif kind == "title units flipped":
        y.title["units"] = "mm" if y.title["units"] == "in" else "in"
    elif kind == "title scale wrong":
        y.title["scale"] = "1:5"
    elif kind == "material wrong":
        y.title["material"] = "AISI 303"
    elif kind == "part number digit wrong":
        y.title["part_no"] = y.title["part_no"].replace("-1", "-7", 1) if "-1" in y.title["part_no"] else "DRG-11111-A"
    elif kind == "frame tolerance wrong":
        y.fcf["tolerance"] = y.fcf["tolerance"] * 2
    return y


CORRUPTIONS = ["first digit of a segment", "last digit of a segment", "first digit of hole position", "last digit of hole position", "decimal point moved",
               "tolerance dropped", "tolerance digit wrong", "tolerance ten times too big", "hole count wrong", "hole size first digit",
               "title units flipped", "title scale wrong", "material wrong", "part number digit wrong", "frame tolerance wrong"]


# %% Self-checks on the small pieces
def test_pieces():
    d = parse_dim([("3X 08.50", 0, 0, 0), ("±0.10", 5, 0, 0)])
    assert (d.count, d.nominal, d.plus, d.minus) == (3, D("8.50"), D("0.10"), D("0.10"))
    d = parse_dim([("25.00", 0, 0, 0), ("-0.05", 9, 0, 0), ("+0.10", 9, 3, 0)])
    assert (d.nominal, d.plus, d.minus) == (D("25.00"), D("0.10"), D("0.05"))
    assert parse_dim([("25.00", 0, 0, 0), ("+0.10", 9, 3, 0)]).partial, "half a tolerance must be flagged, not completed"
    assert parse_dim([("THRU", 0, 0, 0)]) is None
    r = random.Random(1)
    for _ in range(20):
        drw = make_drawing(r)
        by = {d.feature: d for d in drw["dims"]}
        assert by["seg1"].nominal + by["seg2"].nominal + by["seg3"].nominal == by["len_overall"].nominal
        assert by["hole_dia"].plus is not None
        got = wrong_fields(perfect_read(drw), drw)
        assert got == ["frame datums"] * (not drw["fcf_datums"]) or not got or got == [], got
    drw = make_drawing(random.Random(2))
    explicit = next(d for d in drw["dims"] if d.plus is not None)
    x = perfect_read(drw)
    next(d for d in x.dims if d.feature == explicit.feature).plus = None
    rows = [c for c in score(x, drw) if c["field"] == "tolerance"]
    assert sum(c["fn"] for c in rows) == 1, "a dropped tolerance must count as a miss"


# %% Run
def main(n):
    test_pieces()
    r = random.Random(SEED)
    records, sample = [], {}
    t_start = time.perf_counter()
    for quality, q in QUALITY.items():
        for i in range(n):
            drw = make_drawing(r)
            pixels, regions = render(drw, q["dpi"])
            image, angle = degrade(pixels, r, q["dpi"], q["blur"], q["noise"], q["skew"])
            ppm = q["dpi"] / 25.4
            if i == 0:
                sample[quality] = image
            t0 = time.perf_counter()
            tokens = page_tokens(image, ppm)
            page_seconds = time.perf_counter() - t0
            t0 = time.perf_counter()
            found = find_regions(image, ppm)
            crop = read_regions(found)
            crop_seconds = time.perf_counter() - t0
            deskew = rotate_tokens(tokens, image.shape, found, image)
            truth_layout = true_regions(image, angle, regions, drw, ppm)
            records.append(dict(
                quality=quality, drw=drw, page_seconds=page_seconds, crop_seconds=crop_seconds,
                reads={"page only": whole_page(tokens), "page + regions": read_regions(found, deskew),
                       "crop-first": crop, "crop, true regions": read_regions(truth_layout)},
                m=measure(found), m_true=measure(truth_layout), n_found=len(found.lines), n_title=len(found.title_cells), n_cells=len(found.fcf_cells),
                has_shelf=found.shelf is not None))
    report(records, sample, n, time.perf_counter() - t_start)


def rotate_tokens(tokens, shape, layout, image):
    """Page tokens came from the skewed image. Carry their centres into the deskewed frame the regions live in."""
    if layout.image is image:
        return tokens
    deskew = estimate_skew(image, layout.ppm)
    h, w = shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -deskew, 1)
    return [(t, *(M @ np.array([x, y, 1.0])), hh) for t, x, y, hh in tokens]


def show_table(records, route):
    rows = []
    for quality in QUALITY:
        got = [c for x in records if x["quality"] == quality for c in score(x["reads"][route], x["drw"])]
        rows.append({"quality": quality, **{f: f1([c for c in got if c["field"] == f]) for f in FIELD_ORDER}})
    return pd.DataFrame(rows).set_index("quality").T


def report(records, sample, n, seconds):
    print(f"{len(records)} GENERATED drawings: {len(QUALITY)} quality levels, {n} of each, one layout, one font. Reader: RapidOCR. No vision model.\n")
    print("Region finding from pixels alone, share of the true regions found")
    rows = []
    for quality in QUALITY:
        xs = [x for x in records if x["quality"] == quality]
        rows.append(dict(quality=quality, dimension_lines=np.mean([x["n_found"] / 10 for x in xs]), shelf=np.mean([x["has_shelf"] for x in xs]),
                         title_cells=np.mean([x["n_title"] / 8 for x in xs]),
                         frame_found=np.mean([x["n_cells"] == 2 + len(x["drw"]["fcf_datums"]) for x in xs])))
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    print("\nField F1, the four routes side by side (exact match after normalising number format)")
    tables = {route: show_table(records, route) for route in ROUTES}
    combined = pd.concat(tables, axis=1)
    print(combined.to_string(float_format=lambda v: f"{v:.3f}"))
    print("'page only' has no geometry, so its low feature score is by construction, not a finding. 'page + regions' is the fair comparison for reading.")

    print("\nWhat a value-only score hides, crop-first")
    rows = []
    for quality in QUALITY:
        xs = [x for x in records if x["quality"] == quality]
        value_right = tol_right = dropped = wrong_tol = explicit = 0
        for x in xs:
            pairs, _ = align(x["reads"]["crop-first"].dims, x["drw"]["dims"])
            for t in x["drw"]["dims"]:
                if t.plus is None:
                    continue
                explicit += 1
                p = pairs.get(t.feature)
                if p is not None:
                    value_right += 1
                    if tol_key(p) == tol_key(t):
                        tol_right += 1
                    elif p.plus is None:
                        dropped += 1
                    else:
                        wrong_tol += 1
        rows.append(dict(quality=quality, dims_with_tolerance=explicit, value_right=value_right / explicit, value_and_tolerance_right=tol_right / explicit,
                         tolerance_dropped=dropped, tolerance_wrong=wrong_tol))
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    print("\nThe frame's symbol: what the OCR printed for that cell, by symbol, across all drawings (crop-first, recognition alone)")
    counts = {}
    for x in records:
        counts.setdefault(x["drw"]["fcf_symbol"], []).append(x["reads"]["crop-first"].symbol_raw or "(nothing)")
    for kind, seen in counts.items():
        top = pd.Series(seen).value_counts().head(6).to_dict()
        print(f"  {kind:17s} {len(seen):3d} frames  printed: {top}")
    frame_rows = [c for x in records for c in score(x["reads"]["crop, true regions"], x["drw"]) if c["field"] == "frame symbol"]
    symbol_f1 = f1(frame_rows)
    print(f"frame symbol F1, given a perfect crop of the cell: {symbol_f1:.3f}")

    print(f"\nChecks on the crop-first read, by quality. 'wrong' means at least one field is wrong or missing, symbol excluded")
    rows, fired, passed_wrong = [], {}, {}
    for quality in QUALITY:
        xs = [x for x in records if x["quality"] == quality]
        tp = fa = wrong = 0
        for x in xs:
            y = x["reads"]["crop-first"]
            fails = checks(y, x["m"])
            bad = [f for f in wrong_fields(y, x["drw"]) if f != "frame symbol"]
            wrong += bool(bad)
            tp += bool(bad) and bool(fails)
            fa += bool(fails) and not bad
            for f in fails:
                fired[f] = fired.get(f, 0) + 1
            if bad and not fails:
                for f in bad:
                    passed_wrong[f] = passed_wrong.get(f, 0) + 1
        rows.append(dict(quality=quality, drawings=len(xs), wrong=wrong, caught=tp, missed=wrong - tp, clean_but_flagged=fa))
    print(pd.DataFrame(rows).to_string(index=False))
    print("how often each check fired:", dict(sorted(fired.items(), key=lambda kv: -kv[1])))
    print("wrong fields on drawings that passed:", dict(sorted(passed_wrong.items(), key=lambda kv: -kv[1])) or "none")

    print("\nThe checks against one known misread at a time: perfect read, true geometry, no OCR involved, every drawing")
    rows, base_fail = [], 0
    for x in records:
        base_fail += bool(checks(perfect_read(x["drw"]), x["m_true"]))
    for kind in CORRUPTIONS:
        caught, by = 0, {}
        for x in records:
            fails = checks(corrupt(perfect_read(x["drw"]), kind, x["drw"]), x["m_true"])
            caught += bool(fails)
            for f in fails:
                by[f] = by.get(f, 0) + 1
        rows.append(dict(misread=kind, caught=caught / len(records), by=max(by, key=by.get) if by else "nothing"))
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print(f"perfect reads the checks flag anyway (false alarms with no misread at all): {base_fail} of {len(records)}")
    assert base_fail <= .34 * len(records), "the checks should mostly pass a perfect read"

    print(f"\nRouting. Assumptions: full review {REVIEW_MINUTES} min, a look at one frame {FRAME_LOOK_MINUTES} min, {REVIEW_PER_HOUR} per hour, "
          f"{COST_OF_WRONG_FIELD} per wrong field shipped, and a reviewer who fixes everything they see (optimistic)")
    minute = REVIEW_PER_HOUR / 60

    def policy(name, route, review):
        shipped, spent, reviewed, frames = 0, 0.0, 0, 0
        for x in records:
            y, wrong = x["reads"][route], wrong_fields(x["reads"][route], x["drw"])
            mode = review(y, x["m"])
            if mode == "full":
                spent += REVIEW_MINUTES * minute
                reviewed += 1
            else:
                if mode == "frame":
                    spent += FRAME_LOOK_MINUTES * minute
                    frames += 1
                    wrong = [f for f in wrong if f != "frame symbol"]
                shipped += len(wrong)
        count = len(records)
        return dict(policy=name, full_review=reviewed / count, frame_look=frames / count, wrong_fields_shipped=shipped / count, review_cost=spent / count,
                    error_cost=shipped / count * COST_OF_WRONG_FIELD, total=spent / count + shipped / count * COST_OF_WRONG_FIELD)

    pol = pd.DataFrame([
        policy("page only, ship it", "page only", lambda y, m: "ship"),
        policy("crop-first, ship it", "crop-first", lambda y, m: "ship"),
        policy("crop-first, review if a check fails", "crop-first", lambda y, m: "full" if checks(y, m) else "ship"),
        policy("same, plus a person reads every frame", "crop-first", lambda y, m: "full" if checks(y, m) else "frame"),
        policy("a person reviews every drawing", "crop-first", lambda y, m: "full")])
    print(pol.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    no_review = pol.total[1]
    print(f"crop-first shipped without review spends more on errors than a full review (at {REVIEW_MINUTES} min) as soon as a wrong field costs more than "
          f"{REVIEW_MINUTES * minute / max(pol.wrong_fields_shipped[1], 1e-9):.2f}")

    print("\nWhat this cannot show")
    print("- These drawings are generated. One part family, one layout, one font, no hatching, no section views, no handwriting, no stamps, no real scanner.")
    print("- name_features() is a rule written for this layout. Feature scores here are close to the best case, and a new layout would break them.")
    print(f"- The frame symbol F1 above is {symbol_f1:.3f}, on symbols we drew ourselves, with a perfect crop. We did not train or template-match a recogniser, because")
    print("  matching our own strokes would score well and tell you nothing. Assume a text OCR can't read these symbols, and test a real recogniser on real frames.")
    print("- A generated part always closes: the chain always sums and the lines are to scale. Real drawings can be marked 'not to scale', and then the line check is void.")
    print("- No published figure is reproduced here, and these numbers can't be compared with the papers in the note.")
    print(f"\nRan in {seconds:.0f} seconds. Time per drawing, mean: whole-page OCR {np.mean([x['page_seconds'] for x in records]):.2f}s, crop-first {np.mean([x['crop_seconds'] for x in records]):.2f}s")

    # %% Figures
    cs.apply()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
    for ax, name in zip(axes, ["clean", "poor scan"]):
        ax.imshow(sample[name], cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Generated drawing, {name}")
        ax.axis("off")
    cs.save(fig, "docs-drawing-sample.png")

    show = ["page only", "page + regions", "crop-first", "crop, true regions"]
    fig, axes = plt.subplots(1, len(QUALITY), sharey=True, figsize=(10, 5.2))
    cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list("seq", cs.SEQUENTIAL)
    for ax, quality in zip(axes, QUALITY):
        grid = np.array([[tables[route].loc[f, quality] for route in show] for f in FIELD_ORDER])
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(show)), [s.replace(" + ", "\n+ ").replace(", ", ",\n").replace("-first", "-\nfirst") for s in show], fontsize=8)
        ax.set_yticks(range(len(FIELD_ORDER)), FIELD_ORDER)
        ax.grid(False)
        ax.set_title(quality)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white" if grid[i, j] > .55 else cs.INK)
    cs.save(fig, "docs-drawing-field-f1.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=N_PER_QUALITY, help="drawings per quality level")
    main(parser.parse_args().n)
