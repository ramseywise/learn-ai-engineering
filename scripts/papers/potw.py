#!/usr/bin/env python3
"""Readings ledger: AI Papers of the Week -> pillar sources/, plus every PDF already in the repo.

  fetch     pull DAIR's years/<YYYY>.md and append unseen papers to the ledger
  triage    assign each new paper a pillar + target note (one `claude -p` call per batch)
  download  fetch arXiv PDFs for queued papers into <pillar>/sources/<author-year-slug>.pdf
  scan      register every PDF in the repo (source "repo") and set have_pdf / local_pdf
  run       fetch + triage + scan + download (what the weekly launchd job calls)
  status    counts by status, or list one status with --list
  mark      set a paper's status (the /papers skill marks papers `integrated`)

Ledger: ai-engineering/readings/ledger.jsonl, one reading per line — the single source of
truth for what we have and where it came from. `source` is "dair" (fetched from AI Papers
of the Week) or "repo" (a PDF found in the repo). Keyed by arXiv id, else the DAIR URL,
else `sha1:<hash>` of the file, so moving a PDF keeps its row. Every triaged paper gets a
`topic` (TOPICS below) — the sort key for all readings; `pillar` is set only when the
course uses it. Writing findings
into the notes is the /papers skill's job, not this script's — nothing here edits
markdown or commits.

Backfill (older weeks, tagged `backlog` so the weekly run leaves them alone):
  potw.py fetch --years 2023 2024 2025 2026 --since 2023-01-01
  potw.py triage --backlog
  potw.py download --backlog
"""
import argparse
import hashlib
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AI_ENG = REPO / "ai-engineering"
LEDGER = AI_ENG / "readings" / "ledger.jsonl"
# summaries/abstracts for triage, one file per year to stay under the pre-commit size limit
BLURBS = AI_ENG / "readings" / "blurbs"
# empty fields aren't written to the ledger; load_ledger puts these back as None
FIELDS = ("arxiv", "url", "pillar", "note", "topic", "local_pdf", "copies", "sha1")
RAW_URL = "https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/years/{year}.md"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={id}&max_results=100"
ARXIV_PDF = "https://arxiv.org/pdf/{id}"
USER_AGENT = "learn-ai-engineering-potw/1.0 (mailto:ramsey.wise@gmail.com)"
TRIAGE_MODEL = os.environ.get("POTW_TRIAGE_MODEL", "claude-haiku-5-5")
TRIAGE_BATCH = 25

PILLARS = {
    "prompt": "01-prompt-engineering",
    "context": "02-context-engineering",
    "harness": "03-harness-engineering",
    "loop": "04-loop-engineering",
    "graph": "05-graph-engineering",
    "eval": "06-eval",
}
# Sort key for every reading. The six pillars first, then the off-syllabus buckets.
TOPICS = {
    **{p: f"course pillar ({f})" for p, f in PILLARS.items()},
    "llm-fundamentals": "architecture, pretraining, scaling laws, tokenization, long-context models",
    "post-training": "RL, RLHF/DPO, fine-tuning, distillation, reasoning-model training",
    "inference": "serving, efficiency, quantization, kernels, hardware",
    "interpretability": "mechanistic interpretability, probing, model internals",
    "safety": "alignment, security, red-teaming, misuse, policy",
    "multimodal": "vision, audio, video, robotics, embodied models",
    "applications": "domain applications: science, medicine, finance, education",
    "other": "anything that fits none of the above",
}
SKIP_NOTES = {"README.md", "references.md", "OUTLINE.md"}
PDF_SKIP_DIRS = {".git", "node_modules", ".venv", "idk"}
STOPWORDS = {"a", "an", "the", "of", "for", "and", "in", "on", "to", "with", "via", "is", "are", "by", "from", "at"}

