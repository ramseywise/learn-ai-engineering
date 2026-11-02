#!/usr/bin/env python3
"""Build the curriculum map: every note, how it connects, and where the connections have broken.

The map is generated from the repo on every run, so it cannot drift from the notes. It answers the
structural questions; the curriculum-steward agent answers the ones that need reading.

    python3 scripts/curriculum_map.py build                 write the JSON map, print a summary
    python3 scripts/curriculum_map.py issues [--pillar P] [--kind K] [--strict]
    python3 scripts/curriculum_map.py find "positional encoding"     where a topic already lives
    python3 scripts/curriculum_map.py note <path>           one note's neighbours

Issue kinds, most actionable first:
    missing_next_target  a note's ## Next links to a file that does not exist
    next_out_of_order    a note's ## Next skips or misses the following note in its pillar
    not_in_readme        the pillar README never links to this note
    deck_stale_source    a deck slide's source: names a note that does not exist
    deck_gap             the pillar has a deck, and no slide cites this note
    ledger_stale_note    a ledger row maps a reading to a note that does not exist
    duplicate_number     two notes in a pillar share a number
    number_gap           a pillar's note numbers skip a value
    no_inbound           no other note links here (information: a first note often has none)
    no_cross_links       the pillar README has neither a Builds on nor a Feeds into table
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

SUBJECTS = ("programming", "data-analytics", "data-engineering", "data-science", "generative-ai", "ai-engineering")
SKIP_PARTS = {"practice", "sources", "slides", "checkpoints", "__pycache__", ".ipynb_checkpoints"}
MAP_PATH = ".claude/docs/curriculum-map.json"
INFO_KINDS = {"no_inbound"}

FENCE = re.compile(r"^```.*?^```", re.S | re.M)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
H1 = re.compile(r"^# +(.+)$", re.M)
H2 = re.compile(r"^## +(.+)$", re.M)
NEXT = re.compile(r"^## +Next\b[^\n]*\n(.*?)(?=^## |\Z)", re.S | re.M)
NUMBER = re.compile(r"^(\d+)([a-z]?)[-_.]")  # 13b is a deliberate second note beside 13
CROSS = re.compile(r"^(?:#+ +|\*\*)(?:Builds on|Feeds into)\b", re.M | re.I)
DECK_SOURCE = re.compile(r"""\bsource:\s*["']?([^"'\s#,}]+\.md)""")  # block or inline {source: x, ...}
WORD = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
STOPWORDS = {"a", "an", "in", "of", "on", "to", "the", "and", "for", "with", "from", "into", "that", "this", "what", "how", "why", "are"}


def split_front(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def front_value(front: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*(.+?)\s*(?:#.*)?$", front, re.M)
    return match.group(1).strip("\"'") if match else None


def links_from(text: str, source: Path, root: Path) -> set[str]:
    """Repo-relative paths of the local files a markdown text links to, code fences excluded."""
    found = set()
    for target in LINK.findall(FENCE.sub("", text)):
        if "://" in target or target.startswith(("/", "mailto:")):
            continue
        resolved = (source.parent / unquote(target)).resolve()
        try:
            found.add(resolved.relative_to(root).as_posix())
        except ValueError:
            pass  # a link that climbs out of the repo is link_check's concern
    return found


def find_notes(root: Path) -> list[Path]:
    notes = []
    for subject in SUBJECTS:
        for path in sorted((root / subject).rglob("*.md")) if (root / subject).is_dir() else []:
            parts = path.relative_to(root).parts
            if path.parent.name == "notes" and not SKIP_PARTS.intersection(parts):
                notes.append(path)
    return notes


def read_note(path: Path, root: Path) -> dict:
    front, body = split_front(path.read_text(encoding="utf-8"))
    prose = FENCE.sub("", body)
    title = H1.search(prose)
    next_section = NEXT.search(prose)
    number = NUMBER.match(path.name)
    return {
        "path": path.relative_to(root).as_posix(),
        "pillar": path.parent.parent.relative_to(root).as_posix(),
        "subject": path.relative_to(root).parts[0],
        "number": int(number.group(1)) if number else None,
        "suffix": number.group(2) if number else "",
        "title": title.group(1).strip() if title else path.stem,
        "words": len(body.split()),
        "status": front_value(front, "status"),
        "origin": front_value(front, "origin"),
        "confidence": front_value(front, "confidence"),
        "headings": [h.strip() for h in H2.findall(prose)],
        "links": sorted(links_from(body, path, root)),
        "next": sorted(links_from(next_section.group(1), path, root)) if next_section else None,
        "inbound": [],
    }


def build(root: Path) -> dict:
    root = root.resolve()
    notes = {}
    for path in find_notes(root):
        note = read_note(path, root)
        notes[note["path"]] = note

    pillars: dict[str, dict] = {}
    for note in notes.values():
        pillars.setdefault(note["pillar"], {"path": note["pillar"], "subject": note["subject"], "notes": []})
        pillars[note["pillar"]]["notes"].append(note["path"])
        for target in note["links"]:
            if target in notes and target != note["path"]:
                notes[target]["inbound"].append(note["path"])

    issues: list[dict] = []

    def add(kind: str, path: str, detail: str) -> None:
        pillar = next((p for p in sorted(pillars, key=len, reverse=True) if path == p or path.startswith(p + "/")), None)
        issues.append({"kind": kind, "path": path, "pillar": pillar, "detail": detail})

    for name, pillar in sorted(pillars.items()):
        members = sorted(pillar["notes"])
        # A programming module is listed by its track's README, one level up, and has no chapter tables.
        exempt = pillar["subject"] == "programming"
        readme = root / name / "README.md"
        if exempt and not readme.is_file():
            readme = root / name / ".." / "README.md"
        readme_links: set[str] = set()
        if readme.is_file():
            readme_text = readme.read_text(encoding="utf-8")
            readme_links = links_from(readme_text, readme, root)
            pillar["has_cross_links"] = bool(CROSS.search(FENCE.sub("", readme_text)))
            if not pillar["has_cross_links"] and not exempt:
                add("no_cross_links", f"{name}/README.md", "no Builds on or Feeds into table")
        else:
            pillar["has_cross_links"] = False
            add("no_cross_links", f"{name}/README.md", "the pillar has no README")

        for path in members:
            if readme.is_file() and path not in readme_links:
                add("not_in_readme", path, f"{readme.resolve().relative_to(root).as_posix()} does not link to it")

        labels = [(notes[p]["number"], notes[p]["suffix"]) for p in members if notes[p]["number"] is not None]
        for (number, suffix), count in sorted(Counter(labels).items()):
            if count > 1:
                add("duplicate_number", name, f"note number {number:02d}{suffix} is used {count} times")
        numbers = sorted({number for number, _ in labels})
        for low, high in zip(numbers, numbers[1:]):
            if high - low > 1:
                span = f"{low + 1:02d}" if high - low == 2 else f"{low + 1:02d} to {high - 1:02d}"
                add("number_gap", name, f"no note numbered {span}")

        ordered = sorted(
            (p for p in members if notes[p]["number"] is not None),
            key=lambda p: (notes[p]["number"], notes[p]["suffix"], p),
        )
        for index, path in enumerate(ordered):
            targets = notes[path]["next"]
            if targets is None:
                continue
            for target in targets:
                if not (root / target).exists():
                    add("missing_next_target", path, f"## Next links to {target}, which does not exist")
            if index + 1 < len(ordered) and ordered[index + 1] not in targets:
                add("next_out_of_order", path, f"## Next does not link to {ordered[index + 1]}")

        deck = root / name / "slides" / "deck.yaml"
        pillar["has_deck"] = deck.is_file()
        if deck.is_file():
            cited = set()
            for source in DECK_SOURCE.findall(deck.read_text(encoding="utf-8")):
                resolved = (root / name / source).resolve()
                if not resolved.exists():
                    add("deck_stale_source", f"{name}/slides/deck.yaml", f"source: {source} does not exist")
                else:
                    cited.add(resolved.relative_to(root).as_posix())
            for path in members:
                if path not in cited:
                    add("deck_gap", path, f"no slide in {name}/slides/deck.yaml cites it")

    ledger = root / "scripts/papers/ledger.jsonl"
    if ledger.is_file():
        stale = Counter()
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                note = json.loads(line).get("note")
                if note and not (root / note).exists():
                    stale[note] += 1
        for note, count in sorted(stale.items()):
            add("ledger_stale_note", note, f"{count} ledger row(s) map a reading to this missing note")

    for note in notes.values():
        note["inbound"] = sorted(note["inbound"])
        if not note["inbound"]:
            add("no_inbound", note["path"], "no other note links here")

    return {"notes": notes, "pillars": pillars, "issues": issues}


def tokens(text: str) -> set[str]:
    return {w for w in WORD.findall(text.lower()) if w not in STOPWORDS}


def find_topic(curriculum: dict, query: str, root: Path, limit: int = 10) -> list[dict]:
    """Rank notes for a topic. Rare words count for more, and the exact phrase counts most."""
    wanted = tokens(query)
    phrase = " ".join(query.lower().split())
    multiword = len(wanted) > 1
    documents = {}
    frequency = Counter()
    for note in curriculum["notes"].values():
        body = (root / note["path"]).read_text(encoding="utf-8").lower()
        documents[note["path"]] = (body, tokens(body))
        frequency.update(wanted & documents[note["path"]][1])
    total = max(len(documents), 1)
    weight = {w: math.log((1 + total) / (1 + frequency[w])) + 0.1 for w in wanted}

    ranked = []
    for note in curriculum["notes"].values():
        body, body_tokens = documents[note["path"]]
        found = wanted & body_tokens
        if not found:
            continue
        title_tokens = tokens(note["title"])
        heading_tokens = tokens(" ".join(note["headings"]))
        phrase_hits = body.count(phrase) if multiword else 0
        score = sum(weight[w] * (1 + 5 * (w in title_tokens) + 3 * (w in heading_tokens)) for w in found)
        score += 10 * min(phrase_hits, 5)
        if multiword and len(found) == 1 and not phrase_hits:
            score /= 4  # one word of a phrase, on its own, is weak evidence
        matching = [h for h in note["headings"] if wanted & tokens(h)]
        ranked.append({"path": note["path"], "score": round(score, 1), "title": note["title"],
                       "phrase_hits": phrase_hits, "headings": matching[:4]})
    return sorted(ranked, key=lambda r: (-r["score"], r["path"]))[:limit]


def summary(curriculum: dict) -> str:
    notes = curriculum["notes"].values()
    by_subject = Counter(n["subject"] for n in notes)
    pillar_count = Counter(p["subject"] for p in curriculum["pillars"].values())
    words = defaultdict(int)
    for note in notes:
        words[note["subject"]] += note["words"]
    lines = [f"{'subject':<18}{'pillars':>8}{'notes':>7}{'words':>10}"]
    for subject in SUBJECTS:
        lines.append(f"{subject:<18}{pillar_count[subject]:>8}{by_subject[subject]:>7}{words[subject]:>10}")
    lines.append("")
    kinds = Counter(i["kind"] for i in curriculum["issues"])
    lines.extend(f"{kinds[k]:>5}  {k}" for k in sorted(kinds, key=lambda k: (k in INFO_KINDS, -kinds[k])))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build")
    issues_parser = commands.add_parser("issues")
    issues_parser.add_argument("--pillar", help="only this pillar, or every pillar under this prefix")
    issues_parser.add_argument("--kind")
    issues_parser.add_argument("--strict", action="store_true", help="exit 1 on any issue that is not information only")
    find_parser = commands.add_parser("find")
    find_parser.add_argument("query")
    note_parser = commands.add_parser("note")
    note_parser.add_argument("path")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    curriculum = build(root)

    if args.command == "build":
        out = root / MAP_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(curriculum, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(summary(curriculum))
        print(f"\nwrote {MAP_PATH}")
    elif args.command == "issues":
        selected = [
            i for i in curriculum["issues"]
            if (not args.kind or i["kind"] == args.kind)
            and (not args.pillar or (i["pillar"] or i["path"]).startswith(args.pillar.rstrip("/")))
        ]
        for issue in selected:
            print(f"{issue['kind']:<20} {issue['path']}: {issue['detail']}")
        actionable = [i for i in selected if i["kind"] not in INFO_KINDS]
        print(f"{len(actionable)} issue(s), {len(selected) - len(actionable)} information only")
        if args.strict and actionable:
            return 1
    elif args.command == "find":
        for row in find_topic(curriculum, args.query, root):
            headings = f"  [{'; '.join(row['headings'])}]" if row["headings"] else ""
            print(f"{row['score']:>6}  {row['path']}  {row['title']}{headings}")
    elif args.command == "note":
        key = Path(args.path).as_posix().removeprefix("./")
        note = curriculum["notes"].get(key)
        if note is None:
            print(f"not a note: {key}", file=sys.stderr)
            return 2
        print(json.dumps(note, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
