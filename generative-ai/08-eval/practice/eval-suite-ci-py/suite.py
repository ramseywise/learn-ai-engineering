"""Phase 1 runs the agent and writes rows. Phase 2 reads rows and decides. The note explains why
these stay apart: a threshold change should not cost a model run."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

SHARED = Path(__file__).parent / "../eval-suite-ci"
FLOOR, ALPHA = 0.6, 0.05


def load_cases() -> list[dict]:
    return [json.loads(l) for l in (SHARED / "cases.jsonl").read_text().strip().split("\n")]


def load_variants() -> dict[str, str]:
    return json.loads((SHARED / "variants.json").read_text())


def grade(case: dict, text: str, tools: list[str]) -> list[str]:
    failures = []
    expect = case["expect"]
    failures += [f'missing "{s}"' for s in expect.get("includes", []) if s not in text]
    failures += [f'contains "{s}"' for s in expect.get("excludes", []) if s in text.lower()]
    want = expect.get("tools")
    if want is not None and want != tools:
        failures.append(f"tools [{','.join(tools)}], wanted [{','.join(want)}]")
    return failures


def run_suite(cases: list[dict], system: str, agent: Callable) -> list[dict]:
    rows = []
    for c in cases:
        r = agent(system, c["input"])
        failures = grade(c, r.text, r.tools)
        rows.append({"id": c["id"], "kind": c["kind"], "critical": c["critical"], "pass": not failures, "failures": failures, "text": r.text, "tools": r.tools, "tokens": r.tokens})
    return rows


def sign_test(fixed: int, broken: int) -> float:
    """Exact two-sided sign test on paired flips. Pairs that did not change carry no information."""
    n = fixed + broken
    if n == 0:
        return 1.0
    tail, choose = 0.0, 1.0
    for k in range(min(fixed, broken) + 1):
        tail += choose
        choose = choose * (n - k) / (k + 1)
    return min(1.0, 2 * tail / 2**n)


def to_baseline(variant: str, rows: list[dict]) -> dict:
    return {"variant": variant, "passRate": sum(r["pass"] for r in rows) / len(rows), "results": {r["id"]: r["pass"] for r in rows}}


@dataclass
class Verdict:
    passed: bool
    pass_rate: float
    fixed: list[str]
    broken: list[str]
    p: float
    critical_failures: list[str]
    reasons: list[str] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)


def assert_gates(rows: list[dict], baseline: dict, floor: float = FLOOR, alpha: float = ALPHA) -> Verdict:
    """Three gates, each with its own reason, so a red build says what to do next."""
    base = baseline["results"]
    pass_rate = sum(r["pass"] for r in rows) / len(rows)
    fixed = [r["id"] for r in rows if r["id"] in base and r["pass"] and not base[r["id"]]]
    broken = [r["id"] for r in rows if r["id"] in base and not r["pass"] and base[r["id"]]]
    p = sign_test(len(fixed), len(broken))
    critical = [r["id"] for r in rows if r["critical"] and not r["pass"]]
    reasons = []
    if critical:
        reasons.append(f"critical cases failing: {', '.join(critical)}. Fix these, whatever the average says")
    if len(broken) > len(fixed) and p < alpha:
        reasons.append(f"regression: {len(broken)} broken, {len(fixed)} fixed, sign test p={p:.4f}")
    if pass_rate < floor:
        reasons.append(f"pass rate {100 * pass_rate:.0f}% is under the {100 * floor:.0f}% floor")
    return Verdict(not reasons, pass_rate, fixed, broken, p, critical, reasons, [r["id"] for r in rows if r["id"] not in base])


def report(name: str, v: Verdict) -> str:
    lines = [
        f"--- {name}: {'PASS' if v.passed else 'FAIL'}, pass rate {100 * v.pass_rate:.0f}%",
        f"  against baseline: fixed {len(v.fixed)}, broken {len(v.broken)}, sign test p={v.p:.4f}",
    ]
    if v.fixed:
        lines.append(f"  fixed:  {', '.join(v.fixed)}")
    if v.broken:
        lines.append(f"  broken: {', '.join(v.broken)}")
    if v.unmatched:
        lines.append(f"  new, no baseline yet: {', '.join(v.unmatched)}")
    lines += [f"  BLOCKED: {r}" for r in v.reasons]
    return "\n".join(lines)
