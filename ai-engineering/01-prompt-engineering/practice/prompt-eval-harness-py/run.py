# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Same cases, variants and report as the TypeScript lab in ../prompt-eval-harness."""
import json
from pathlib import Path

from harness import flips, run_variant
from model import choose_model
from stub import stub
from variants import VARIANTS

cases = json.loads((Path(__file__).parent / "../prompt-eval-harness/cases.json").read_text())
name, complete = choose_model(stub)
print(f"model: {name}, {len(cases)} cases\n")

results = [run_variant(v, cases, complete) for v in VARIANTS]


def pct(x: float) -> str:
    return f"{100 * x:.0f}%".rjust(4)


print("variant          pass   95% CI       json  known  correct  tokens")
for r in results:
    b = r.by_grader
    print(
        f"{r.name:<16} {pct(r.pass_rate)}  [{pct(r.ci95[0])},{pct(r.ci95[1])}]  "
        f"{pct(b['valid_json'])}  {pct(b['known_label'])}    {pct(b['correct_label'])}  {r.tokens:>6}"
    )
for a, b in zip(results, results[1:]):
    fixed, broken = flips(a, b)
    print(f"\n{a.name} -> {b.name}\n  fixed:  {', '.join(fixed) or 'none'}\n  broken: {', '.join(broken) or 'none'}")
last = results[-1]
failing = [r for r in last.results if r.failures]
print(f"\nstill failing in {last.name}: {len(failing)}")
for r in failing:
    print(f"  {r.id}: {next(iter(r.failures.values()))}")
