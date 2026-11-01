from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Callable

from model import Complete

LABELS = ["billing", "account", "bug", "how_to"]


@dataclass
class Variant:
    name: str
    render: Callable[[str], str]
    system: str = ""


def parse_label(output: str) -> str | None:
    """Parses the output as {"label": ...}. Prose around the JSON is a failure: downstream code parses this."""
    try:
        value = json.loads(output.strip())
    except json.JSONDecodeError:
        return None
    label = value.get("label") if isinstance(value, dict) else None
    return label if isinstance(label, str) else None


def _valid_json(output: str, case: dict) -> str | None:
    return "not JSON with a string `label`" if parse_label(output) is None else None


def _known_label(output: str, case: dict) -> str | None:
    label = parse_label(output)
    return None if label in LABELS else f"label outside the set: {'null' if label is None else label}"


def _correct_label(output: str, case: dict) -> str | None:
    label = parse_label(output)
    return None if label == case["label"] else f"wanted {case['label']}, got {'null' if label is None else label}"


# A grader returns None on pass, or the reason for failing.
GRADERS = {"valid_json": _valid_json, "known_label": _known_label, "correct_label": _correct_label}


@dataclass
class CaseResult:
    id: str
    failures: dict[str, str]
    output: str


@dataclass
class VariantResult:
    name: str
    results: list[CaseResult]
    pass_rate: float
    ci95: tuple[float, float]
    by_grader: dict[str, float] = field(default_factory=dict)
    tokens: int = 0


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson interval: stays honest at small n, where a plain +/- would leave [0, 1]."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, mid - half), min(1.0, mid + half)


def run_variant(v: Variant, cases: list[dict], complete: Complete) -> VariantResult:
    results = []
    tokens = 0
    for case in cases:
        res = complete(v.render(case["ticket"]), system=v.system, max_tokens=256)
        tokens += res.input_tokens + res.output_tokens
        failures = {n: why for n, grade in GRADERS.items() if (why := grade(res.text, case))}
        results.append(CaseResult(case["id"], failures, res.text))
    passed = sum(not r.failures for r in results)
    by_grader = {g: sum(g not in r.failures for r in results) / len(results) for g in GRADERS}
    return VariantResult(v.name, results, passed / len(results), wilson(passed, len(results)), by_grader, tokens)


def flips(a: VariantResult, b: VariantResult) -> tuple[list[str], list[str]]:
    """Cases where the second variant changed the outcome. Aggregates hide these."""
    fixed = [x.id for x, y in zip(a.results, b.results) if x.failures and not y.failures]
    broken = [x.id for x, y in zip(a.results, b.results) if not x.failures and y.failures]
    return fixed, broken
