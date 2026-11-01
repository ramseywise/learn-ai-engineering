#!/usr/bin/env python3
"""Check notes against the chapter standard in ai-engineering/PILLAR-LAYOUT.md.

    python3 scripts/check_chapters.py data-analytics/06-applied-analyses [more paths] [--strict]

A path is a pillar folder or a single note. Prints one line per shortfall. --strict exits 1 on any.
Notes marked `status: skeleton` in frontmatter are reported as skeletons, not failed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MIN_WORDS, MAX_WORDS = 1500, 7000
SECTIONS = [("Pitfalls", r"pitfall"), ("Try it", r"try it"), ("Interview checklist", r"interview"), ("Next", r"next\b")]
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
FIGURE = re.compile(r"!\[[^\]]*\]\(|<img\s|^```(mermaid|text|ascii)\b", re.M)


def check(note: Path) -> list[str]:
    text = note.read_text(encoding="utf-8")
    front = ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        front, text = text[:end], text[end + 4:]
    if re.search(r"^status:\s*skeleton", front, re.M):
        return ["skeleton (status: skeleton)"]
    problems = []
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any shortfall")
    args = ap.parse_args()
    notes: list[Path] = []
    for path in args.paths:
        notes += [path] if path.is_file() else sorted((path / "notes").glob("*.md"))
    bad = 0
    for note in notes:
        problems = check(note)
        for problem in problems:
            print(f"{note}: {problem}")
        bad += bool(problems)
    print(f"{len(notes) - bad} of {len(notes)} notes meet the chapter standard")
    if bad and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
