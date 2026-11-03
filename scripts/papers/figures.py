#!/usr/bin/env python3
"""Find and extract figures from a source PDF, for notes and slides, and report figure yield per home.

Run with PyMuPDF:  uv run -q --with pymupdf python scripts/papers/figures.py <cmd> ...

  captions <pdf>                         every "Figure N-M." caption, with its page
  list     <pdf> [--pages 3-9]           raster images per page: xref, size, nearest caption
  page     <pdf> --page P --out x.png    render a whole page (to look at it before cropping)
  extract  <pdf> --page P --xref X --out sources/images/<author>-<title>-fig<N>.png
                                         save one embedded raster image as-is
  crop     <pdf> --page P --clip x0,y0,x1,y1 --out ...png [--dpi 200]
                                         render a page region (vector diagrams, or a figure
                                         with its labels); coordinates in PDF points, 72/in
  yield    [--home data-science]         per home: integrated readings, images kept, images embedded
                                         in notes, embedded per 100 readings (no PyMuPDF needed)

Pages are 1-based. `list` and `page` print the page size so `crop` coordinates can be chosen
from the rendered page. After saving, embed it in the note with the caption line `extract`
and `crop` print.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import potw  # noqa: E402

fitz = None  # PyMuPDF, loaded by main() for the commands that open a PDF
LOW_YIELD_PER_100 = 5  # flagged in `yield` once a home has this few embedded per 100 readings
LOW_YIELD_MIN_READINGS = 20  # below this, a low rate says little
IMAGE_EMBED = re.compile(r"!\[[^\]]*\]\(<?[^)]*sources/images/[^)]+\)")
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

caption_re = re.compile(r"^\s*(Fig(?:ure)?\.?\s*(\d+(?:[-.]\d+)?))[.:]\s*(.+)", re.I)


def page_range(spec, n):
    if not spec:
        return range(n)
    a, _, b = spec.partition("-")
    return range(int(a) - 1, min(int(b or a), n))


def captions_on(page):
    out = []
    for block in page.get_text("blocks"):
        text = " ".join(block[4].split())
        m = caption_re.match(text)
        if m:
            out.append((m.group(2), m.group(3)[:160], block[1]))
    return out


def cmd_captions(doc, args):
    for i, page in enumerate(doc):
        for num, text, _ in captions_on(page):
            print(f"p{i + 1:<4} Figure {num}: {text}")


def cmd_list(doc, args):
    for i in page_range(args.pages, len(doc)):
        page = doc[i]
        caps = captions_on(page)
        imgs = page.get_images(full=True)
        if not imgs and not caps:
            continue
        r = page.rect
        print(f"p{i + 1}  ({r.width:.0f}x{r.height:.0f} pt)")
        for img in imgs:
            xref, w, h = img[0], img[2], img[3]
            rects = page.get_image_rects(xref)
            where = f" at {tuple(round(v) for v in rects[0])}" if rects else ""
            near = ""
            if rects and caps:  # caption closest below the image
                below = [c for c in caps if c[2] >= rects[0].y1 - 5] or caps
                near = f"  ~ Figure {min(below, key=lambda c: abs(c[2] - rects[0].y1))[0]}"
            print(f"   xref {xref:<5} {w}x{h}px{where}{near}")
        for num, text, y in caps:
            print(f"   caption y={y:.0f}  Figure {num}: {text}")


def cmd_page(doc, args):
    page = doc[args.page - 1]
    page.get_pixmap(dpi=args.dpi).save(args.out)
    print(f"wrote {args.out}  (page {args.page}, {page.rect.width:.0f}x{page.rect.height:.0f} pt)")


def caption_hint(out):
    print(f"\n![<alt text>](../sources/images/{Path(out).name})")
    print("*Image Source: <Author>, [<Title>](<public url>) (<year>), Fig. <N> (<licence, if any>)*")


def cmd_extract(doc, args):
    pix = fitz.Pixmap(doc, args.xref)
    if pix.n - pix.alpha >= 4:  # CMYK -> RGB
        pix = fitz.Pixmap(fitz.csRGB, pix)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pix.save(args.out)
    print(f"wrote {args.out}  ({pix.width}x{pix.height}px)")
    caption_hint(args.out)


def cmd_crop(doc, args):
    page = doc[args.page - 1]
    clip = fitz.Rect(*[float(v) for v in args.clip.split(",")])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(dpi=args.dpi, clip=clip)
    pix.save(args.out)
    print(f"wrote {args.out}  ({pix.width}x{pix.height}px)")
    caption_hint(args.out)


def figure_yield(rows, home=None):
    """One dict per course folder. Homes sharing a folder (data-systems, ml-systems) share a line."""
    folders = {}
    for key, folder in potw.PILLARS.items():
        folders.setdefault(folder, []).append(key)
    out = []
    for folder, keys in sorted(folders.items()):
        if home and home not in keys:
            continue
        readings = sum(r.get("status") == "integrated" and r.get("pillar") in keys and bool(r.get("local_pdf"))
                       for r in rows)
        base = potw.REPO / folder
        kept = sum(p.suffix.lower() in IMAGE_TYPES and p.parent.name == "images" and p.parent.parent.name == "sources"
                   for p in base.rglob("*") if not set(p.relative_to(base).parts) & potw.PDF_SKIP_DIRS) if base.is_dir() else 0
        embedded = sum(len(IMAGE_EMBED.findall(p.read_text(encoding="utf-8", errors="replace")))
                       for p in potw.home_notes(folder)) if base.is_dir() else 0
        per_100 = 100 * embedded / readings if readings else 0
        out.append({"folder": folder, "readings": readings, "kept": kept, "embedded": embedded, "per_100": per_100,
                    "low": readings >= LOW_YIELD_MIN_READINGS and per_100 < LOW_YIELD_PER_100})
    return out


def cmd_yield(args):
    print(f"{'home':<42} {'readings':>8} {'kept':>6} {'embedded':>8} {'per 100':>8}")
    for y in figure_yield(potw.read_jsonl(potw.LEDGER), args.home):
        print(f"{y['folder']:<42} {y['readings']:>8} {y['kept']:>6} {y['embedded']:>8} {y['per_100']:>8.1f}"
              + ("  LOW" if y["low"] else ""))


def main():
    global fitz
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("captions", cmd_captions), ("list", cmd_list), ("page", cmd_page),
                     ("extract", cmd_extract), ("crop", cmd_crop)):
        p = sub.add_parser(name)
        p.add_argument("pdf")
        p.set_defaults(fn=fn)
        if name == "list":
            p.add_argument("--pages", help="e.g. 3-9 (1-based)")
        if name in ("page", "extract", "crop"):
            p.add_argument("--page", type=int, required=True)
            p.add_argument("--out", required=True)
        if name in ("page", "crop"):
            p.add_argument("--dpi", type=int, default=150 if name == "page" else 200)
        if name == "extract":
            p.add_argument("--xref", type=int, required=True)
        if name == "crop":
            p.add_argument("--clip", required=True, help="x0,y0,x1,y1 in PDF points")
    p = sub.add_parser("yield", help="per home: readings, images kept and embedded")
    p.add_argument("--home", help="one home key from potw.py")
    p.set_defaults(fn=cmd_yield)
    args = ap.parse_args()
    if args.cmd == "yield":
        args.fn(args)
        return
    try:
        import pymupdf as fitz
    except ImportError:
        sys.exit("needs PyMuPDF: uv run -q --with pymupdf python scripts/papers/figures.py ...")
    with fitz.open(args.pdf) as doc:
        args.fn(doc, args)


if __name__ == "__main__":
    main()
