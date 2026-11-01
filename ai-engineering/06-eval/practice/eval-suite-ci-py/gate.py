# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Phase 2: read results and baseline, print the verdict, exit 1 on failure. No model involved."""
import json
import sys
from pathlib import Path

from suite import assert_gates, report

here = Path(__file__).parent
variant = sys.argv[1] if len(sys.argv) > 1 else "v1"
rows = [json.loads(l) for l in (here / f"results-{variant}.jsonl").read_text().strip().split("\n")]
verdict = assert_gates(rows, json.loads((here / "baseline.json").read_text()))
print(report(variant, verdict))
sys.exit(0 if verdict.passed else 1)
