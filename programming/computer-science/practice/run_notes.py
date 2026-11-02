#!/usr/bin/env python3
"""Run every ```python block in the chapters, each in its own empty temporary directory.

A block must exit 0. If a ```text block follows, its output is compared exactly, unless the text block
is marked <!-- measured -->. Measured output holds timings, which change on every run: for those this
checks that the code still runs, not that your numbers match.

Markers on the line before a python block:
  <!-- requires: numpy -->          run with numpy available
  <!-- requires: free-threaded -->  run on python3.14t
  <!-- requires: openssl -->        skip with a note if the openssl command is missing
  <!-- requires: network -->        skip unless run with --network

Usage: run_notes.py [--network] [--only 03] [--list]
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

NOTES = Path(__file__).resolve().parent.parent / "notes"
TIMEOUT_SECONDS = 180
MARKER = re.compile(r"<!--\s*(requires:\s*([\w-]+)|measured)\s*-->")


def blocks(text):
    """Yield (line number, code, requires, expected output or None, measured)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() != "```python":
            i += 1
            continue
        start = i + 1
        previous = lines[i - 1] if i else ""
        match = MARKER.fullmatch(previous.strip())
        requires = match.group(2) if match and match.group(2) else None
        j = start
        while lines[j].strip() != "```":
            j += 1
        code = "\n".join(lines[start:j]) + "\n"
        i = j + 1
        k = i
        while k < len(lines) and not lines[k].strip():
            k += 1
        measured = k < len(lines) and lines[k].strip() == "<!-- measured -->"
        if measured:
            k += 1
            while k < len(lines) and not lines[k].strip():
                k += 1
        expected = None
        if k < len(lines) and lines[k].strip() == "```text":
            end = k + 1
            while lines[end].strip() != "```":
                end += 1
            expected = "\n".join(lines[k + 1:end])
            i = end + 1
        yield start, code, requires, expected, measured


def command(requires):
    uv = ["uv", "run", "--quiet", "--no-project"]
    if requires == "numpy":
        return [*uv, "--python", "3.14", "--with", "numpy", "python"]
    if requires == "free-threaded":
        return [*uv, "--python", "3.14t", "python"]
    return [sys.executable]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true")
    parser.add_argument("--only", default="")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    failures = skipped = passed = 0
    for note in sorted(NOTES.glob("*.md")):
        if not note.name.startswith(args.only):
            continue
        start_note = time.perf_counter()
        ran = exact = 0
        for line, code, requires, expected, measured in blocks(note.read_text()):
            if args.list:
                kind = "measured" if measured or expected is None else "exact"
                print(f"{note.name}:{line} {kind} {requires or ''}")
                continue
            if requires == "network" and not args.network:
                print(f"skip  {note.name}:{line}  (needs the network; pass --network)")
                skipped += 1
                continue
            if requires == "openssl" and not shutil.which("openssl"):
                print(f"skip  {note.name}:{line}  (needs the openssl command)")
                skipped += 1
                continue
            with tempfile.TemporaryDirectory() as work:
                script = Path(work) / "block.py"
                script.write_text(code)
                try:
                    done = subprocess.run(
                        [*command(requires), str(script)],
                        cwd=work,
                        capture_output=True,
                        text=True,
                        timeout=TIMEOUT_SECONDS,
                    )
                except subprocess.TimeoutExpired:
                    print(f"FAIL  {note.name}:{line}  timed out after {TIMEOUT_SECONDS} s")
                    failures += 1
                    continue
            if done.returncode:
                print(f"FAIL  {note.name}:{line}  exit {done.returncode}\n{done.stderr[-800:]}")
                failures += 1
                continue
            if expected is not None and not measured:
                exact += 1
                if done.stdout.rstrip("\n") != expected.rstrip("\n"):
                    print(f"FAIL  {note.name}:{line}  output differs\n--- note\n{expected}\n--- run\n{done.stdout}")
                    failures += 1
                    continue
            ran += 1
            passed += 1
        if not args.list:
            print(f"ok    {note.name}  ({ran} blocks ran, {exact} compared exactly, {time.perf_counter() - start_note:.0f} s)")
    if not args.list:
        print(f"{passed} blocks passed, {failures} failed, {skipped} skipped")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
