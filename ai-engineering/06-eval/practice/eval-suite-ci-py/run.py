# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Phase 1: run one variant and write results-<variant>.jsonl.  uv run run.py v1 [--write-baseline]"""
import json
import sys
from pathlib import Path

from agent import choose_agent
from suite import load_cases, load_variants, run_suite, to_baseline

here = Path(__file__).parent
variant = sys.argv[1] if len(sys.argv) > 1 else "v1"
system = load_variants().get(variant)
if not system:
    raise SystemExit(f"unknown variant: {variant}")
name, agent = choose_agent()
rows = run_suite(load_cases(), system, agent)
(here / f"results-{variant}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
print(f"{name}, {variant}: {sum(r['pass'] for r in rows)}/{len(rows)} passed, wrote results-{variant}.jsonl")
if "--write-baseline" in sys.argv:
    (here / "baseline.json").write_text(json.dumps(to_baseline(variant, rows), indent=2) + "\n")
    print("wrote baseline.json")
