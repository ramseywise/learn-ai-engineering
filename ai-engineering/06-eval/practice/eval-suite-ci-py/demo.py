# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Every variant through both phases, in memory, against the stub. Writes nothing."""
import json
from pathlib import Path

from agent import stub_agent
from suite import assert_gates, load_cases, load_variants, report, run_suite

baseline = json.loads((Path(__file__).parent / "baseline.json").read_text())
cases = load_cases()
print(f"{len(cases)} cases, {sum(c['critical'] for c in cases)} critical. Baseline: {baseline['variant']}, {100 * baseline['passRate']:.0f}%.\n")
for name, system in load_variants().items():
    print(report(name, assert_gates(run_suite(cases, system, stub_agent), baseline)) + "\n")
