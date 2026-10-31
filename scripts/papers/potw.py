#!/usr/bin/env python3
"""Readings ledger: AI Papers of the Week -> pillar sources/, plus every PDF already in the repo.

  fetch     pull DAIR's years/<YYYY>.md and append unseen papers to the ledger
  triage    assign each new paper a home + target note (one `claude -p` call per batch)
  download  fetch arXiv PDFs for queued papers into <home>/sources/<author-year-slug>.pdf
  scan      register every PDF in the repo (source "repo") and set have_pdf / local_pdf
  route     move triaged PDFs out of the readings/ inbox into their home's sources/
  run       fetch + triage + scan + download (what the weekly launchd job calls)
  status    counts by status, or list one status with --list
  mark      set a paper's status (the /papers and /chapter skills mark papers `integrated`)

A *home* is the folder whose notes a reading feeds (HOMES below): the ai-engineering and
generative-ai pillars, plus data-science and data-engineering for classical ML and ML
systems. `pillar` in the ledger is the home key. `note` and `local_pdf` are repo-relative.

Ledger: ai-engineering/readings/ledger.jsonl, one reading per line — the single source of
truth for what we have and where it came from. `source` is "dair" (fetched from AI Papers
of the Week) or "repo" (a PDF found in the repo). Keyed by arXiv id, else the DAIR URL,
else `sha1:<hash>` of the file, so moving a PDF keeps its row. Every triaged paper gets a
`topic` (TOPICS below) — the sort key for all readings; `pillar` is set only when the
topic has a home. `skipped` means no home in this repo. Writing findings
into the notes is the /papers skill's job, not this script's — nothing here edits
markdown or commits.

Backfill (older weeks, tagged `backlog` so the weekly run leaves them alone):
  potw.py fetch --years 2023 2024 2025 2026 --since 2023-01-01
  potw.py triage --backlog
  potw.py download --backlog

Re-triage after HOMES changes (e.g. the repo PDFs triage once skipped):
  potw.py triage --status skipped --source repo
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
READINGS = AI_ENG / "readings"
LEDGER = READINGS / "ledger.jsonl"
# summaries/abstracts for triage, one file per year to stay under the pre-commit size limit
BLURBS = READINGS / "blurbs"
INBOX = "ai-engineering/readings/"  # PDFs dropped here wait for `route`
# empty fields aren't written to the ledger; load_ledger puts these back as None
FIELDS = ("arxiv", "url", "pillar", "note", "topic", "local_pdf", "copies", "sha1")
RAW_URL = "https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/years/{year}.md"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={id}&max_results=100"
ARXIV_PDF = "https://arxiv.org/pdf/{id}"
USER_AGENT = "learn-ai-engineering-potw/1.0 (mailto:ramsey.wise@gmail.com)"
TRIAGE_MODEL = os.environ.get("POTW_TRIAGE_MODEL", "claude-haiku-5-5")
TRIAGE_BATCH = 25

# Every topic with a home in the repo: key -> (folder, scope). The key is what the ledger
# stores as `pillar` (and `topic`). Pillar folders file PDFs under sources/; the two
# subject folders without pillars file them under readings/.
HOMES = {
    "prompt": ("ai-engineering/01-prompt-engineering",
               "prompt engineering: instructions, few-shot, chain-of-thought prompting, output formats, prompt injection"),
    "context": ("ai-engineering/02-context-engineering",
                "context engineering: window budgeting, retrieval as a context decision, memory, compaction, MCP and protocols"),
    "harness": ("ai-engineering/03-harness-engineering",
                "agent harness: tool design, execution boundaries, sandboxing, orchestration, human-in-the-loop, agent UX"),
    "loop": ("ai-engineering/04-loop-engineering",
             "agent loops: control flow, verification, autonomy levels, self-improving loops"),
    "graph": ("ai-engineering/05-graph-engineering",
              "multi-agent graphs and topologies, LangGraph, knowledge graphs and KG-RAG"),
    "eval": ("ai-engineering/06-eval",
             "evaluation: metrics, LLM-as-judge, benchmarks, tracing, production monitoring, feedback loops"),
    "inference": ("ai-engineering/07-inference-engineering",
                  "inference and systems performance: serving, batching, KV cache, prefill/decode, quantization, "
                  "GPU hardware, CUDA kernels, compilers, distributed training/inference infrastructure"),
    "llm-fundamentals": ("generative-ai/01-llm-fundamentals",
                         "how LLMs work: transformers, attention, embeddings, pretraining, scaling, tokenization, "
                         "classic NLP/LM papers, foundation-model surveys, generative image/audio models (VAE, GAN, diffusion, ViT)"),
    "rag": ("generative-ai/02-rag-retrieval",
            "RAG pipelines: chunking, embeddings, vector search, reranking, RAG architectures and RAG evaluation"),
    "agents": ("generative-ai/03-agentic-foundations",
               "agent foundations: reasoning and planning methods (ReAct, Tree of Thoughts, Reflexion), "
               "tool-use models, agent memory architectures, generative agents, agent design patterns"),
    "frameworks": ("generative-ai/04-agentic-frameworks",
                   "agent framework reference: LangGraph, ADK, AutoGen, CrewAI, framework comparisons"),
    "post-training": ("generative-ai/05-RL",
                      "RL, RLHF/DPO/GRPO, reward models, constitutional AI, fine-tuning, distillation, training-data engineering"),
    "observability": ("generative-ai/06-observability",
                      "LLM app observability tooling: tracing SDKs, LangFuse, scoring pipelines"),
    "agentic-apps": ("generative-ai/07-agentic-applications",
                     "built applications: chatbots, conversational AI and dialogue systems, deep-research agents, "
                     "human-AI interaction guidelines"),
    "classical-ml": ("data-science",
                     "classical ML and deep-learning training: model interpretability (SHAP, LIME), calibration, "
                     "normalization layers, classical NLP"),
    "ml-systems": ("data-engineering",
                   "ML engineering and MLOps: ML technical debt, software engineering for ML, metric pitfalls, "
                   "data warehousing and pipelines"),
}
PILLARS = {k: folder for k, (folder, _) in HOMES.items()}
# Readings that fit no home: kept in the ledger as `skipped`, never routed.
OFF_SYLLABUS = {
    "interpretability": "mechanistic interpretability, probing, model internals",
    "safety": "alignment research, red-teaming, misuse, policy",
    "multimodal": "vision, audio, video, robotics, embodied models (beyond the classic generative-model papers)",
    "domain-apps": "domain applications: science, medicine, finance, education",
    "other": "anything that fits none of the above",
}
# Sort key for every reading: the homes first, then the off-syllabus buckets.
TOPICS = {**{k: scope for k, (_, scope) in HOMES.items()}, **OFF_SYLLABUS}
SKIP_NOTES = {"README.md", "references.md", "OUTLINE.md", "CURRICULUM.md", "resources.md"}
PDF_SKIP_DIRS = {".git", "node_modules", ".venv", "idk"}
STOPWORDS = {"a", "an", "the", "of", "for", "and", "in", "on", "to", "with", "via", "is", "are", "by", "from", "at"}

# 2023-25 headings omit the trailing "- YYYY"; fall back to the page's year
week_re = re.compile(r"^## Top AI Papers of the Week \((\w+) (\d+)\s*[-–]\s*(\w+).*?\)(?:\s*-\s*(\d{4}))?")
row_re = re.compile(r"^\|\s*\d+\)\s*\*\*(.+?)\*\*\s*[-–:]?\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
link_re = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
# arxiv.org/abs/<id>, or DAIR academy pages whose slug ends in the arXiv id
arxiv_re = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})|academy\.dair\.ai/papers/\S*-(\d{4}\.\d{4,5})/?$")


def sources_rel(home):
    """Repo-relative folder a home files its PDFs in."""
    folder = PILLARS[home]
    return f"{folder}/{'sources' if '/' in folder else 'readings'}"


def is_tracked(path):
    return subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], cwd=REPO,
                          capture_output=True).returncode == 0


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
        r.pop("pdf", None)  # old rows: AI_ENG-relative copy of local_pdf
        if r.get("note") and not r["note"].startswith(tuple(f"{f.split('/')[0]}/" for f in PILLARS.values())):
            r["note"] = f"ai-engineering/{r['note']}"  # old rows: notes were AI_ENG-relative
        if r.get("topic") == "applications":
            r["topic"] = "domain-apps"  # renamed when agentic-apps got a home
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
    """Lines of `[home] path — H1 title` for every note a reading could map to (repo-relative)."""
    lines = []
    for home, folder in PILLARS.items():
        base = REPO / folder
        if "/" not in folder:  # subject folder without pillars: PDFs only, no note targets
            lines.append(f"[{home}] {folder}/ — no notes; file the PDF only (note null)")
            continue
        candidates = sorted(base.glob("*.md")) + sorted((base / "notes").glob("*.md"))
        found = False
        for p in candidates:
            if p.name in SKIP_NOTES:
                continue
            h1 = next((l[2:].strip() for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), p.stem)
            lines.append(f"[{home}] {p.relative_to(REPO)} — {h1}")
            found = True
        if not found:
            lines.append(f"[{home}] {folder}/ — no notes yet (note null)")
    return "\n".join(lines)


TRIAGE_PROMPT = """You are triaging readings (papers, book chapters) for a learning repo. Each reading
gets one home: the course folder whose notes it should feed. Homes and their scope:

