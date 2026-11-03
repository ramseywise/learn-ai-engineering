#!/usr/bin/env python3
"""Check notes against the chapter standard in .claude/skills/pillar/references/pillar-layout.md.

    python3 scripts/check_chapters.py data-analytics/06-applied-analyses [more paths] [--strict]

A path is a pillar folder or a single note. Prints one line per shortfall. --strict exits 1 on any.
Notes marked `status: skeleton` in frontmatter are reported as skeletons, not failed, but their metadata is checked.
A pillar folder whose README has neither a Builds on nor a Feeds into table gets a warning line. A
warning never counts as a shortfall, so it does not change the summary or the --strict exit code.

Metadata rules, which count as shortfalls and apply everywhere the chapter shape does:
- `origin` is one of LEGAL_ORIGINS;
- each `sources` entry holds a URL or DOI, a repo path that exists, or a dated citation in the layout's form
  ("Huyen, AI Engineering (O'Reilly, 2025), ch. 6"), is a plain string, and names no local PDF;
- no `~/.claude/`, `~/workspace/` or `/Users/` anywhere in the file, code fences and frontmatter included;
- the checklist heading is exactly `## Interview checklist`;
- every arXiv id and DOI the body links is in `sources`.

--metadata-only applies those rules and skips the chapter shape, for programming/ modules the layout exempts from it.

--advisory prints what is reported and not gated: Interview checklist rows under one per ADVISORY_WORDS_PER_ROW words,
body links other than papers that `sources` does not name, and `sources` URLs the body never cites.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

MIN_WORDS, MAX_WORDS = 1500, 7000
SECTIONS = [("Pitfalls", r"pitfall"), ("Try it", r"try it"), ("Interview checklist", r"interview"), ("Next", r"next\b")]
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
FIGURE = re.compile(r"!\[[^\]]*\]\(|<img\s|^```(mermaid|text|ascii)\b", re.M)
LINK_TABLE = re.compile(r"^(?:#+ +|\*\*)(?:Builds on|Feeds into)\b[^\n]*\n+\|", re.M | re.I)
PILLARED = {"ai-engineering", "generative-ai", "data-analytics", "data-science", "data-engineering"}
LEGAL_ORIGINS = {"synthesis", "book-condensed", "web-authored", "curated"}
CHECKLIST_HEADING = "Interview checklist"
ADVISORY_WORDS_PER_ROW = 500
ROOT = Path(__file__).resolve().parents[1]
PERSONAL_PATH = re.compile(r"~/\.claude\b|~/workspace\b|/Users/")
URL = re.compile(r"https?://[^\s)\]>\"'`]+")
DOI = re.compile(r"\b10\.\d{4,9}/(?:[^\s()\]>\"'`,;]|\([^\s()]*\))+", re.I)
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", re.I)
LOCAL_PDF = re.compile(r"\.pdf\b", re.I)
YEAR = re.compile(r"\b(?:19|20)\d\d\b")


def split_front(text: str) -> tuple[str, str]:
    """(frontmatter, body). The frontmatter is empty when the file has none."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[3:end], text[end + 4:]
    return "", text


def origin_of(front: str) -> str | None:
    match = re.search(r"^origin:[ \t]*(.*)$", front, re.M)
    if not match:
        return None
    return re.sub(r"\s+#.*$", "", match.group(1)).strip().strip("'\"")


def sources_of(front: str) -> list[str]:
    """The raw `sources` entries, quotes included. A continuation line belongs to the entry above it; a YAML comment
    is no entry."""
    lines = front.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"sources:", line):
            continue
        rest = line[len("sources:"):].strip()
        if rest:
            return [e.strip() for e in rest.strip("[]").split(",") if e.strip()]
        entries: list[str] = []
        for item in lines[i + 1:]:
            if item.strip().startswith("#"):
                continue
            if re.match(r"\s*- ", item) or item.strip() == "-":
                entries.append(item.strip()[1:].strip())
            elif item.startswith(" ") and entries:
                entries[-1] += " " + item.strip()
            elif item.strip():
                break
        return entries
    return []


def source_problem(entry: str, note: Path) -> str | None:
    """Why one `sources` entry is illegal, or None."""
    plain = entry
    if plain[:1] in "'\"":
        plain = plain.strip("'\"")
    elif ": " in plain:
        return f"source is not a plain string, quote it: {entry}"
    bare = URL.sub("", plain)
    if LOCAL_PDF.search(bare):
        return f"source names a local PDF, use the public URL or a citation: {entry}"
    if URL.search(plain) or DOI.search(plain):
        return None
    path = re.split(r"\s+\(", plain, maxsplit=1)[0].strip()
    first = path.split()[0] if path else ""
    if "/" in first or re.search(r"\.\w{1,8}$", first):
        bases = (note.parent, note.parent.parent, ROOT)
        found = any((base / path).exists() for base in bases)
        return None if found else f"source path does not exist: {entry}"
    if YEAR.search(plain) and "," in plain:
        return None
    return f"source is not a URL, DOI, repo path or dated citation: {entry}"


def paper_ids(text: str) -> set[str]:
    """arXiv ids and DOIs in text, lower-cased with trailing punctuation dropped."""
    return {m.lower() for m in ARXIV.findall(text)} | {m.rstrip(".").lower() for m in DOI.findall(text)}


