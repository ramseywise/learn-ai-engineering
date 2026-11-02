#!/usr/bin/env python3
"""Run a note's Python code blocks top to bottom in one shared namespace.

    uv run --with <packages> python practice/run_note.py notes/01-some-chapter.md

The working directory becomes the note's folder, so relative data paths in the note resolve.
Blocks whose first line contains `# illustrative` are skipped. Block N's output is printed
under a `--- block N (line L)` header. Exits 1 on the first failure unless --keep-going is set.
"""
import argparse
import os
import re
import sys
import time
import traceback
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("note", type=Path)
ap.add_argument("--keep-going", action="store_true")
args = ap.parse_args()
note = args.note.resolve()
text = note.read_text(encoding="utf-8")
os.chdir(note.parent)
os.environ.setdefault("MPLBACKEND", "Agg")
sys.path.insert(0, str(note.parent))

ns = {"__name__": "__main__"}
failed = 0
for i, m in enumerate(re.finditer(r"^```python\n(.*?)^```", text, re.S | re.M), 1):
    code = m.group(1)
    line = text.count("\n", 0, m.start()) + 1
    first = code.split("\n", 1)[0]
    if "# illustrative" in first:
        print(f"--- block {i} (line {line}): skipped, illustrative", flush=True)
        continue
    print(f"--- block {i} (line {line})", flush=True)
    start = time.time()
    try:
        exec(compile(code, f"{note.name}:block{i}", "exec"), ns)
    except Exception:
        traceback.print_exc()
        failed += 1
        if not args.keep_going:
            sys.exit(1)
    print(f"    [{time.time() - start:.1f}s]", flush=True)
print(f"{note.name}: {failed} block(s) failed")
sys.exit(1 if failed else 0)
