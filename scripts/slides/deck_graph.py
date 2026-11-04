#!/usr/bin/env python3
"""The lecture graph: which deck teaches which note, and how the decks lead into each other.

A pillar's lectures live in <pillar>/slides/lectures/NN-slug.yaml, one per note, plus an overview. Each carries a
`lecture:` block whose edges point at notes, because a note is the stable entity: an edge to a note with no lecture
yet is still true, and it starts naming the lecture the day one is written.

    uv run -q --with pyyaml python scripts/slides/deck_graph.py check     exit 1 on a broken edge or a double claim
    uv run -q --with pyyaml python scripts/slides/deck_graph.py build     regenerate DECKS.md, the curriculum-wide map

The spec is in .claude/skills/slides/references/deck-spec.md.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".venv", "node_modules", ".git"}
EDGES = ("requires", "next", "related")
DECKS_MD = "DECKS.md"
# Sections that are study aids, not lecture material. Anything else needs a slide, or a line in `omits:`.
BACK_MATTER = {"Practice", "Try it", "Interview checklist", "Next", "References", "Further reading"}
SUBJECTS = ("ai-engineering", "generative-ai", "data-analytics", "data-science", "data-engineering", "programming")
H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
LINK = re.compile(r"\]\((?!https?:)([^)#\s]+\.md)(?:#[^)]*)?\)")


@dataclass
class Lecture:
    spec: Path
    pillar: str
    title: str
    covers: list[str]
    requires: list[str] = field(default_factory=list)
    next: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    omits: list[str] = field(default_factory=list)
    overview: bool = False

    @property
    def stem(self) -> str:
        return self.spec.stem


def lecture_from(spec_path: Path, data: dict, root: Path = ROOT) -> Lecture:
    block = data["lecture"]
    pillar = spec_path.resolve().parents[2].relative_to(root.resolve()).as_posix()
    return Lecture(spec_path, pillar, data["deck"]["title"], list(block.get("covers", [])),
                   *(list(block.get(edge, [])) for edge in EDGES),
                   omits=list(block.get("omits", [])), overview=bool(block.get("overview")))


def lecture_specs(root: Path = ROOT) -> list[Path]:
    return sorted(p for p in root.rglob("slides/lectures/*.yaml") if SKIP.isdisjoint(p.parts))


def load_lectures(root: Path = ROOT) -> list[Lecture]:
    return [lecture_from(p, yaml.safe_load(p.read_text(encoding="utf-8")), root) for p in lecture_specs(root)]


def _strip_fences(text: str) -> str:
    return re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)


def note_title(path: Path) -> str:
    body = _strip_fences(path.read_text(encoding="utf-8"))
    match = H1.search(body)
    title = match.group(1) if match else path.stem
    return re.sub(r"^[\dA-Za-z.]+\s+[—-]\s+", "", title)


def note_sections(path: Path) -> list[str]:
    """The note's ## headings in order, leaving out fenced code, where a # is a comment."""
    return re.findall(r"^##\s+(.+?)\s*$", _strip_fences(path.read_text(encoding="utf-8")), flags=re.M)


def teaching_sections(path: Path) -> list[str]:
    return [s for s in note_sections(path) if s not in BACK_MATTER]


def syllabus_order(pillar: str, root: Path = ROOT) -> list[str]:
    """The pillar's notes in reading order: as the README's syllabus links them, then any it doesn't."""
    readme = root / pillar / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    start = text.find("## Syllabus")
    if start < 0:
        start = 0
    end = text.find("\n## ", start + 1)
    linked = [f"{pillar}/{m}" for m in LINK.findall(text[start:end if end > 0 else None]) if m.startswith("notes/")]
    every = [p.relative_to(root).as_posix() for p in sorted((root / pillar / "notes").glob("*.md"))]
    return [p for p in dict.fromkeys(linked) if p in every] + [p for p in every if p not in linked]


def position(lecture: Lecture, root: Path = ROOT) -> tuple[int, int]:
    """(this lecture's place, the lectures the series will have): one per note, plus the overview."""
    order = syllabus_order(lecture.pillar, root)
    total = len(order) + 1
    if lecture.overview:
        return 1, total
    indices = [order.index(c) for c in lecture.covers if c in order]
    return (min(indices) + 2 if indices else total), total


def label(note: str, lectures: list[Lecture], root: Path = ROOT, here: str = "") -> str:
    """How a slide names an edge's target: the lecture that teaches it, or the note, saying which it is."""
    pillar = note.split("/notes/")[0] if "/notes/" in note else Path(note).parent.as_posix()
    where = "" if pillar == here else f" ({pillar})"
    for lecture in lectures:
        if note in lecture.covers:
            return f"{lecture.title}{where}"
    path = root / note
    return f"{note_title(path) if path.is_file() else note}{where}, notes only"


def slide_label(note: str, lectures: list[Lecture], root: Path = ROOT, here: str = "") -> str:
    """How a generated slide names an edge's target for a seated audience: its title, and its subject if it's elsewhere."""
    pillar = note.split("/notes/")[0] if "/notes/" in note else Path(note).parent.as_posix()
    where = "" if pillar == here else f" ({pillar.split('/')[0].replace('-', ' ')})"
    for lecture in lectures:
        if note in lecture.covers:
            return f"{lecture.title}{where}"
    path = root / note
    return f"{note_title(path) if path.is_file() else Path(note).stem}{where}"