{homes}

Notes that exist, by home (repo-relative path — title):

{inventory}

For each reading below:
1. topic — ALWAYS set: one home key above, or one of these off-syllabus keys when no home fits:
{off}
2. note — the single existing note (path from the list above) its content belongs in, or null
   when the home has no fitting note yet. Off-syllabus topics always have note null.
3. relevance to the repo (not general quality):
  3 = changes or sharpens a claim a note makes; the note should cite it
  2 = solid evidence for a note, or a core reading for its home
  1 = fits its home only loosely
  0 = unrelated to anything here
Prefer the most specific home: a RAG survey is `rag`, not `context`; PPO is `post-training`;
a CUDA or serving chapter is `inference`.

Readings (JSON):
{papers}

Reply with ONLY a JSON array, one object per reading, no prose:
[{{"key": "...", "topic": "loop", "note": "ai-engineering/04-loop-engineering/notes/08-self-improving-loops.md", "relevance": 3, "reason": "<one sentence>"}}]
"""


def find_claude():
    exe = shutil.which("claude")
    if not exe:
        sys.exit("triage: `claude` CLI not on PATH")
    return exe


def triage_batch(batch, inventory, claude):
    papers = json.dumps([{"key": r["key"], "title": r["title"], "summary": r["blurb"][:1200]} for r in batch], ensure_ascii=False)
    homes = "\n".join(f"  {k} ({folder}) — {scope}" for k, (folder, scope) in HOMES.items())
    off = "\n".join(f"  {t} — {desc}" for t, desc in OFF_SYLLABUS.items())
    prompt = TRIAGE_PROMPT.format(homes=homes, inventory=inventory, off=off, papers=papers)
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
    pending = [r for r in rows if r["status"] == args.status and (args.backlog or not r.get("backlog"))
               and (not args.source or r["source"] == args.source)]
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
            topic = v.get("topic") or v.get("pillar")
            topic = topic if topic in TOPICS else "other"
            pillar = topic if topic in HOMES else None
            note = v.get("note") if pillar else None
            if note and not ((REPO / note).is_file() and note.startswith(PILLARS[pillar] + "/")):
                note = None
            rel = int(v.get("relevance") or 0)
            r.update(topic=topic, pillar=pillar, note=note, relevance=rel, reason=v.get("reason", ""), triaged_at=now)
            # a PDF already in the repo only needs a home; a DAIR paper must earn its download
            floor = 1 if r["source"] == "repo" else args.min_relevance
            r["status"] = "queued" if pillar and rel >= floor else "skipped"
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
    """The home whose sources/ (or readings/) folder holds this PDF, if any."""
    for home in PILLARS:
        if path.startswith(sources_rel(home) + "/"):
            return home
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
        if r.get("have_pdf"):  # already in the repo — `route` files it, don't fetch a copy
            r["status"] = "downloaded"
            log(f"download: {r['key']} already at {r['local_pdf']}")
            continue
        if not r["arxiv"]:
            r["status"] = "link-only"
            continue
        try:
            title, author, year = arxiv_meta(r["arxiv"])
            time.sleep(3)  # arXiv asks for >=3s between API calls
            sources = REPO / sources_rel(r["pillar"])
            slug = make_slug(title, author, year)
            dest = sources / f"{slug}.pdf"
            if dest.exists():
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
            downloaded_at=dt.datetime.now().isoformat(timespec="seconds"),
            have_pdf=True, local_pdf=str(dest.relative_to(REPO)),
        )
        save_ledger(rows)
        done += 1
        log(f"download: {r['key']} -> {r['local_pdf']}")
    save_ledger(rows)
    log(f"download: {done}/{len(queued)} PDFs saved")


# --- route ------------------------------------------------------------------

# O'Reilly/Manning/Packt chapter exports: "6. RAG and Agents _ AI Engineering.pdf",
# "Chapter 2_ Title _ Book.pdf", "Appendix A_ Title _ Book.pdf", "Appendix. Title _ Book.pdf"
chapter_re = re.compile(
    r"^(?:(?:Chapter\s+)?(?P<num>\d+)|Appendix\s*(?P<app>[A-Z])?)\s*[._]\s*(?P<title>.+?)\s+_\s+(?P<book>.+?)\s*\.pdf$", re.I)
# a short, stable folder name per book; anything not listed gets its slugged title
BOOK_SLUGS = {
    "ai engineering": "huyen-ai-engineering",
    "ai systems performance engineering": "ai-systems-performance-engineering",
    "building applications with ai agents": "building-applications-with-ai-agents",
    "building ai agents with llms, rag, and knowledge graphs": "building-ai-agents-llms-rag-kgs",
    "context engineering for multi-agent systems": "context-engineering-multi-agent-systems",
    "ai agents with mcp": "ai-agents-with-mcp",
    "ai agents: the definitive guide": "ai-agents-definitive-guide",
}


def words_slug(text, n=6):
    words = [w for w in ascii_slug(text).split("-") if w and w not in STOPWORDS]
    return "-".join(words[:n])


def arxiv_authors(ids):
    """{id: (title, first author, year)} for many arXiv ids, 100 per API call."""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out, ids = {}, sorted(ids)
    for i in range(0, len(ids), 100):
        chunk = ids[i : i + 100]
        try:
            feed = ET.fromstring(http_get(ARXIV_API.format(id=",".join(chunk))))
        except Exception as exc:
            log(f"route: arXiv metadata failed for {len(chunk)} ids: {exc}")
            continue
        for entry in feed.findall("a:entry", ns):
            m = file_id_re.search(entry.findtext("a:id", "", ns))
            author = entry.findtext("a:author/a:name", "", ns).strip()
            if m and author:
                out[m.group(1)] = (" ".join(entry.findtext("a:title", "", ns).split()), author,
                                   entry.findtext("a:published", "", ns)[:4])
        time.sleep(3)
    return out


def route_name(r, meta):
    """File name (relative to the home's sources/) for a reading."""
    fname = Path(r["local_pdf"]).name
    m = chapter_re.match(fname)
    if m:
        book = m["book"].replace("_", ":").strip()
        folder = BOOK_SLUGS.get(book.lower()) or words_slug(book)
        title = words_slug(m["title"].replace("_", ":"))
        if m["num"]:
            return f"{folder}/ch{int(m['num']):02d}-{title}.pdf"
        return f"{folder}/appendix-{m['app'].lower() + '-' if m['app'] else ''}{title}.pdf"
    if r.get("slug"):
        return f"{r['slug']}.pdf"
    if r.get("arxiv") and r["arxiv"] in meta:
        title, author, year = meta[r["arxiv"]]
        r.update(arxiv_title=title, first_author=author, year=year)
    if r.get("arxiv") and r.get("first_author"):
        return f"{make_slug(r.get('arxiv_title') or r['title'], r['first_author'], r['year'])}.pdf"
    return f"{words_slug(r['title']) or ascii_slug(Path(fname).stem)}.pdf"


def git_mv(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if is_tracked(src.relative_to(REPO)):
        subprocess.run(["git", "mv", str(src), str(dest)], cwd=REPO, check=True, capture_output=True)
    else:
        shutil.move(src, dest)


def git_rm(path):
    if is_tracked(path.relative_to(REPO)):
        subprocess.run(["git", "rm", "-q", str(path)], cwd=REPO, check=True, capture_output=True)
    else:
        path.unlink()


def cmd_route(args):
    """Move every homed PDF under --from into its home's sources/; drop duplicate copies there."""
    rows = load_ledger()
    todo = [r for r in rows if r.get("pillar") and r["status"] != "skipped"
            and (r.get("local_pdf") or "").startswith(args.src) and (REPO / r["local_pdf"]).exists()]
    need = {r["arxiv"] for r in todo if r.get("arxiv") and not r.get("first_author")
            and not chapter_re.match(Path(r["local_pdf"]).name)}
    meta = arxiv_authors(need) if need else {}
    taken = {r["local_pdf"] for r in rows if r.get("local_pdf")}
    moved = dropped = 0
    for r in sorted(todo, key=lambda r: r["local_pdf"]):
        src = REPO / r["local_pdf"]
        dest = REPO / sources_rel(r["pillar"]) / route_name(r, meta)
        rel = str(dest.relative_to(REPO))
        if rel in taken and rel != r["local_pdf"]:  # name clash with a different reading
            dest = dest.with_name(f"{dest.stem}-{(r.get('arxiv') or r['key'][5:13])}.pdf")
            rel = str(dest.relative_to(REPO))
        print(f"{'mv' if args.apply else 'would mv'}  {r['local_pdf']}\n    -> {rel}")
        # duplicate copies inside the inbox go; copies elsewhere wait for /pillar
        extra = [c for c in r.get("copies") or [] if c.startswith(args.src) and (REPO / c).exists()]
        for c in extra:
            print(f"{'rm' if args.apply else 'would rm'}  {c}  (duplicate)")
        if not args.apply:
            continue
        git_mv(src, dest)
        for c in extra:
            git_rm(REPO / c)
            dropped += 1
        taken.discard(r["local_pdf"])
        taken.add(rel)
        r["local_pdf"] = rel
        r["copies"] = [c for c in r.get("copies") or [] if c not in extra] or None
        r["area"] = rel.split("/")[0]
        moved += 1
    if args.apply:
        save_ledger(rows)
    left = sum(1 for r in rows if (r.get("local_pdf") or "").startswith(args.src))
    log(f"route: {moved if args.apply else len(todo)} {'moved' if args.apply else 'to move'}, "
        f"{dropped} duplicates removed; {left} PDFs left under {args.src}"
        + ("" if args.apply else " (dry run; --apply to move)"))


# --- status / mark ----------------------------------------------------------


def cmd_status(args):
    rows = load_ledger()
    if args.list:
        for r in rows:
            if r["status"] == args.list:
                print(json.dumps({**{k: r.get(k) for k in ("key", "title", "topic", "pillar", "note", "relevance")},
                                  "pdf": r.get("local_pdf"), **{k: r.get(k) for k in ("reason", "url")}}, ensure_ascii=False))
        return
    print(f"ledger: {LEDGER.relative_to(REPO)} ({len(rows)} papers, {sum(bool(r.get('have_pdf')) for r in rows)} with a PDF in the repo)")
    inbox = sum(1 for r in rows if (r.get("local_pdf") or "").startswith(INBOX))
    print(f"inbox: {inbox} PDFs still in {INBOX} (`route` files the triaged ones)")
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
        if name == "triage":
            p.add_argument("--status", default="new", help="re-triage rows with this status (default new)")
            p.add_argument("--source", choices=["dair", "repo"], help="only rows from this source")
        if name in ("triage", "download"):
            p.add_argument("--backlog", action="store_true", help="include backfilled papers")
        else:
            p.set_defaults(backlog=False)
        if name == "run":
            p.set_defaults(status="new", source=None)
    p = sub.add_parser("scan")
    p.add_argument("--deep", action="store_true", help="also read the arXiv stamp inside each PDF (needs pypdf)")
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("route")
    p.add_argument("--from", dest="src", default=INBOX, help=f"move PDFs found under this prefix (default {INBOX})")
    p.add_argument("--apply", action="store_true", help="move the files (default: dry run)")
    p.set_defaults(fn=cmd_route)
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
