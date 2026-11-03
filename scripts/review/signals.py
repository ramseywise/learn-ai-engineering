#!/usr/bin/env python3
"""Collect what learners and reviewers show about the coursework into one list to look at.

    python3 scripts/review/signals.py             # print
    python3 scripts/review/signals.py --write     # also write .claude/docs/signals/<date>.md (gitignored)

Reads, and never changes:
- librarian's logs/flashcards.jsonl: self-graded cards ($LIBRARIAN_DIR, default ../librarian)
- librarian's logs/retrieval.jsonl: real wiki searches that found nothing. Eval and sweep rows are ignored
- sisyphus's drills/coding/drill-log.md: the Date, QID, Aid and Score columns, never the Note ($SISYPHUS_DIR)
- scripts/review/findings.jsonl: open decisions and recurring faults

The output proposes what to re-read. With one learner a missed card can mean a topic not learned yet rather than a bad
card, so nothing here is evidence that content is wrong. The output holds personal history, so keep it out of tracked files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import findings as fl

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
SOURCE_PREFIX = "learn-ai-engineering/"
MIN_CARD_ATTEMPTS = 3  # Fewer than this says nothing about one card
MISS_RATE = 0.5
STRUGGLE_AID = 2  # Hint rung from which a drill counts as needing help


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def deck_location(root: Path, source: str, deck: str, front: str) -> str:
    """`<pillar>/slides/deck.yaml:<line>` for the slide this card came from, or "" if it can't be found."""
    note = source.removeprefix(SOURCE_PREFIX)
    pillar = note.split("/notes/")[0] if "/notes/" in note else deck
    path = root / pillar / "slides" / "deck.yaml"
    if not path.exists():
        return ""
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"\s*(- )?(title|recall):", line) and front in line:
            return f"{pillar}/slides/deck.yaml:{n}"
    return ""


def flashcard_section(rows: list[dict], root: Path) -> list[str]:
    cards: dict[tuple[str, str], Counter] = defaultdict(Counter)
    source: dict[tuple[str, str], str] = {}
    for row in rows:
        key = (row.get("deck", ""), row.get("front", ""))
        cards[key][row.get("result", "")] += 1
        source[key] = row.get("source", "")
    flagged = []
    for key, counts in cards.items():
        total = counts["knew"] + counts["missed"]
        if total >= MIN_CARD_ATTEMPTS and counts["missed"] / total >= MISS_RATE:
            flagged.append((counts["missed"] / total, total, key))
    lines = [f"{len(rows)} grades on {len(cards)} cards. Flagged at {MIN_CARD_ATTEMPTS}+ attempts and {MISS_RATE:.0%}+ missed."]
    for rate, total, (deck, front) in sorted(flagged, key=lambda f: (-f[0], -f[1])):
        where = deck_location(root, source[(deck, front)], deck, front) or source[(deck, front)] or deck
        lines.append(f"- {rate:.0%} missed of {total}: \"{front}\" ({where})")
    return lines


def parse_drill_log(text: str) -> list[dict]:
    """Rows of the log's table, keeping only date, qid, aid and score. Note text is dropped here."""
    rows, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if "QID" in cells:
                header = cells
            continue
        if set(cells[0]) <= {"-", ":"} or len(cells) < len(header):
            continue
        row = dict(zip(header, cells))
        rows.append({"date": row.get("Date", ""), "qid": row.get("QID", ""), "aid": row.get("Aid", ""), "score": row.get("Score", "")})
    return rows


def drill_files(root: Path) -> dict[str, str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "programming/drills"],
                         capture_output=True, text=True)
    return {Path(p).stem: p for p in out.stdout.splitlines() if p.endswith((".md", ".py"))}


def drill_section(rows: list[dict], files: dict[str, str]) -> list[str]:
    by_qid: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_qid[row["qid"]].append(row)
    flagged = []
    for qid, attempts in by_qid.items():
        last = attempts[-1]
        misses, marks = last["score"].count("✗"), last["score"].count("✓") + last["score"].count("✗")
        aid = int(last["aid"]) if last["aid"].isdigit() else 0
        if aid >= STRUGGLE_AID or (marks and misses / marks >= MISS_RATE):
            flagged.append((misses, aid, qid, len(attempts), last["score"]))
    matched = sum(1 for q in by_qid if q in files)
    lines = [f"{len(rows)} attempts on {len(by_qid)} drills; {matched} match a drill file here by slug. "
             f"Flagged on the latest attempt at hint rung {STRUGGLE_AID}+ or half the marks missed."]
    for _, aid, qid, n, score in sorted(flagged, reverse=True):
        lines.append(f"- {qid}: {n} attempt(s), hint rung {aid}, {score} ({files.get(qid, 'no drill file here')})")
    return lines


def search_section(rows: list[dict]) -> list[str]:
    real = [r for r in rows if r.get("tool") == "search_wiki" and r.get("query")]
    empty = Counter(r["query"] for r in real if not r.get("n_results"))
    lines = [f"{len(real)} real wiki searches, {sum(empty.values())} found nothing. {len(rows) - len(real)} other rows ignored."]
    lines += [f"- {n}x \"{q}\"" for q, n in empty.most_common(15)]
    return lines


def build(root: Path, librarian: Path, sisyphus: Path, findings_log: Path) -> str:
    drill_log = sisyphus / "drills" / "coding" / "drill-log.md"
    drills = parse_drill_log(drill_log.read_text(encoding="utf-8")) if drill_log.exists() else []
    parts = [f"# Coursework signals, {date.today().isoformat()}", "",
             "Proposals to re-read, not evidence that content is wrong. One learner can miss a card simply by not "
             "having learned the topic yet.", "",
             "## Flashcards", *flashcard_section(read_jsonl(librarian / "logs" / "flashcards.jsonl"), root), "",
             "## Drills", *drill_section(drills, drill_files(root)), "",
             "## Wiki searches", *search_section(read_jsonl(librarian / "logs" / "retrieval.jsonl")), "",
             "## Reviewers", *fl.report_lines(fl.read_rows(findings_log)), ""]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    librarian = Path(os.environ.get("LIBRARIAN_DIR", WORKSPACE / "librarian"))
    sisyphus = Path(os.environ.get("SISYPHUS_DIR", WORKSPACE / "sisyphus"))
    text = build(ROOT, librarian, sisyphus, fl.LOG)
    print(text)
    if args.write:
        out = ROOT / ".claude" / "docs" / "signals" / f"{date.today().isoformat()}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