def problems(lectures: list[Lecture], root: Path = ROOT) -> list[str]:
    """Broken edges, notes claimed twice and requirement cycles. Unwritten lectures are fine: the series grows."""
    found = []
    owner: dict[str, str] = {}
    for lecture in lectures:
        name = f"{lecture.pillar}/{lecture.stem}"
        if not lecture.covers:
            found.append(f"{name}: covers nothing")
        for note in lecture.covers:
            if not (root / note).is_file():
                found.append(f"{name}: covers {note}, which does not exist")
            if note in owner:
                found.append(f"{name}: {note} is already covered by {owner[note]}")
            owner[note] = name
        for edge in EDGES:
            for note in getattr(lecture, edge):
                if not (root / note).is_file():
                    found.append(f"{name}: {edge} {note}, which does not exist")
    needs = {f"{l.pillar}/{l.stem}": {owner[n] for n in l.requires if n in owner} for l in lectures}

    def walk(node: str, trail: tuple[str, ...]) -> None:
        for dep in needs.get(node, ()):
            if dep in trail:
                found.append("requires cycle: " + " -> ".join((*trail[trail.index(dep):], dep)))
            else:
                walk(dep, (*trail, dep))

    for node in needs:
        walk(node, (node,))
    return list(dict.fromkeys(found))


def pillar_dirs(root: Path = ROOT) -> list[str]:
    found = []
    for subject in SUBJECTS:
        for readme in sorted((root / subject).rglob("README.md")):
            pillar = readme.parent
            if (pillar / "notes").is_dir() and SKIP.isdisjoint(pillar.parts):
                found.append(pillar.relative_to(root).as_posix())
    return found


def pillar_builds_on(pillar: str, known: list[str], root: Path = ROOT) -> list[str]:
    """Pillars linked from the README's **Builds on** table."""
    text = (root / pillar / "README.md").read_text(encoding="utf-8")
    start = text.find("**Builds on**")
    if start < 0:
        return []
    end = text.find("**Feeds into**", start)
    found = []
    for link in LINK.findall(text[start:end if end > 0 else None]):
        target = (root / pillar / link).resolve()
        try:
            rel = target.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        match = next((k for k in known if rel.startswith(k + "/")), None)
        if match and match != pillar:
            found.append(match)
    return list(dict.fromkeys(found))


def _node(name: str) -> str:
    return re.sub(r"\W", "_", name)


def render(lectures: list[Lecture], root: Path = ROOT) -> str:
    pillars = pillar_dirs(root)
    out = ["# Decks", "",
           "Generated by `make deck-graph` from each lecture's `lecture:` block and each README's Builds on table. Don't edit it by hand.",
           "", "A pillar's series is one lecture per note, plus an overview. A pillar deck is the older single condensed deck.",
           "", "## The curriculum", "", "An arrow means the pillar at its head builds on the one at its tail.", "",
           "```mermaid", "flowchart LR"]
    for subject in SUBJECTS:
        members = [p for p in pillars if p.startswith(subject + "/")]
        if members:
            out.append(f"  subgraph {_node(subject)}[{subject}]")
            out += [f'    {_node(p)}["{p.removeprefix(subject + "/")}"]' for p in members]
            out.append("  end")
    for pillar in pillars:
        out += [f"  {_node(dep)} --> {_node(pillar)}" for dep in pillar_builds_on(pillar, pillars, root)]
    out += ["```", "", "## Progress", "", "| Pillar | Lectures written | Notes | Pillar deck |", "|---|---|---|---|"]
    for pillar in pillars:
        written = sum(l.pillar == pillar for l in lectures)
        planned = len(syllabus_order(pillar, root)) + 1
        has_deck = "yes" if (root / pillar / "slides" / "deck.yaml").is_file() else "no"
        out.append(f"| [{pillar}]({pillar}/README.md) | {written} of {planned} | {planned - 1} | {has_deck} |")
    for pillar in dict.fromkeys(l.pillar for l in lectures):
        series = sorted((l for l in lectures if l.pillar == pillar), key=lambda l: position(l, root)[0])
        out += ["", f"## {pillar}", "", "| # | Lecture | Before it | After it |", "|---|---|---|---|"]
        for lecture in series:
            place = position(lecture, root)[0]
            spec = lecture.spec.relative_to(root).as_posix()
            before = ", ".join(label(n, lectures, root, pillar) for n in lecture.requires) or "nothing"
            after = ", ".join(label(n, lectures, root, pillar) for n in lecture.next) or "end of the series"
            out.append(f"| {place} | [{lecture.title}]({spec}) | {before} | {after} |")
    return "\n".join(out) + "\n"


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    lectures = load_lectures()
    found = problems(lectures)
    for problem in found:
        print(f"deck-graph: {problem}")
    if command == "build":
        (ROOT / DECKS_MD).write_text(render(lectures), encoding="utf-8")
        print(f"wrote {DECKS_MD}")
    elif (ROOT / DECKS_MD).is_file() and (ROOT / DECKS_MD).read_text(encoding="utf-8") != render(lectures):
        # Reported, not gated: another session editing a Builds on table shouldn't fail this one's tests.
        print(f"deck-graph: {DECKS_MD} is out of date, run make deck-graph")
    print(f"deck-graph: {len(lectures)} lectures, {len(found)} problems")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
