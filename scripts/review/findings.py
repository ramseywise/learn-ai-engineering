#!/usr/bin/env python3
"""The reviewer findings log: what reviewers reported and what was decided about it.

    python3 scripts/review/findings.py add < findings.jsonl     # one JSON object per line, all or nothing
    python3 scripts/review/findings.py decide <id> applied|rejected --reason "why"
    python3 scripts/review/findings.py promote <pattern> --to "scripts/check_chapters.py"
    python3 scripts/review/findings.py report
    python3 scripts/review/findings.py patterns

Append-only JSONL, so the latest row for an id is its current state. Required fields for add: run, reviewer,
target, kind, decision, summary. Optional: line, pattern. A rejection needs a reason. `pattern` is a short slug
naming a fault a script or spec could prevent (`preprint-missing`); run `patterns` and reuse one if it fits.

Precision is applied / (applied + rejected), per reviewer. `listed` findings await the user and count for neither.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

LOG = Path(__file__).resolve().parent / "findings.jsonl"
DECISIONS = {"applied", "listed", "rejected"}
REQUIRED = ("run", "reviewer", "target", "kind", "decision", "summary")
MIN_SAMPLE = 20  # Below this a precision figure is an anecdote, so the report says so
PROMOTE_AT = 3  # Applied this many times, across at least two files, a pattern is a promotion candidate


def finding_id(row: dict) -> str:
    key = "|".join(str(row[k]) for k in ("reviewer", "target", "kind", "summary"))
    return hashlib.sha1(key.encode()).hexdigest()[:8]


def validate(row: dict) -> str | None:
    missing = [k for k in REQUIRED if not row.get(k)]
    if missing:
        return f"missing {', '.join(missing)}"
    if row["decision"] not in DECISIONS:
        return f"decision must be one of {sorted(DECISIONS)}, got {row['decision']!r}"
    if row["decision"] == "rejected" and not row.get("reason"):
        return "a rejected finding needs a reason"
    return None


def read_rows(log: Path) -> list[dict]:
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(log: Path, rows: list[dict]) -> None:
    with log.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def current(rows: list[dict]) -> dict[str, dict]:
    """The latest state of each finding, merging later decisions into the original row."""
    state: dict[str, dict] = {}
    for row in rows:
        if row.get("type") == "promotion":
            continue
        state.setdefault(row["id"], {}).update(row)
    return state


def promoted(rows: list[dict]) -> dict[str, str]:
    return {r["pattern"]: r["to"] for r in rows if r.get("type") == "promotion"}


def add(log: Path, lines: list[str], today: str) -> list[str]:
    rows = []
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row = json.loads(line)
        problem = validate(row)
        if problem:
            raise ValueError(f"line {n}: {problem}")
        rows.append({"ts": today, "id": finding_id(row), **row})
    append(log, rows)
    return [r["id"] for r in rows]


def decide(log: Path, finding: str, decision: str, reason: str, today: str) -> None:
    if finding not in current(read_rows(log)):
        raise ValueError(f"no finding {finding}")
    if decision == "rejected" and not reason:
        raise ValueError("a rejected finding needs a reason")
    append(log, [{"ts": today, "id": finding, "decision": decision, **({"reason": reason} if reason else {})}])


def precision(findings: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = defaultdict(lambda: Counter())
    for f in findings:
        out[f["reviewer"]][f["decision"]] += 1
    return {k: dict(v) for k, v in out.items()}


def candidates(rows: list[dict]) -> list[tuple[str, int, int]]:
    """(pattern, times applied, files) for unpromoted patterns at the threshold, most frequent first."""
    done = promoted(rows)
    applied = [f for f in current(rows).values() if f.get("pattern") and f["decision"] == "applied"]
    found = []
    for pattern in {f["pattern"] for f in applied} - set(done):
        mine = [f for f in applied if f["pattern"] == pattern]
        files = len({f["target"] for f in mine})
        if len(mine) >= PROMOTE_AT and files >= 2:
            found.append((pattern, len(mine), files))
    return sorted(found, key=lambda c: -c[1])


def report_lines(rows: list[dict]) -> list[str]:
    findings = list(current(rows).values())
    if not findings:
        return ["No findings logged yet."]
    lines = [f"{len(findings)} findings from {len({f['run'] for f in findings})} runs", "", "PRECISION"]
    for reviewer, c in sorted(precision(findings).items()):
        applied, rejected = c.get("applied", 0), c.get("rejected", 0)
        decided = applied + rejected
        rate = f"{applied / decided:.0%}" if decided else "n/a"
        note = "" if decided >= MIN_SAMPLE else f" (only {decided} decided, under {MIN_SAMPLE}: not a rate yet)"
        lines.append(f"  {reviewer}: {rate}, {applied} applied, {rejected} rejected, {c.get('listed', 0)} open{note}")
    lines += ["", "PROMOTION CANDIDATES (propose a script check or spec change)"]
    lines += [f"  {p}: applied {n} times in {files} files" for p, n, files in candidates(rows)] or ["  none"]
    lines += ["", "OPEN (listed, waiting for a decision)"]
    still_open = [f for f in findings if f["decision"] == "listed"]
    lines += [f"  {f['id']} {f['reviewer']} {f['target']}: {f['summary']}" for f in still_open] or ["  none"]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=LOG)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("add")
    decide_parser = commands.add_parser("decide")
    decide_parser.add_argument("id")
    decide_parser.add_argument("decision", choices=["applied", "rejected"])
    decide_parser.add_argument("--reason", default="")
    promote_parser = commands.add_parser("promote")
    promote_parser.add_argument("pattern")
    promote_parser.add_argument("--to", required=True, help="the script or spec that now prevents it")
    commands.add_parser("report")
    commands.add_parser("patterns")
    args = parser.parse_args()
    today = date.today().isoformat()
    try:
        if args.command == "add":
            print("\n".join(add(args.log, sys.stdin.readlines(), today)))
        elif args.command == "decide":
            decide(args.log, args.id, args.decision, args.reason, today)
        elif args.command == "promote":
            append(args.log, [{"ts": today, "type": "promotion", "pattern": args.pattern, "to": args.to}])
        elif args.command == "report":
            print("\n".join(report_lines(read_rows(args.log))))
        elif args.command == "patterns":
            counts = Counter(f["pattern"] for f in current(read_rows(args.log)).values() if f.get("pattern"))
            print("\n".join(f"{n:>4}  {p}" for p, n in counts.most_common()))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