def metadata_problems(text: str, note: Path) -> list[str]:
    front, body = split_front(text)
    problems = []
    origin = origin_of(front)
    if origin is None:
        problems.append("no origin in frontmatter")
    elif origin not in LEGAL_ORIGINS:
        problems.append(f"origin {origin!r} is not one of {', '.join(sorted(LEGAL_ORIGINS))}")
    problems += [p for p in (source_problem(e, note) for e in sources_of(front)) if p]
    for match in sorted(set(PERSONAL_PATH.findall(text))):
        problems.append(f"personal path {match} in a tracked note")
    prose = FENCE.sub("", body)
    variants = [h for h in re.findall(r"^##+ +(.+?)\s*$", prose, re.M)
                if re.search(r"interview", h, re.I) and h != CHECKLIST_HEADING]
    problems += [f"heading '{h}' must be '## {CHECKLIST_HEADING}'" for h in variants]
    if re.search(rf"^###+ +{CHECKLIST_HEADING}\s*$", prose, re.M):
        problems.append(f"'{CHECKLIST_HEADING}' must be an H2")
    for paper in sorted(paper_ids(prose) - paper_ids(front)):
        problems.append(f"body cites {paper}, not in frontmatter sources")
    return problems


def checklist_rows(body: str) -> int:
    """Answer rows in the Interview checklist table: its table lines minus header and separator."""
    match = re.search(rf"^## {CHECKLIST_HEADING}\s*$(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not match:
        return 0
    return max(0, sum(line.startswith("|") for line in match.group(1).splitlines()) - 2)


def advisories(text: str) -> list[str]:
    """What is reported and not gated."""
    front, body = split_front(text)
    prose = FENCE.sub("", body)
    out = []
    words, rows = len(body.split()), checklist_rows(body)
    if rows < words // ADVISORY_WORDS_PER_ROW:
        out.append(f"checklist floor: {rows} rows for {words} words, floor {words // ADVISORY_WORDS_PER_ROW}")
    clean = lambda found: {u.rstrip(".,;") for u in found}
    body_urls, front_urls = clean(URL.findall(prose)), clean(URL.findall(front))
    out += [f"body link not in sources: {u}" for u in sorted(body_urls - front_urls) if not paper_ids(u)]
    out += [f"source never cited in the body: {u}" for u in sorted(front_urls - body_urls)
            if not (paper_ids(u) & paper_ids(prose))]
    return out


def check(note: Path, metadata_only: bool = False) -> list[str]:
    raw = note.read_text(encoding="utf-8")
    meta = metadata_problems(raw, note)
    if metadata_only:
        return meta
    front, text = split_front(raw)
    if re.search(r"^status:\s*skeleton", front, re.M):
        return ["skeleton (status: skeleton)", *meta]
    problems = meta
    words = len(text.split())
    if words < MIN_WORDS:
        problems.append(f"{words} words, under {MIN_WORDS}")
    if words > MAX_WORDS:
        problems.append(f"{words} words, over {MAX_WORDS}: split it")
    if not FIGURE.search(text):
        problems.append("no figure or diagram")
    if "```" not in text:
        problems.append("no code block")
    prose = FENCE.sub("", text)
    first_h2 = re.search(r"^## ", prose, re.M)
    head = prose[: first_h2.start()] if first_h2 else prose
    if len(re.sub(r"^#.*$", "", head, flags=re.M).split()) < 25:
        problems.append("no hook paragraph before the first H2")
    headings = [h.lower() for h in re.findall(r"^##+ +(.+)$", prose, re.M)]
    for label, pattern in SECTIONS:
        if not any(re.search(pattern, h) for h in headings):
            problems.append(f"no '{label}' section")
    order = [next((i for i, h in enumerate(headings) if re.search(p, h)), None) for _, p in SECTIONS]
    found = [i for i in order if i is not None]
    if found != sorted(found):
        problems.append("Pitfalls, Try it, Interview checklist and Next are out of order")
    return problems


def missing_link_tables(pillar: Path) -> Path | None:
    """The pillar's README, if it is in a pillared area and has neither table."""
    readme = pillar / "README.md"
    if PILLARED.isdisjoint(pillar.resolve().parts) or not readme.is_file():
        return None
    return None if LINK_TABLE.search(readme.read_text(encoding="utf-8")) else readme


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any shortfall")
    ap.add_argument("--metadata-only", action="store_true", help="skip the chapter shape, keep the metadata rules")
    ap.add_argument("--advisory", action="store_true", help="print what is reported and not gated, then exit 0")
    args = ap.parse_args()
    notes: list[Path] = []
    for path in args.paths:
        notes += [path] if path.is_file() else sorted((path / "notes").glob("*.md"))
    if args.advisory:
        counts: Counter[str] = Counter()
        for note in notes:
            for line in advisories(note.read_text(encoding="utf-8")):
                print(f"{note}: {line}")
                counts[line.split(":")[0]] += 1
        print("advisory, not gated: " + (", ".join(f"{n} {k}" for k, n in sorted(counts.items())) or "none"))
        return
    for path in args.paths:
        readme = None if path.is_file() else missing_link_tables(path)
        if readme:
            print(f"warning: {readme}: no Builds on or Feeds into table")
    bad = 0
    for note in notes:
        problems = check(note, args.metadata_only)
        for problem in problems:
            print(f"{note}: {problem}")
        bad += bool(problems)
    standard = "the metadata rules" if args.metadata_only else "the chapter standard"
    print(f"{len(notes) - bad} of {len(notes)} notes meet {standard}")
    if bad and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
