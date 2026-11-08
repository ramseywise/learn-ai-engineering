#!/usr/bin/env python3
"""Structured extractions: one JSON file per reading, written by the source-reader agent.

Every PDF the pipeline reads leaves `scripts/papers/extractions/<key>.json` behind: the research
question, hypothesis, method in numbers (data, models, training recipe, inference and eval settings),
results with their setup, limits, and lineage (what it extends, replicates, contradicts or uses as a
baseline). The ledger is not touched: a reading's extraction status is the file and its `schema`.

  schema 1   a full extraction in the format of extraction-template.json
  schema 0   salvaged: an older source-reader text report recovered from session transcripts. It has
             claims, limits and builds-on, but no method block, so it still needs a read.

  uv run -q --with pymupdf --with pypdf python scripts/papers/extract.py text <key|pdf>   # cache text, print section map
  uv run -q --with pymupdf --with pypdf python scripts/papers/extract.py check <key> [--strict]
  python3 scripts/papers/extract.py check --all --schema-only        # what make test runs
  python3 scripts/papers/extract.py status [--home rag]
  python3 scripts/papers/extract.py next [--home rag] [--n 10] [--include-v0]   # backlog, best first
  python3 scripts/papers/extract.py path <key>                       # where a key's extraction goes
  python3 scripts/papers/extract.py salvage [--dry-run]              # recover old reports from transcripts
  python3 scripts/papers/extract.py report                           # reports/lineage.md, reports/reproducible.md
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import potw

READINGS = Path(__file__).resolve().parent
EXTRACTIONS = READINGS / "extractions"
TEMPLATE = READINGS / "extraction-template.json"
TEXTCACHE = READINGS / ".textcache"
REPORTS = READINGS / "reports"
SCHEMA = 1
TRANSCRIPTS = Path.home() / ".claude" / "projects" / ("-" + str(potw.REPO).strip("/").replace("/", "-"))

TYPES = ("empirical", "survey", "benchmark", "system", "theory", "position", "book-chapter")
RELATIONS = ("extends", "replicates", "contradicts", "baseline", "evaluates", "uses-method", "uses-data", "surveys",
             "related")
# Method keys added after the first pilots; a file without them still passes (trains defaults to true)
OPTIONAL_METHOD = ("trains", "prompts")
OPTIONAL_TOP = ("practices", "terms")
RESULT_KINDS = ("measured", "reported", "worked-example", "claim")
# Statuses whose PDF the pipeline has read, or will read
READ_STATUSES = ("integrated", "downloaded", "filed", "queued")
# What it takes to retrain or rerun an empirical paper; repro_score counts how many are stated
REPRO_FIELDS = (
    ("datasets", lambda m: bool(m.get("datasets"))),
    ("model size", lambda m: any(x.get("params") for x in m.get("models") or [])),
    ("objective", lambda m: stated(m, "training", "objective")),
    ("optimizer", lambda m: stated(m, "training", "optimizer")),
    ("learning rate", lambda m: stated(m, "training", "lr")),
    ("batch size", lambda m: stated(m, "training", "batch_size")),
    ("training length", lambda m: any(stated(m, "training", k) for k in ("steps", "epochs", "tokens"))),
    ("compute", lambda m: any(stated(m, "training", k) for k in ("hardware", "compute"))),
    ("eval metrics", lambda m: bool((m.get("eval") or {}).get("metrics"))),
    ("decoding", lambda m: any(stated(m, "inference", k) for k in ("decoding", "temperature"))),
    ("code or weights", lambda m: any(stated(m, "availability", k) for k in ("code", "weights"))),
)
# For work that trains nothing (prompting, decoding, evaluation): what it takes to rerun it
RERUN_FIELDS = (
    ("datasets", REPRO_FIELDS[0][1]),
    ("model size", REPRO_FIELDS[1][1]),
    ("eval metrics", REPRO_FIELDS[8][1]),
    ("decoding", REPRO_FIELDS[9][1]),
    ("samples or runs", lambda m: stated(m, "inference", "samples")),
    ("method parameters", lambda m: bool({k: v for k, v in ((m.get("inference") or {}).get("parameters") or {}).items()
                                          if not k.startswith("_") and v not in (None, "", [], {})})),
    ("prompts", lambda m: bool(m.get("prompts")) or stated(m, "inference", "prompting")),
    ("code or weights", REPRO_FIELDS[10][1]),
)
SECTION_HINTS = re.compile(
    r"^[ \t]*(?:(?:[A-H]|\d+(?:\.\d+)*)\.?[ \t]*\n?[ \t]*)?("
    r"appendix|supplementary|abstract|introduction|related work|background|method(?:s|ology)?|approach|"
    r"experiment(?:s|al setup| setup|al details)?|setup|implementation details|training details|"
    r"hyper-?parameters?|training|evaluation|results|ablations?|analysis|discussion|limitations?|"
    r"conclusions?|references|bibliography|datasets?|models?|baselines?|compute|reproducibility"
    r")\b[^\n]{0,50}$", re.I | re.M)
TABLE = re.compile(r"^\s*(table\s+[A-Z]?\d+[.:]?)[^\n]{0,80}", re.I | re.M)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*(?:\s*[eE]\s*[-−–]?\s*\d+)?")


def stated(m, block, key):
    v = (m.get(block) or {}).get(key)
    return v not in (None, "", [], {})


# --- keys and paths ----------------------------------------------------------


def safe_key(key):
    """A ledger key as a file name: arXiv ids stay as they are, URLs and DOIs get a readable slug plus a hash."""
    if re.fullmatch(r"[\w.-]+", key):
        return key
    if key.startswith("sha1:"):
        return "sha1-" + key[5:]
    slug = re.sub(r"[^\w.-]+", "-", key.split("://")[-1]).strip("-")[:60]
    return f"{slug}-{hashlib.sha1(key.encode()).hexdigest()[:8]}"


def path_for(key):
    return EXTRACTIONS / f"{safe_key(key)}.json"


def load(key):
    p = path_for(key)
    return json.loads(p.read_text()) if p.is_file() else None


def all_extractions():
    for p in sorted(EXTRACTIONS.glob("*.json")):
        try:
            yield p, json.loads(p.read_text())
        except json.JSONDecodeError as e:
            yield p, {"_error": str(e)}


def rows_by_key():
    return {r["key"]: r for r in potw.read_jsonl(potw.LEDGER) if not r.get("merged_into")}


def resolve(arg, rows):
    """A ledger row from a key, an arXiv id or a PDF path."""
    if arg in rows:
        return rows[arg]
    for r in rows.values():
        if arg in pdfs_of(r) or r.get("arxiv") == arg:
            return r
    base = os.path.basename(arg)
    hits = [r for r in rows.values() if any(os.path.basename(p) == base for p in pdfs_of(r))]
    if len(hits) == 1:
        return hits[0]
    # A bare slug or file stem: wang-2025-thoughts-all-over-place
    stem = base[:-4] if base.endswith(".pdf") else base
    hits = [r for r in rows.values()
            if r.get("slug") == stem or any(os.path.basename(p)[:-4] == stem for p in pdfs_of(r))]
    return hits[0] if len(hits) == 1 else None


def pdfs_of(r):
    out = [r["local_pdf"]] if r.get("local_pdf") else []
    copies = r.get("copies") or []
    return out + ([copies] if isinstance(copies, str) else list(copies))


def is_chapter(r):
    return bool(re.search(r"/sources/[^/]+/(?:ch\d\d|appendix)[^/]*\.pdf$", r.get("local_pdf") or ""))


# --- text --------------------------------------------------------------------


def file_sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_text(pdf, engine):
    """Cached text of a PDF from one engine (pymupdf or pypdf); None if the engine is not installed."""
    pdf = Path(pdf) if Path(pdf).is_absolute() else potw.REPO / pdf
    cache = TEXTCACHE / f"{file_sha1(pdf)}.{engine}.txt"
    if cache.is_file():
        return cache.read_text()
    try:
        if engine == "pymupdf":
            import pymupdf
            with pymupdf.open(pdf) as doc:
                text = "\n".join(page.get_text() for page in doc)
        else:
            import pypdf
            text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(pdf).pages)
    except ImportError:
        return None
    # PDF text layers can hold lone surrogates (e.g. "\ud835" from math alphanumerics) that UTF-8 refuses.
    text = text.encode("utf-8", "replace").decode("utf-8")
    TEXTCACHE.mkdir(exist_ok=True)
    cache.write_text(text)
    return text


def norm_text(s):
    """Lower case, ligatures and dashes unified, line-break hyphens joined, whitespace collapsed."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("­", "").translate(str.maketrans("‐‑‒–—−“”‘’×", "------\"\"''x"))
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def squash(s):
    return re.sub(r"[\s\-]+", "", norm_text(s))


