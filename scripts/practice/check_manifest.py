#!/usr/bin/env python3
"""Validate every pillar's practice/manifest.yaml.

    python3 scripts/practice/check_manifest.py

A manifest tells a prototyping agent which course example is the smallest working one for a pattern.
One manifest per pillar that has a practice/ folder, in ai-engineering, generative-ai, data-analytics,
data-science and data-engineering (programming/ is out of scope). Reads only files git would track
(`git ls-files -co --exclude-standard`), as crosswalk.py does, so nothing ignored is read or required.

Each entry under `examples:` has these keys, one per line:
    path               relative to the pillar, starts with practice/, names a tracked file or folder
    purpose            one sentence, non-empty
    demonstrates       list of note paths relative to the pillar (the list may be empty)
    pattern            retrieval judge loop graph tool-agent guardrail budget finetune eval analysis other
    language           python typescript javascript jupyter sql
    runs_offline       true or false: no API key and no network at run time, once dependencies are installed
    verified_by        a command, written relative to the pillar's practice/ folder, that was run and passed, or none
    verification_note  required when verified_by is none and the example ships a test
    licence            course, unrecorded, or a licence named in THIRD_PARTY.md (the path must appear there)

Checks, one line per problem, exit 1 on any:
- the schema and the enum values;
- every path exists, and no path is listed twice;
- every demonstrates link resolves to a tracked file;
- every tracked practice example (the first path component under practice/) has an entry;
- a pillar with tracked examples has a manifest.

The file is a strict YAML subset (no PyYAML on the course's python3): `examples:` then `  - key: value`
items, `    key: value` lines, block lists of `      - value`, `[]` for an empty list, values as JSON
strings, bare words, true/false or integers, and `#` comment lines.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBJECTS = ("ai-engineering", "generative-ai", "data-analytics", "data-science", "data-engineering")
PATTERNS = {"retrieval", "judge", "loop", "graph", "tool-agent", "guardrail", "budget", "finetune", "eval", "analysis", "other"}
LANGUAGES = {"python", "typescript", "javascript", "jupyter", "sql"}
REQUIRED = ("path", "purpose", "demonstrates", "pattern", "language", "runs_offline", "verified_by", "licence")
OPTIONAL = ("verification_note",)
EXEMPT = {"README.md", ".gitignore", "data", "fetch_data.sh", "manifest.yaml"}  # dot-names are exempt too
TEST_NAME = re.compile(r"(^|/)(test\.(py|ts|js)|test_[^/]*\.py|[^/]*_test\.py|[^/]*\.test\.(ts|js)|tests/.+)$")


class ManifestError(Exception):
    pass


def _scalar(raw: str, lineno: int):
    raw = raw.strip()
    if raw == "":
        raise ManifestError(f"line {lineno}: missing value")
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ManifestError(f"line {lineno}: bad quoted string ({e.msg})") from None
        if not isinstance(value, str):
            raise ManifestError(f"line {lineno}: expected a string")
        return value
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "none":
        return None
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"[A-Za-z0-9._/-]+", raw):
        return raw
    raise ManifestError(f"line {lineno}: unquoted value {raw!r}; quote strings with double quotes")


def parse(text: str) -> list[dict]:
    """Parse the strict subset into a list of entry dicts. Raises ManifestError."""
    entries: list[dict] = []
    current: dict | None = None
    list_key: str | None = None
    seen_header = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            raise ManifestError(f"line {lineno}: tab character")
        if not seen_header:
            if line.rstrip() != "examples:":
                raise ManifestError(f"line {lineno}: expected `examples:` as the first key")
            seen_header = True
            continue
        m = re.fullmatch(r"  - ([a-z_]+):(?: (.*))?", line.rstrip())
        if m:
            current = {}
            entries.append(current)
            key, raw = m.group(1), m.group(2)
        else:
            m = re.fullmatch(r"    ([a-z_]+):(?: (.*))?", line.rstrip())
            if m:
                if current is None:
                    raise ManifestError(f"line {lineno}: key before the first `- ` item")
                key, raw = m.group(1), m.group(2)
            else:
                m = re.fullmatch(r"      - (.*)", line.rstrip())
                if not m or current is None or list_key is None or not isinstance(current.get(list_key), list):
                    raise ManifestError(f"line {lineno}: cannot parse {line.strip()!r}")
                value = _scalar(m.group(1), lineno)
                if not isinstance(value, str):
                    raise ManifestError(f"line {lineno}: list items must be quoted strings")
                current[list_key].append(value)
                continue
        if key in current:
            raise ManifestError(f"line {lineno}: key {key!r} repeated in one entry")
        list_key = None
        if raw is None or raw == "":
            current[key] = []
            list_key = key
        elif raw == "[]":
            current[key] = []
        else:
            current[key] = _scalar(raw, lineno)
    if not seen_header:
        raise ManifestError("empty manifest: expected `examples:`")
    return entries


def practice_units(pillar: str, tracked: set[str]) -> dict[str, list[str]]:
    """First path component under <pillar>/practice/ -> the tracked files under it. Exempt names are left out."""
    prefix = f"{pillar}/practice/"
    units: dict[str, list[str]] = {}
    for path in tracked:
        if not path.startswith(prefix):
            continue
        rest = path[len(prefix):]
        head = rest.split("/", 1)[0]
        if head in EXEMPT or head.startswith("."):
            continue
        units.setdefault(head, []).append(path)
    return units


def check_pillar(pillar: str, text: str | None, tracked: set[str], third_party: str) -> list[str]:
    """Problems for one pillar. `text` is the manifest, or None if the pillar has none."""
    where = f"{pillar}/practice/manifest.yaml"
    units = practice_units(pillar, tracked)
    if text is None:
        return [f"{pillar}: has tracked practice examples but no practice/manifest.yaml"] if units else []
    try:
        entries = parse(text)
    except ManifestError as e:
        return [f"{where}: {e}"]
    problems: list[str] = []
    seen: set[str] = set()
    covered: set[str] = set()
    for i, e in enumerate(entries, 1):
        name = e.get("path") if isinstance(e.get("path"), str) else f"entry {i}"
        tag = f"{where}: {name}"
        unknown = set(e) - set(REQUIRED) - set(OPTIONAL)
        missing = [k for k in REQUIRED if k not in e]
        if unknown:
            problems.append(f"{tag}: unknown key(s) {sorted(unknown)}")
        if missing:
            problems.append(f"{tag}: missing key(s) {missing}")
        path = e.get("path")
        if isinstance(path, str):
            full = f"{pillar}/{path}"
            if not path.startswith("practice/") or path.endswith("/") or ".." in path.split("/"):
                problems.append(f"{tag}: path must be practice/<name>[/...] relative to the pillar, no trailing slash")
            elif not (full in tracked or any(t.startswith(full + "/") for t in tracked)):
                problems.append(f"{tag}: path does not exist among tracked files")
            else:
                if path in seen:
                    problems.append(f"{tag}: listed twice")
                seen.add(path)
                head = path[len("practice/"):].split("/", 1)[0]
                covered.add(head)
        elif "path" in e:
            problems.append(f"{tag}: path must be a string")
        purpose = e.get("purpose")
        if "purpose" in e and (not isinstance(purpose, str) or not purpose.strip() or "\n" in purpose):
            problems.append(f"{tag}: purpose must be one non-empty line")
        dem = e.get("demonstrates")
        if "demonstrates" in e:
            if not isinstance(dem, list):
                problems.append(f"{tag}: demonstrates must be a list")
            else:
                for note in dem:
                    if f"{pillar}/{note}" not in tracked:
                        problems.append(f"{tag}: demonstrates {note!r} does not resolve to a tracked file")
        if "pattern" in e and e["pattern"] not in PATTERNS:
            problems.append(f"{tag}: pattern {e['pattern']!r} not in {sorted(PATTERNS)}")
        if "language" in e and e["language"] not in LANGUAGES:
            problems.append(f"{tag}: language {e['language']!r} not in {sorted(LANGUAGES)}")
        if "runs_offline" in e and not isinstance(e["runs_offline"], bool):
            problems.append(f"{tag}: runs_offline must be true or false")
        vb = e.get("verified_by")
        if "verified_by" in e and vb is not None and (not isinstance(vb, str) or not vb.strip()):
            problems.append(f"{tag}: verified_by must be a command or none")
        note = e.get("verification_note")
        if "verification_note" in e and (not isinstance(note, str) or not note.strip()):
            problems.append(f"{tag}: verification_note must be a non-empty string")
        if "verified_by" in e and vb is None and isinstance(path, str) and not note:
            full = f"{pillar}/{path}"
            if any(TEST_NAME.search("/" + (t[len(full) + 1:] if t != full else t.rsplit("/", 1)[-1]))
                   for t in tracked if t == full or t.startswith(full + "/")):
                problems.append(f"{tag}: ships a test but verified_by is none; add a verification_note saying why it was not run")
        if "verification_note" in e and vb is not None:
            problems.append(f"{tag}: verification_note only belongs on entries whose verified_by is none")
        lic = e.get("licence")
        if "licence" in e:
            if not isinstance(lic, str) or not lic.strip():
                problems.append(f"{tag}: licence must be a non-empty string")
            elif lic not in ("course", "unrecorded") and isinstance(path, str):
                if f"{pillar}/{path}" not in third_party:
                    problems.append(f"{tag}: licence {lic!r} but the path is not named in THIRD_PARTY.md")
    for unit in sorted(set(units) - covered):
        problems.append(f"{where}: tracked example practice/{unit} has no entry")
    return problems


def git_tracked() -> set[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-co", "--exclude-standard"],
                         check=True, capture_output=True, text=True)
    return {line for line in out.stdout.splitlines() if line}


def pillars(tracked: set[str]) -> list[str]:
    found = set()
    for path in tracked:
        parts = path.split("/")
        if len(parts) > 3 and parts[0] in SUBJECTS and parts[2] == "practice":
            found.add(f"{parts[0]}/{parts[1]}")
    return sorted(found)


def main() -> int:
    tracked = git_tracked()
    third_party = (ROOT / "THIRD_PARTY.md").read_text(errors="replace")
    problems: list[str] = []
    names = pillars(tracked)
    for pillar in names:
        mpath = f"{pillar}/practice/manifest.yaml"
        text = (ROOT / mpath).read_text() if mpath in tracked else None
        problems += check_pillar(pillar, text, tracked, third_party)
    for line in problems:
        print(line)
    if problems:
        print(f"manifest-check: {len(problems)} problem(s)")
        return 1
    print(f"manifest-check: {len(names)} pillars ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