# 2023-25 headings omit the trailing "- YYYY"; fall back to the page's year
week_re = re.compile(r"^## Top AI Papers of the Week \((\w+) (\d+)\s*[-–]\s*(\w+).*?\)(?:\s*-\s*(\d{4}))?")
row_re = re.compile(r"^\|\s*\d+\)\s*\*\*(.+?)\*\*\s*[-–:]?\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
link_re = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
# arxiv.org/abs/<id>, or DAIR academy pages whose slug ends in the arXiv id
arxiv_re = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})|academy\.dair\.ai/papers/\S*-(\d{4}\.\d{4,5})/?$")


def log(msg):
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# --- ledger -----------------------------------------------------------------


def read_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    tmp.replace(path)


def load_ledger():
    """Ledger rows, each with its `blurb` joined back in from blurbs/<year>.jsonl ("" if missing)."""
    blurbs = {b["key"]: b["blurb"] for path in sorted(BLURBS.glob("*.jsonl")) for b in read_jsonl(path)}
    rows = read_jsonl(LEDGER)
    for r in rows:
        r["blurb"] = r.get("blurb") or blurbs.get(r["key"], "")
        r.pop("week", None)  # old rows: the heading text, redundant with week_start
        for k in FIELDS:
            r.setdefault(k, None)
        r.setdefault("have_pdf", False)
    return rows


def empty(v):
    return v is None or v is False or v == "" or v == []  # not 0: relevance 0 is a verdict


def save_ledger(rows):
    # repo-only readings have no week; they sort first, by path
    rows.sort(key=lambda r: (r.get("week_start") or "", r.get("rank") or 0, r.get("local_pdf") or "", r["key"]))
    by_year = {}
    for r in rows:
        if r.get("blurb"):
            year = (r.get("week_start") or r.get("added_at") or "undated")[:4]
            by_year.setdefault(year, []).append({"key": r["key"], "blurb": r["blurb"]})
    for year, items in by_year.items():
        write_jsonl(BLURBS / f"{year}.jsonl", items)
    write_jsonl(LEDGER, ({k: v for k, v in r.items() if k != "blurb" and not empty(v)} for r in rows))


# --- fetch ------------------------------------------------------------------


def parse_year(md, page_year):
    """Yield one dict per paper row in a DAIR years/<YYYY>.md page."""
    week = week_start = None
    for line in md.splitlines():
        m = week_re.match(line)
        if m:
            month, day, end_month, year = m.groups()
            year = year or page_year
            # some 2023 headings abbreviate the month ("Mar 27")
            fmt = "%B %d %Y" if len(month) > 3 else "%b %d %Y"
            start = dt.datetime.strptime(f"{month} {day} {year}", fmt).date()
            # "December 29 - January 4" is filed under the year it ends in
            if end_month.startswith("Jan") and month.startswith("Dec"):
                start = start.replace(year=start.year - 1)
            week_start = start.isoformat()
            week = line.removeprefix("## ").strip()
            continue
        m = row_re.match(line)
        if not (m and week):
            continue
        title, blurb, links = m.groups()
        urls = {label.strip().lower(): url for label, url in link_re.findall(links)}
        url = urls.get("paper") or next((u for u in urls.values() if "x.com" not in u and "twitter" not in u), None)
        if not url:
            continue
        m = next(filter(None, (arxiv_re.search(u) for u in [url, *urls.values()])), None)
        aid = (m.group(1) or m.group(2)) if m else None
        rank = int(re.match(r"^\|\s*(\d+)\)", line).group(1))
        yield {
            "key": aid or url,
            "arxiv": aid,
            "url": url,
            "title": title.strip(),
            "blurb": re.sub(r"\s*<br>\s*", " ", blurb).strip(),
            "week_start": week_start,
            "rank": rank,
            "status": "new",
            "source": "dair",
        }


