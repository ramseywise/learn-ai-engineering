#!/usr/bin/env python3
"""Check what can be computed about practice material: python3 scripts/practice/check_drills.py [path ...]

Reads only files git would track, as crosswalk.py does. Exit 1 on any problem. Checks:
- a schema drill (a drills/ Markdown file with `track:` in its frontmatter, see programming/drills/README.md) has
  valid required fields, no H1, the required sections in order, and its solution inside <details>;
- every tracked .py file parses (seeded-bug and stub files are meant to fail when run, so nothing is run);
- every tracked .sql seed loads into an in-memory SQLite database.

Whether the answer is right is a judgement for the drill-reviewer agent, not this script.
"""
from __future__ import annotations

import argparse
import ast
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKS = {"python", "sql", "typescript", "terraform", "tooling", "coding"}
DIFFICULTIES = {"easy", "medium", "hard"}
REQUIRED = ("title", "track", "topic", "difficulty", "timebox_min", "concepts", "source")
SECTIONS = ("Prompt", "Starter", "Tests")
FENCE = re.compile(r"^\s*```.*?^\s*```", re.S | re.M)


def fields(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return dict(m.groups() for m in re.finditer(r"^([a-z_]+):[ \t]*(.*)$", text[4:end], re.M))


def check_drill(text: str) -> list[str]:
    """Problems in one schema drill. Files with no `track:` aren't schema drills and return nothing."""
    meta = fields(text)
    if not meta or "track" not in meta:
        return []
    problems = [f"missing frontmatter field: {k}" for k in REQUIRED if k not in meta]
    if meta["track"].strip() not in TRACKS:
        problems.append(f"unknown track: {meta['track']}")
    if "difficulty" in meta and meta["difficulty"].strip() not in DIFFICULTIES:
        problems.append(f"unknown difficulty: {meta['difficulty']}")
    if "timebox_min" in meta and not meta["timebox_min"].strip().isdigit():
        problems.append(f"timebox_min is not a whole number: {meta['timebox_min']}")
    body = FENCE.sub("", text[text.find("\n---", 4) + 4 :])
    if re.search(r"^# ", body, re.M):
        problems.append("H1 in the body: the title lives in frontmatter")
    headings = re.findall(r"^## +(.+?)\s*$", body, re.M)
    positions = []
    for section in SECTIONS:
        if section in headings:
            positions.append(headings.index(section))
        else:
            problems.append(f"no '## {section}' section")
    if positions != sorted(positions):
        problems.append(f"sections out of order: expected {', '.join(SECTIONS)}")
    if not re.search(r"<summary>\s*Solution", body, re.I):
        problems.append("no solution inside a <details> block")
    return problems


def check_python(text: str) -> list[str]:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        return [f"does not parse: line {exc.lineno}: {exc.msg}"]
    return []


def check_sql(text: str) -> list[str]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(text)
    except sqlite3.Error as exc:
        return [f"does not load in SQLite: {exc}"]
    finally:
        connection.close()
    return []


def published(paths: list[str]) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-co", "--exclude-standard", "--", *paths],
        check=True, capture_output=True, text=True,
    )
    return sorted(set(out.stdout.splitlines()))


def check_file(path: str, text: str) -> list[str]:
    if path.endswith(".py"):
        return check_python(text)
    if path.endswith(".sql"):
        return check_sql(text)
    if path.endswith(".md") and "/drills/" in f"/{path}":
        return check_drill(text)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", default=["programming/drills/", "practice/"])
    args = parser.parse_args()
    files = problems = 0
    for path in published(args.paths):
        target = ROOT / path
        if target.suffix not in {".py", ".sql", ".md"} or not target.is_file():
            continue
        files += 1
        for problem in check_file(path, target.read_text(encoding="utf-8", errors="replace")):
            print(f"{path}: {problem}")
            problems += 1
    print(f"drill-check: {files} files, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