def contains(texts, needle):
    """Is `needle` in any of the texts, allowing for the spacing pypdf drops and the hyphens it adds."""
    n, sq = norm_text(needle), squash(needle)
    if not sq:
        return True
    for t in texts:
        if n in t["norm"] or sq in t["squash"]:
            return True
        if "..." in needle or "…" in needle:  # an elided quote: every piece must be there, in order
            parts = [squash(p) for p in re.split(r"\.\.\.|…", needle) if squash(p)]
            pos = 0
            for p in parts:
                pos = t["squash"].find(p, pos)
                if pos < 0:
                    break
            else:
                return True
    return False


def number_forms(token):
    """Ways a number can be printed: 3e-4 as 3e-4, 3x10-4, 0.0003; 1,000 as 1000."""
    t = token.replace(" ", "").replace("−", "-").replace("–", "-")
    forms = {t, t.replace(",", "")}
    m = re.fullmatch(r"(\d+(?:\.\d+)?)[eE](-?\d+)", t)
    if m:
        mant, exp = m.groups()
        forms |= {f"{mant}x10{exp}", f"{mant}·10{exp}", f"{mant}*10{exp}", f"10{exp}" if mant == "1" else f"{mant}e{exp}"}
        try:
            forms.add(f"{float(t):.10f}".rstrip("0").rstrip("."))
        except ValueError:
            pass
    return {squash(f) for f in forms if f}