def cmd_fetch(args):
    rows = load_ledger()
    seen = {r["key"]: r for r in rows}
    # Without --since, only pick up weeks at or after the newest one already in the
    # ledger, so the weekly job never backfills by accident.
    since = args.since or max((r["week_start"] for r in rows), default=None)
    added = 0
    for year in args.years:
        try:
            md = http_get(RAW_URL.format(year=year)).decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            log(f"fetch: no page for {year} yet")
            continue
        for paper in parse_year(md, year):
            if paper["key"] in seen:  # refill a missing blurb from the DAIR page
                seen[paper["key"]]["blurb"] = seen[paper["key"]]["blurb"] or paper["blurb"]
                continue
            if since and paper["week_start"] < since:
                continue
            # an explicit --since is a backfill: the weekly run leaves these alone
            # until `triage --backlog` / `download --backlog`
            if args.since:
                paper["backlog"] = True
            rows.append(paper)
            seen[paper["key"]] = paper
            added += 1
    save_ledger(rows)
    log(f"fetch: {added} new papers (ledger: {len(rows)})")


# --- triage -----------------------------------------------------------------


def note_inventory():
    """Lines of `path — H1 title` for every note a paper could map to."""
    lines = []
    for pillar, folder in PILLARS.items():
        base = AI_ENG / folder
        candidates = sorted(base.glob("*.md")) + sorted((base / "notes").glob("*.md"))
        for p in candidates:
            if p.name in SKIP_NOTES:
                continue
            h1 = next((l[2:].strip() for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), p.stem)
            lines.append(f"[{pillar}] {p.relative_to(AI_ENG)} — {h1}")
    return "\n".join(lines)


TRIAGE_PROMPT = """You are triaging research papers for an AI-engineering course with six pillars:
prompt, context, harness, loop, graph, eval. Course notes, by pillar:

{inventory}

For each paper below:
1. topic — ALWAYS set, exactly one of:
{topics}
2. pillar + note — which pillar it feeds and which single note its findings belong in.
3. relevance to the course (not general quality):
  3 = changes or sharpens a claim a note makes; the note should cite it
  2 = solid supporting evidence for a note
  1 = adjacent (training, architecture, hardware, a domain application) — course doesn't cover it
  0 = unrelated
Use pillar null and note null for relevance 0-1. A paper with a pillar has that pillar as its topic.

Papers (JSON):
{papers}

Reply with ONLY a JSON array, one object per paper, no prose:
[{{"key": "...", "topic": "loop", "pillar": "loop", "note": "04-loop-engineering/notes/08-self-improving-loops.md", "relevance": 3, "reason": "<one sentence>"}}]
"""


def find_claude():
    exe = shutil.which("claude")
    if not exe:
        sys.exit("triage: `claude` CLI not on PATH")
    return exe


