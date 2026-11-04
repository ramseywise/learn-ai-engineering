#!/usr/bin/env python3
"""Tell whether a built .pptx still matches its deck.yaml. Standard library only, so `make test` needs no packages.

    python3 scripts/slides/deck_stamp.py [deck.yaml ...]     # default: every tracked or local slides/deck.yaml and lecture

build_deck.py writes the sha256 of the deck.yaml bytes into the pptx's core properties. A timestamp could not do this
job: zip entries change on every build and a git checkout resets mtimes, so a fresh clone would look stale.

- stale: the stamp differs from the yaml. Exit 1.
- unstamped: the pptx was built before stamping, so its state is unknown. Reported, not failed, until the decks are rebuilt.
- no pptx: nothing built yet. Reported, not failed.

The stamp covers the yaml only: a changed image or a changed builder does not make a deck stale.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP_KEY = "deck-yaml-sha256:"
STAMP = re.compile(re.escape(STAMP_KEY) + r"([0-9a-f]{64})")
OUTPUT = re.compile(r"^\s+output:\s*['\"]?([^'\"#\n]+?)['\"]?\s*(?:#.*)?$", re.M)
SKIP = {".venv", "node_modules", ".git"}


def deck_hash(spec: Path) -> str:
    return hashlib.sha256(spec.read_bytes()).hexdigest()


def stamp_value(spec: Path) -> str:
    return STAMP_KEY + deck_hash(spec)


def pptx_for(spec: Path) -> Path:
    """Where build_deck.py writes this deck: `deck.output`, else <pillar>.pptx, or a lecture's own name."""
    head = spec.read_text(encoding="utf-8").split("\nparts:", 1)[0]
    match = OUTPUT.search(head)
    default = f"{spec.stem}.pptx" if spec.parent.name == "lectures" else f"{spec.parent.parent.name}.pptx"
    return spec.parent / (match.group(1) if match else default)


def state(spec: Path) -> str:
    """One of current, stale, unstamped, no pptx."""
    pptx = pptx_for(spec)
    if not pptx.is_file():
        return "no pptx"
    with zipfile.ZipFile(pptx) as archive:
        try:
            core = archive.read("docProps/core.xml").decode("utf-8")
        except KeyError:
            return "unstamped"
    found = STAMP.search(core)
    if not found:
        return "unstamped"
    return "current" if found.group(1) == deck_hash(spec) else "stale"


def all_specs() -> list[Path]:
    specs = [*ROOT.rglob("slides/deck.yaml"), *ROOT.rglob("slides/lectures/*.yaml")]
    return sorted(p for p in specs if SKIP.isdisjoint(p.parts))


def check(specs: list[Path]) -> int:
    """Print the report and return the number of stale decks."""
    counts = {"current": 0, "stale": 0, "unstamped": 0, "no pptx": 0}
    for spec in specs:
        found = state(spec)
        counts[found] += 1
        if found == "stale":
            print(f"stale: {spec}: rebuild with make slides")
    print(f"deck-check: {counts['current']} current, {counts['stale']} stale; "
          f"not gated: {counts['unstamped']} unstamped (built before stamping), {counts['no pptx']} with no pptx")
    return counts["stale"]


def main() -> None:
    specs = [Path(a) for a in sys.argv[1:]] or all_specs()
    sys.exit(1 if check(specs) else 0)


if __name__ == "__main__":
    main()
