#!/usr/bin/env python3
"""Find and extract figures from a source PDF, for notes and slides.

Run with PyMuPDF:  uv run -q --with pymupdf python scripts/papers/figures.py <cmd> ...

  captions <pdf>                         every "Figure N-M." caption, with its page
  list     <pdf> [--pages 3-9]           raster images per page: xref, size, nearest caption
  page     <pdf> --page P --out x.png    render a whole page (to look at it before cropping)
  extract  <pdf> --page P --xref X --out sources/images/<author>-<title>-fig<N>.png
                                         save one embedded raster image as-is
  crop     <pdf> --page P --clip x0,y0,x1,y1 --out ...png [--dpi 200]
                                         render a page region (vector diagrams, or a figure
                                         with its labels); coordinates in PDF points, 72/in

Pages are 1-based. `list` and `page` print the page size so `crop` coordinates can be chosen
from the rendered page. After saving, embed it in the note with the caption line `extract`
and `crop` print.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    sys.exit("needs PyMuPDF: uv run -q --with pymupdf python scripts/papers/figures.py ...")

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


def main():
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
    args = ap.parse_args()
    with fitz.open(args.pdf) as doc:
        args.fn(doc, args)


if __name__ == "__main__":
    main()