def triage_batch(batch, inventory, claude):
    papers = json.dumps([{"key": r["key"], "title": r["title"], "summary": r["blurb"][:1200]} for r in batch], ensure_ascii=False)
    topics = "\n".join(f"  {t} — {desc}" for t, desc in TOPICS.items())
    prompt = TRIAGE_PROMPT.format(inventory=inventory, topics=topics, papers=papers)
    out = subprocess.run(
        [claude, "-p", "--model", TRIAGE_MODEL],
        input=prompt, capture_output=True, text=True, timeout=600, check=True,
    ).stdout
    m = re.search(r"\[.*\]", out, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON array in triage output: {out[:300]!r}")
    return {d["key"]: d for d in json.loads(m.group(0))}


def cmd_triage(args):
    rows = load_ledger()
    pending = [r for r in rows if r["status"] == "new" and (args.backlog or not r.get("backlog"))]
    if not pending:
        log("triage: nothing new")
        return
    inventory, claude = note_inventory(), find_claude()
    now = dt.datetime.now().isoformat(timespec="seconds")
    for i in range(0, len(pending), TRIAGE_BATCH):
        batch = pending[i : i + TRIAGE_BATCH]
        try:
            verdicts = triage_batch(batch, inventory, claude)
        except (subprocess.SubprocessError, ValueError, json.JSONDecodeError) as exc:
            log(f"triage: batch {i // TRIAGE_BATCH} failed, left as new: {exc}")
            continue
        for r in batch:
            v = verdicts.get(r["key"])
            if not v:
                continue
            pillar = v.get("pillar") if v.get("pillar") in PILLARS else None
            note = v.get("note")
            if note and not (AI_ENG / note).exists():
                note = None
            rel = int(v.get("relevance") or 0)
            topic = pillar or (v.get("topic") if v.get("topic") in TOPICS else "other")
            r.update(topic=topic, pillar=pillar, note=note, relevance=rel, reason=v.get("reason", ""), triaged_at=now)
            r["status"] = "queued" if pillar and rel >= args.min_relevance else "skipped"
        save_ledger(rows)
    counts = {s: sum(r["status"] == s for r in pending) for s in ("queued", "skipped", "new")}
    log(f"triage: {counts['queued']} queued, {counts['skipped']} skipped, {counts['new']} still new")


# --- download ---------------------------------------------------------------


def ascii_slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def arxiv_meta(aid):
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = ET.fromstring(http_get(ARXIV_API.format(id=aid))).find("a:entry", ns)
    if entry is None or entry.find("a:title", ns) is None:
        raise ValueError(f"arXiv has no entry for {aid}")
    title = " ".join(entry.find("a:title", ns).text.split())
    first_author = entry.find("a:author/a:name", ns).text.strip()
    year = entry.find("a:published", ns).text[:4]
    return title, first_author, year


def make_slug(title, first_author, year):
    surname = ascii_slug(first_author.split()[-1])
    head = re.split(r"[:?]", title)[0]
    words = [w for w in ascii_slug(head).split("-") if w and w not in STOPWORDS][:5]
    return f"{surname}-{year}-{'-'.join(words)}"


# --- scan -------------------------------------------------------------------

file_id_re = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(?:v\d+)?(?![\d])")
stamp_re = re.compile(r"arXiv:(\d{4}\.\d{4,5})")


def pdf_tidy_title(path, meta_title):
    """PDF metadata title when it looks real, else the filename."""
    t = " ".join((meta_title or "").split())
    if len(t) > 8 and not re.match(r"(microsoft word|untitled|\S+\.(docx?|tex|pdf)$)", t, re.I):
        return t
    return re.sub(r"[_\s]+", " ", path.stem).strip()


def local_pdfs(deep=False):
    """One dict per PDF in the repo: path, sha1, arXiv id, title, and (deep) page-1 text.

    Filenames carrying an arXiv id (1706.03762v7.pdf) always match. With deep=True, also
    read page 1 of every PDF for the arXiv stamp, metadata title and an excerpt for triage
    (needs pypdf: `uv run --with pypdf python scripts/papers/potw.py scan --deep`).
    """
    reader = None
    if deep:
        try:
            from pypdf import PdfReader as reader
        except ImportError:
            sys.exit("scan --deep needs pypdf: uv run --with pypdf python scripts/papers/potw.py scan --deep")
        import logging
        logging.getLogger("pypdf").setLevel(logging.ERROR)  # font/xref warnings drown the log
    pdfs = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = sorted(d for d in dirs if d not in PDF_SKIP_DIRS)
        for fname in sorted(files):
            if not fname.lower().endswith(".pdf"):
                continue
            path = Path(root) / fname
            ids, meta_title, text = file_id_re.findall(fname), None, ""
            if reader:
                try:
                    pdf = reader(path)
                    text = pdf.pages[0].extract_text() or ""
                    meta_title = (pdf.metadata or {}).get("/Title")
                    ids = ids or stamp_re.findall(text)[:1]
                except Exception:  # encrypted / malformed PDFs: filename only
                    pass
            pdfs.append({
                "path": str(path.relative_to(REPO)),
                "sha1": hashlib.sha1(path.read_bytes()).hexdigest(),
                "arxiv": ids[0] if ids else None,
                "title": pdf_tidy_title(path, meta_title if isinstance(meta_title, str) else None),
                "excerpt": " ".join(text.split())[:1200],
            })
    return pdfs


def arxiv_batch_meta(ids):
    """{id: (title, abstract)} for many arXiv ids, 100 per API call."""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = {}
    ids = sorted(ids)
    for i in range(0, len(ids), 100):
        chunk = ids[i : i + 100]
        try:
            feed = ET.fromstring(http_get(ARXIV_API.format(id=",".join(chunk))))
        except Exception as exc:
            log(f"scan: arXiv metadata failed for {len(chunk)} ids: {exc}")
            continue
        for entry in feed.findall("a:entry", ns):
            m = file_id_re.search(entry.findtext("a:id", "", ns))
            if m and entry.find("a:title", ns) is not None:
                out[m.group(1)] = (" ".join(entry.findtext("a:title", "", ns).split()),
                                   " ".join(entry.findtext("a:summary", "", ns).split()))
        time.sleep(3)
    return out


def sources_pillar(path):
    """The pillar whose sources/ folder holds this PDF, if any."""
    for pillar, folder in PILLARS.items():
        if path.startswith(f"ai-engineering/{folder}/sources/"):
            return pillar
    return None


def cmd_scan(args):
    rows = load_ledger()
    pdfs = local_pdfs(deep=getattr(args, "deep", False))
    # a plain scan can't see arXiv stamps inside PDFs; recover the id from the file hash
    # an earlier deep scan recorded
    arxiv_by_sha = {r["sha1"]: r["arxiv"] for r in rows if r.get("sha1") and r.get("arxiv")}
    by_arxiv, by_sha = {}, {}
    for f in pdfs:
        f["arxiv"] = f["arxiv"] or arxiv_by_sha.get(f["sha1"])
        if f["arxiv"]:
            by_arxiv.setdefault(f["arxiv"], []).append(f)
        else:
            by_sha.setdefault(f"sha1:{f['sha1'][:12]}", []).append(f)

    # every PDF gets a row: DAIR rows match by arXiv id, earlier repo rows by id or hash
    known = {r["key"] for r in rows}
    new_ids = [aid for aid in by_arxiv if aid not in known]
    meta = arxiv_batch_meta(new_ids) if new_ids else {}
    now = dt.datetime.now().isoformat(timespec="seconds")
    added = 0
    for key, group, aid in [(a, g, a) for a, g in by_arxiv.items()] + [(k, g, None) for k, g in by_sha.items()]:
        if key in known:
            continue
        first = group[0]
        title, abstract = meta.get(aid, (first["title"], ""))
        row = {
            "key": key, "arxiv": aid, "url": f"https://arxiv.org/abs/{aid}" if aid else None,
            "title": title, "blurb": abstract or first["excerpt"], "status": "new", "source": "repo",
            "area": first["path"].split("/")[0], "added_at": now,
        }
        pillar = sources_pillar(first["path"])
        if pillar:  # already filed in a pillar's sources/: it's course material, no triage needed
            row.update(status="integrated", pillar=pillar, topic=pillar)
        rows.append(row)
        known.add(key)
        added += 1

    found = 0
    for r in rows:
        group = by_arxiv.get(r["arxiv"]) if r.get("arxiv") else by_sha.get(r["key"])
        paths = [f["path"] for f in group or []]
        prior = r.get("local_pdf")
        if prior in paths or (not paths and prior and (REPO / prior).exists()):
            path = prior
        else:  # prefer the copy filed in a pillar's sources/
            path = next((p for p in paths if sources_pillar(p)), paths[0] if paths else None)
        r["have_pdf"], r["local_pdf"] = bool(path), path
        r["sha1"] = next((f["sha1"] for f in group or [] if f["path"] == path), r.get("sha1"))
        r["copies"] = [p for p in paths if p != path] or None
        found += bool(path)
    save_ledger(rows)
    log(f"scan: {len(pdfs)} PDFs in the repo, {added} new rows; {found}/{len(rows)} readings have a local PDF")


def cmd_download(args):
    rows = load_ledger()
    queued = [r for r in rows if r["status"] == "queued" and (args.backlog or not r.get("backlog"))]
    done = 0
    for r in queued:
        if r.get("have_pdf"):  # already in the repo — point at it, don't fetch a copy
            r.update(status="downloaded", pdf=os.path.relpath(REPO / r["local_pdf"], AI_ENG))
            log(f"download: {r['key']} already at {r['local_pdf']}")
            continue
        if not r["arxiv"]:
            r["status"] = "link-only"
            continue
        try:
            title, author, year = arxiv_meta(r["arxiv"])
            time.sleep(3)  # arXiv asks for >=3s between API calls
            sources = AI_ENG / PILLARS[r["pillar"]] / "sources"
            slug = make_slug(title, author, year)
            dest = sources / f"{slug}.pdf"
            if dest.exists() and not any(o.get("pdf") == str(dest.relative_to(AI_ENG)) and o["key"] == r["key"] for o in rows):
                dest = sources / f"{slug}-{r['arxiv']}.pdf"
            pdf = http_get(ARXIV_PDF.format(id=r["arxiv"]), timeout=120)
            time.sleep(3)
            if not pdf.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            sources.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(pdf)
        except Exception as exc:  # leave queued; next run retries
            log(f"download: {r['key']} failed: {exc}")
            continue
        r.update(
            status="downloaded", arxiv_title=title, first_author=author, year=year, slug=dest.stem,
            pdf=str(dest.relative_to(AI_ENG)), downloaded_at=dt.datetime.now().isoformat(timespec="seconds"),
            have_pdf=True, local_pdf=str(dest.relative_to(REPO)),
        )
        save_ledger(rows)
        done += 1
        log(f"download: {r['key']} -> {r['pdf']}")
    save_ledger(rows)
    log(f"download: {done}/{len(queued)} PDFs saved")


# --- status / mark ----------------------------------------------------------


def cmd_status(args):
    rows = load_ledger()
    if args.list:
        for r in rows:
            if r["status"] == args.list:
                print(json.dumps({k: r.get(k) for k in ("key", "title", "topic", "pillar", "note", "relevance", "pdf", "have_pdf", "reason", "url")}, ensure_ascii=False))
        return
    print(f"ledger: {LEDGER.relative_to(REPO)} ({len(rows)} papers, {sum(bool(r.get('have_pdf')) for r in rows)} with a PDF in the repo)")
    for field in ("source", "status", "topic"):
        counts = {}
        for r in rows:
            counts[r.get(field) or "-"] = counts.get(r.get(field) or "-", 0) + 1
        print(f"by {field}:")
        for value, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {value:<17} {n}")


def cmd_mark(args):
    rows = load_ledger()
    hits = [r for r in rows if r["key"] in args.keys]
    for r in hits:
        r["status"] = args.status
    save_ledger(rows)
    print(f"marked {len(hits)} as {args.status}")


def cmd_run(args):
    cmd_fetch(args)
    cmd_triage(args)
    cmd_scan(args)
    cmd_download(args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    # last year too, so the weeks around New Year are never missed
    this_year = dt.date.today().year
    default_years = [str(this_year - 1), str(this_year)]
    for name, fn in (("fetch", cmd_fetch), ("triage", cmd_triage), ("download", cmd_download), ("run", cmd_run)):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name in ("fetch", "run"):
            p.add_argument("--years", nargs="+", default=default_years)
            p.add_argument("--since", help="ignore weeks starting before YYYY-MM-DD")
        if name in ("triage", "run"):
            p.add_argument("--min-relevance", type=int, default=2)
        if name in ("triage", "download"):
            p.add_argument("--backlog", action="store_true", help="include backfilled papers")
        else:
            p.set_defaults(backlog=False)
    p = sub.add_parser("scan")
    p.add_argument("--deep", action="store_true", help="also read the arXiv stamp inside each PDF (needs pypdf)")
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("status")
    p.add_argument("--list", metavar="STATUS")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("mark")
    p.add_argument("status", choices=["new", "queued", "skipped", "downloaded", "link-only", "integrated"])
    p.add_argument("keys", nargs="+")
    p.set_defaults(fn=cmd_mark)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
