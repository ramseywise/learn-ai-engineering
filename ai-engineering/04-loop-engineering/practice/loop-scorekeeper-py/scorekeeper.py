from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass

# The task: a slugify function. The maker sees VISIBLE. It never sees HELD_OUT.
# The checks are the same as in the TypeScript lab.
VISIBLE = [
    {"input": "Hello World", "want": "hello-world"},
    {"input": "  Trim me  ", "want": "trim-me"},
    {"input": "Already-slugged", "want": "already-slugged"},
    {"input": "Rock & Roll!", "want": "rock-roll"},
]
HELD_OUT = [
    {"input": "Crème Brûlée", "want": "creme-brulee"},
    {"input": "a---b", "want": "a-b"},
    {"input": "!!!", "want": ""},
    {"input": "Mixed_Case 42", "want": "mixed-case-42"},
]


@dataclass
class Score:
    passed: int
    total: int
    failures: list[str]


# Python has no vm module with a timeout, so a candidate runs in a child process. That also lets an
# infinite loop cost one failed iteration. It stops accidents, not attackers.
_RUNNER = """
import json, sys
spec = json.load(sys.stdin)
try:
    fn = eval(spec["code"])
    if not callable(fn):
        raise TypeError("not a function")
except BaseException as e:
    print(json.dumps({"load_error": str(e)}))
    sys.exit(0)
out = []
for c in spec["inputs"]:
    try:
        out.append({"got": fn(c)})
    except Exception as e:
        out.append({"threw": str(e)})
print(json.dumps({"results": out}))
"""


def score(code: str, checks: list[dict], timeout_s: float = 2.0) -> Score:
    """Deterministic: the same code gets the same score, and no model is asked its opinion."""
    total = len(checks)
    spec = json.dumps({"code": code, "inputs": [c["input"] for c in checks]})
    try:
        done = subprocess.run([sys.executable, "-I", "-c", _RUNNER], input=spec, capture_output=True, text=True, timeout=timeout_s, encoding="utf8")
    except subprocess.TimeoutExpired:
        return Score(0, total, [f"timed out after {timeout_s} s"])
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError:
        return Score(0, total, [f"does not load: {done.stderr.strip()[:200]}"])
    if "load_error" in report:
        return Score(0, total, [f"does not load: {report['load_error']}"])
    failures, passed = [], 0
    for c, r in zip(checks, report["results"]):
        shown = json.dumps(c["input"], ensure_ascii=False)
        if "threw" in r:
            failures.append(f"slugify({shown}) threw: {r['threw']}")
        elif r["got"] == c["want"]:
            passed += 1
        else:
            failures.append(f"slugify({shown}) gave {json.dumps(r['got'], ensure_ascii=False)}, wanted {json.dumps(c['want'])}")
    return Score(passed, total, failures)


def fingerprint() -> str:
    """Fingerprints the checks. If they change during a run, the maker moved the goalposts."""
    return hashlib.sha256(json.dumps([VISIBLE, HELD_OUT]).encode()).hexdigest()