def numbers_in(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [repr(value)]
    if isinstance(value, list):
        return [n for v in value for n in numbers_in(v)]
    if isinstance(value, str):
        return [n for n in NUMBER.findall(value) if len(n.replace(",", "").replace(".", "")) >= 2 or "e" in n.lower()]
    return []


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def is_heading(line):
    """A short line that starts with a capital and does not read like a sentence or a formula."""
    line = line.strip()
    return (len(line) <= 60 and line[:1].isupper() and not line.endswith((".", ",", ";", ":"))
            and not re.search(r"[=·(){}\[\]]", line))


def section_map(text):
    marks = [(m.start(), " ".join(m.group(0).split())) for m in SECTION_HINTS.finditer(text)
             if is_heading(m.group(0).split("\n")[-1])]
    marks += [(m.start(), m.group(0).strip()) for m in TABLE.finditer(text)]
    return sorted(marks)


# --- checks ------------------------------------------------------------------


def schema_errors(x):
    errs = []
    if x.get("schema") not in (0, SCHEMA):
        errs.append(f"schema is {x.get('schema')!r}, expected 0 or {SCHEMA}")
        return errs
    for k in ("key", "pdf"):
        if not x.get(k):
            errs.append(f"missing {k}")
    if x["schema"] == 0:
        if not (x.get("legacy_report") or "").strip():
            errs.append("schema 0 needs legacy_report")
        return errs
    template = json.loads(TEMPLATE.read_text())
    for k in template:
        if k.startswith("_") or k in OPTIONAL_TOP:
            continue
        if k not in x:
            errs.append(f"missing top-level field {k}")
    if x.get("type") not in TYPES:
        errs.append(f"type {x.get('type')!r} is not one of {', '.join(TYPES)}")
    read = x.get("read") or {}
    if not isinstance(read.get("chars_read"), int) or not isinstance(read.get("chars_total"), int):
        errs.append("read.chars_read and read.chars_total must be integers")
    if x.get("type") in ("empirical", "system", "benchmark"):
        m = x.get("method")
        if not isinstance(m, dict):
            errs.append("an empirical, system or benchmark paper needs a method block")
        else:
            for k in template["method"]:
                if not k.startswith("_") and k not in OPTIONAL_METHOD and k not in m:
                    errs.append(f"method.{k} missing (use null or [] when the paper does not state it)")
    for i, r in enumerate(x.get("results") or []):
        if not r.get("claim"):
            errs.append(f"results[{i}] has no claim")
        if r.get("value") not in (None, "") and not r.get("quote") and not r.get("table"):
            errs.append(f"results[{i}] has a value but no quote (or table reference)")
        if not r.get("setup"):
            errs.append(f"results[{i}] has no setup")
        if r.get("kind") not in (None, *RESULT_KINDS):
            errs.append(f"results[{i}].kind {r.get('kind')!r} is not one of {', '.join(RESULT_KINDS)}")
    for i, l in enumerate(x.get("lineage") or []):
        if l.get("relation") not in RELATIONS:
            errs.append(f"lineage[{i}].relation {l.get('relation')!r} is not one of {', '.join(RELATIONS)}")
        if not l.get("work"):
            errs.append(f"lineage[{i}] has no work")
    return errs


def evidence_problems(x, texts):
    """(errors, warnings): result quotes not in the PDF are errors; method numbers not in the PDF are warnings."""
    errs, warns = [], []
    for i, r in enumerate(x.get("results") or []):
        if r.get("quote") and not contains(texts, r["quote"]):
            errs.append(f"results[{i}].quote not found in the PDF text: {r['quote'][:80]!r}")
        elif r.get("table") and not r.get("quote"):
            # A table cell: the value's numbers must occur somewhere in the text
            for n in numbers_in(r.get("value")):
                if not any(f in t["squash"] for t in texts for f in number_forms(n)):
                    errs.append(f"results[{i}].value {n} (from {r['table']}) is not in the PDF text")
    for i, l in enumerate(x.get("lineage") or []):
        if l.get("quote") and not contains(texts, l["quote"]):
            warns.append(f"lineage[{i}].quote not found: {l['quote'][:80]!r}")
    for path, value in walk({"method": x.get("method") or {}}):
        if path.endswith((".quote", ".text")) and isinstance(value, str) and value and not contains(texts, value):
            warns.append(f"{path} not found: {value[:80]!r}")
            continue
        if path.endswith((".where", ".field", "._comment", ".purpose", ".quote", ".text")):
            continue
        if isinstance(value, str) and value.lower().startswith("inferred:"):
            continue
        for n in numbers_in(value):
            if not any(f in t["squash"] for t in texts for f in number_forms(n)):
                warns.append(f"{path}: {n} is not in the PDF text (derived, or a misread?)")
    return errs, warns


def texts_for(x):
    out = []
    pdf = potw.REPO / x["pdf"]
    if not pdf.is_file():
        return None
    for engine in ("pymupdf", "pypdf"):
        t = pdf_text(pdf, engine)
        if t:
            out.append({"norm": norm_text(t), "squash": squash(t)})
    return out


def repro(x):
    """(score 0-3, stated, missing) for an empirical paper; None for other types."""
    if x.get("schema") != SCHEMA or x.get("type") not in ("empirical", "system") or not isinstance(x.get("method"), dict):
        return None
    m = x["method"]
    fields = REPRO_FIELDS if m.get("trains", True) is not False else RERUN_FIELDS
    have = [name for name, ok in fields if ok(m)]
    missing = [name for name, ok in fields if not ok(m)]
    frac = len(have) / len(fields)
    return (3 if frac >= 0.85 else 2 if frac >= 0.6 else 1 if frac >= 0.3 else 0), have, missing


def check_one(path, x, rows, schema_only=False, strict=False):
    errs = ["invalid JSON: " + x["_error"]] if "_error" in x else schema_errors(x)
    warns = []
    if errs:
        return errs, warns
    if x["key"] not in rows:
        errs.append(f"no ledger row for key {x['key']!r}")
    elif path.name != path_for(x["key"]).name:
        errs.append(f"file name should be {path_for(x['key']).name}")
    if not schema_only and x["schema"] == SCHEMA:
        texts = texts_for(x)
        if texts is None:
            errs.append(f"PDF not found: {x['pdf']}")
        elif not texts:
            warns.append("no PDF engine installed: run under uv with --with pymupdf --with pypdf to check evidence")
        else:
            e, w = evidence_problems(x, texts)
            errs += e
            warns += w
    if strict:
        errs, warns = errs + warns, []
    return errs, warns


# --- commands ----------------------------------------------------------------


def cmd_text(args):
    rows = rows_by_key()
    r = resolve(args.target, rows)
    pdf = r["local_pdf"] if r else args.target
    if not (potw.REPO / pdf).is_file():
        sys.exit(f"text: no PDF for {args.target}")
    text = pdf_text(pdf, "pymupdf") or pdf_text(pdf, "pypdf")
    if text is None:
        sys.exit("text: needs pymupdf or pypdf; run under uv run -q --with pymupdf --with pypdf")
    cache = TEXTCACHE / f"{file_sha1(potw.REPO / pdf)}.{'pymupdf' if pdf_text(pdf, 'pymupdf') else 'pypdf'}.txt"
    print(f"key: {r['key'] if r else '(no ledger row)'}")
    print(f"pdf: {pdf}")
    print(f"text: {cache.relative_to(potw.REPO)} ({len(text)} chars)")
    print(f"extraction: {path_for(r['key']).relative_to(potw.REPO) if r else '-'}")
    print("sections and tables (char offset):")
    for off, label in section_map(text):
        print(f"  {off:>8}  {label[:90]}")


def cmd_check(args):
    rows = rows_by_key()
    if args.all:
        items = list(all_extractions())
    else:
        items = []
        for k in args.keys:
            r = resolve(k, rows)
            p = path_for(r["key"] if r else k)
            if not p.is_file():
                print(f"FAIL {k}: no extraction at {p.relative_to(potw.REPO)}")
                items.append(None)
                continue
            items.append((p, json.loads(p.read_text()) if p.read_text().strip() else {"_error": "empty file"}))
    failed = 0
    for item in items:
        if item is None:
            failed += 1
            continue
        p, x = item
        errs, warns = check_one(p, x, rows, schema_only=args.schema_only, strict=args.strict)
        name = p.relative_to(potw.REPO)
        if errs:
            failed += 1
            print(f"FAIL {name}", *errs, sep="\n  ")
        if warns and not args.quiet:
            print(f"warn {name}", *warns, sep="\n  ")
        if not errs and not args.all:
            sc = repro(x)
            print(f"ok   {name} (schema {x['schema']}" + (f", repro {sc[0]}/3, missing: {', '.join(sc[2]) or 'none'}" if sc else "") + ")")
    if args.all:
        print(f"{len(items)} extractions, {failed} failing")
    sys.exit(1 if failed else 0)


def backlog_rows(rows):
    return [r for r in rows.values()
            if r.get("status") in READ_STATUSES and r.get("local_pdf") and (potw.REPO / r["local_pdf"]).is_file()]


def cmd_status(args):
    rows = rows_by_key()
    by_home = defaultdict(Counter)
    rest = Counter()
    for r in backlog_rows(rows):
        home = r.get("pillar") or "none"
        if args.home and home != args.home:
            continue
        x = load(r["key"])
        if not in_scope(r, args.all):
            if not (x and x.get("schema") == SCHEMA):
                rest["v0" if x else "none"] += 1
            continue
        by_home[home]["v1" if x and x.get("schema") == SCHEMA else "v0" if x else "none"] += 1
    total = Counter()
    print(f"{'home':<18} {'full':>6} {'salvaged':>9} {'none':>6}")
    for home in sorted(by_home):
        c = by_home[home]
        total.update(c)
        print(f"{home:<18} {c['v1']:>6} {c['v0']:>9} {c['none']:>6}")
    print(f"{'all':<18} {total['v1']:>6} {total['v0']:>9} {total['none']:>6}")
    print("full = schema 1; salvaged = old text report only, still needs a read for its method")
    if not args.all:
        print(f"scope: tier 1, tier 2 and book chapters. Not counted: {sum(rest.values())} paper-tier 3-6 readings "
              f"without a full extraction ({rest['v0']} salvaged); --all includes them")


# Buckets 1-3 are the core backfill: tier 1, tier 2, book chapters. The rest (paper tiers 3-6, buckets 4-7)
# is backfilled only once the core is empty, with --all: a later /papers read writes those extractions anyway.
CORE_BUCKET = 3


def bucket(r):
    """tier 1 and 2 first, then book chapters, then the remaining paper tiers."""
    tier = potw.integration_tier(r)
    return tier if tier <= 2 else 3 if is_chapter(r) else tier + 1


def in_scope(r, everything=False):
    return everything or bucket(r) <= CORE_BUCKET


def next_rows(rows, home=None, include_v0=True, everything=False):
    out = []
    for r in backlog_rows(rows):
        if home and r.get("pillar") != home:
            continue
        x = load(r["key"])
        if x and x.get("schema") == SCHEMA:
            continue
        if x and not include_v0:
            continue
        b = bucket(r)
        if b > CORE_BUCKET and not everything:
            continue
        # within a bucket, the most cited first
        out.append((b, -(r.get("citations") or 0), r["key"], r))
    return [t[-1] for t in sorted(out, key=lambda t: t[:3])]


def cmd_next(args):
    rows = rows_by_key()
    picked = next_rows(rows, args.home, include_v0=args.include_v0, everything=args.all)
    if args.count:
        print(len(picked))
        return
    if args.homes:
        print("\n".join(sorted({r.get("pillar") or "none" for r in picked})))
        return
    for r in picked[: args.n]:
        x = load(r["key"])
        print("\t".join([r["key"], r["local_pdf"], r.get("note") or "-", "salvaged" if x else "none",
                         str(path_for(r["key"]).relative_to(potw.REPO))]))


def cmd_path(args):
    rows = rows_by_key()
    r = resolve(args.target, rows)
    if not r:
        sys.exit(f"path: no ledger row for {args.target}")
    print(path_for(r["key"]).relative_to(potw.REPO))


# --- salvage -----------------------------------------------------------------


def transcript_reports(root=TRANSCRIPTS):
    """Yield (timestamp, session, prompt, report) for every source-reader run in the session transcripts."""
    for f in glob.glob(str(root / "*" / "subagents" / "*.jsonl")):
        try:
            meta = json.loads(Path(f[:-6] + ".meta.json").read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("agentType") != "source-reader":
            continue
        try:
            lines = [json.loads(l) for l in open(f) if l.strip()]
        except (OSError, json.JSONDecodeError):
            continue
        if not lines:
            continue
        prompt = lines[0].get("message", {}).get("content", "")
        if not isinstance(prompt, str):
            prompt = " ".join(b.get("text", "") for b in prompt if isinstance(b, dict))
        best = ""
        for l in lines:
            if l.get("type") != "assistant":
                continue
            content = l["message"].get("content", [])
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            for b in content:
                t = ""
                if b.get("type") == "text":
                    t = b.get("text", "")
                elif b.get("type") == "tool_use":
                    inp = b.get("input", {})
                    t = inp if isinstance(inp, str) else next(
                        (v for v in inp.values() if isinstance(v, str) and ("COVERAGE" in v or "CLAIMS" in v)), "")
                if ("COVERAGE" in t or "CLAIMS" in t) and len(t) > len(best):
                    best = t
        if best:
            yield lines[0].get("timestamp", ""), lines[0].get("sessionId", ""), prompt, best


def match_report(prompt, report, rows, by_pdf, by_base):
    cands = set()
    for p in re.findall(r"[\w./()&%+-]+\.pdf", prompt + "\n" + report[:600]):
        p = p.replace(str(potw.REPO) + "/", "").lstrip("./")
        if p in by_pdf:
            cands.add(by_pdf[p])
        elif len(by_base.get(os.path.basename(p), ())) == 1:
            cands.add(by_base[os.path.basename(p)][0])
    for aid in re.findall(r"(?<![\d.])(\d{4}\.\d{4,5})(?!\d)", prompt):
        if aid in rows and rows[aid].get("local_pdf"):
            cands.add(aid)
    return cands


def salvage(rows, reports, dry_run=False):
    by_pdf, by_base = {}, defaultdict(list)
    for r in rows.values():
        for p in pdfs_of(r):
            by_pdf[p] = r["key"]
            by_base[os.path.basename(p)].append(r["key"])
    best = {}
    stats = Counter()
    for ts, session, prompt, report in reports:
        keys = match_report(prompt, report, rows, by_pdf, by_base)
        if len(keys) != 1:
            stats["unmatched" if not keys else "ambiguous"] += 1
            continue
        key = keys.pop()
        partial = bool(re.search(r"COVERAGE:[^\n]*(partial|did not read|skipp|not read)", report, re.I))
        rank = (not partial, ts)
        if key not in best or rank > best[key][0]:
            best[key] = (rank, ts, session, report)
        stats["matched"] += 1
    written = kept = 0
    for key, (_, ts, session, report) in sorted(best.items()):
        existing = load(key)
        if existing and existing.get("schema") == SCHEMA:
            kept += 1
            continue
        if existing and existing.get("read", {}).get("at", "") >= ts[:10] and existing.get("legacy_report") == report:
            continue
        r = rows[key]
        x = {
            "schema": 0, "key": key, "pdf": r["local_pdf"],
            "bib": {"title": r.get("arxiv_title") or r.get("title"), "first_author": r.get("first_author"),
                    "year": r.get("year"), "venue": r.get("venue"), "arxiv": r.get("arxiv"), "doi": r.get("doi")},
            "read": {"by": "source-reader", "at": ts[:10], "session": session},
            "legacy_report": report.strip(),
        }
        written += 1
        if not dry_run:
            EXTRACTIONS.mkdir(exist_ok=True)
            path_for(key).write_text(json.dumps(x, indent=1, ensure_ascii=False) + "\n")
    stats.update(written=written, kept_full=kept, keys=len(best))
    return stats


def cmd_salvage(args):
    root = Path(args.transcripts) if args.transcripts else TRANSCRIPTS
    stats = salvage(rows_by_key(), transcript_reports(root), dry_run=args.dry_run)
    print(f"reports matched to one reading: {stats['matched']} (unmatched {stats['unmatched']}, ambiguous {stats['ambiguous']})")
    print(f"readings with a report: {stats['keys']}; {'would write' if args.dry_run else 'wrote'} {stats['written']} "
          f"schema-0 files; left {stats['kept_full']} that already have a full extraction")


# --- reports -----------------------------------------------------------------


def resolver(rows):
    by_title = {}
    for r in rows.values():
        for t in (r.get("title"), r.get("arxiv_title")):
            if t:
                by_title[norm_text(t)] = r["key"]

    def find(l):
        if l.get("arxiv") and l["arxiv"] in rows:
            return l["arxiv"]
        return by_title.get(norm_text(l.get("work", "")))
    return find


def label(rows, key, x=None):
    r = rows.get(key, {})
    who = (r.get("first_author") or "").split()[-1:] or ["?"]
    return f"{who[0]} {r.get('year') or ''}, *{(x or {}).get('bib', {}).get('title') or r.get('title') or key}*".replace(" ,", ",")


def cmd_report(args):
    rows = rows_by_key()
    find = resolver(rows)
    full = {x["key"]: x for _, x in all_extractions() if x.get("schema") == SCHEMA and x.get("key") in rows}
    today = dt.date.today().isoformat()

    lines = [f"# Lineage", "", f"Generated by `extract.py report` on {today} from {len(full)} full extractions. "
             "Each line is what a paper says about earlier work, with the relation the reader recorded. "
             "A linked key is a reading we hold.", ""]
    contra = []
    by_home = defaultdict(list)
    for key, x in sorted(full.items()):
        by_home[rows[key].get("pillar") or "none"].append((key, x))
        for l in x.get("lineage") or []:
            if l.get("relation") == "contradicts":
                contra.append((key, l))
    lines += ["## Disagreements", ""]
    lines += [f"- {label(rows, k)} contradicts {l['work']}" + (f" (`{find(l)}`)" if find(l) else "")
              + (f": {l['note']}" if l.get("note") else "") for k, l in contra] or ["None recorded yet."]
    for home in sorted(by_home):
        lines += ["", f"## {home}", ""]
        for key, x in by_home[home]:
            rel = defaultdict(list)
            for l in x.get("lineage") or []:
                k = find(l)
                rel[l["relation"]].append(l["work"] + (f" (`{k}`)" if k else ""))
            if rel:
                lines.append(f"- `{key}` {label(rows, key, x)}: " + "; ".join(f"**{r}** {', '.join(w)}" for r, w in rel.items()))
    (REPORTS / "lineage.md").write_text("\n".join(lines) + "\n")

    scored = sorted(((repro(x), key, x) for key, x in full.items() if repro(x)), key=lambda t: (-t[0][0], t[1]))
    lines = ["# Reproducibility", "", f"Generated by `extract.py report` on {today}. For each empirical or system paper with a "
             "full extraction: how much of what you need to retrain or rerun it the paper states. Score 3 states at "
             f"least 85% of the {len(REPRO_FIELDS)} fields, 2 at least 60%, 1 at least 30%.", "",
             "| Score | Paper | Home | Not stated |", "|---|---|---|---|"]
    lines += [f"| {s[0]} | `{key}` {label(rows, key, x)} | {rows[key].get('pillar') or ''} | {', '.join(s[2]) or 'none'} |"
              for s, key, x in scored]
    (REPORTS / "reproducible.md").write_text("\n".join(lines) + "\n")
    print(f"wrote reports/lineage.md ({len(full)} papers, {len(contra)} disagreements) and reports/reproducible.md ({len(scored)} scored)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("text", help="cache a PDF's text and print its section and table offsets")
    p.add_argument("target", help="ledger key, arXiv id or PDF path")
    p.set_defaults(fn=cmd_text)
    p = sub.add_parser("check", help="validate extractions; with a PDF engine, check quotes and method numbers against the text")
    p.add_argument("keys", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--schema-only", action="store_true", help="skip the PDF text checks (fast; what make test runs)")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    p.add_argument("--quiet", action="store_true", help="print failures only")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("status", help="extraction coverage per home (tier 1, tier 2 and book chapters unless --all)")
    p.add_argument("--home")
    p.add_argument("--all", action="store_true", help="count paper tiers 3-6 too")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("next", help="readings still needing a full extraction, best first: key, pdf, note, state, path")
    p.add_argument("--home")
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--count", action="store_true")
    p.add_argument("--homes", action="store_true", help="print the homes with a backlog")
    p.add_argument("--no-v0", dest="include_v0", action="store_false", help="skip readings that have a salvaged report")
    p.add_argument("--all", action="store_true", help="include paper tiers 3-6 after the core (tier 1, tier 2, chapters)")
    p.set_defaults(fn=cmd_next)
    p = sub.add_parser("path", help="where a reading's extraction file goes")
    p.add_argument("target")
    p.set_defaults(fn=cmd_path)
    p = sub.add_parser("salvage", help="recover old source-reader reports from session transcripts as schema-0 files")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--transcripts", help=f"transcript folder (default {TRANSCRIPTS})")
    p.set_defaults(fn=cmd_salvage)
    p = sub.add_parser("report", help="write reports/lineage.md and reports/reproducible.md")
    p.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
