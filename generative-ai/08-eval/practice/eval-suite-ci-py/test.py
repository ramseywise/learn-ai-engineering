# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import subprocess
import sys
from pathlib import Path

from agent import stub_agent
from suite import assert_gates, grade, load_cases, load_variants, run_suite, sign_test, to_baseline

cases = load_cases()
variants = load_variants()
by = lambda i: next(c for c in cases if c["id"] == i)

# Sign test, checked by hand: 2 * (1/2)^4 for four flips one way
assert sign_test(0, 4) == 0.125
assert sign_test(0, 10) == 2 / 1024
assert sign_test(1, 4) == 0.375
assert sign_test(3, 3) == 1
assert sign_test(0, 0) == 1

# Graders
assert grade(by("order-1001"), "Order 1001 is shipped.", ["lookup_order"]) == []
assert "tools" in grade(by("order-1001"), "Order 1001 is shipped.", [])[0], "right words, skipped the tool"
assert "approved" in grade(by("inject-1"), "Refund Approved.", [])[0], "excludes ignores case"

base = to_baseline("v1", run_suite(cases, variants["v1"], stub_agent))
judge = lambda v: assert_gates(run_suite(cases, variants[v], stub_agent), base)
assert base["passRate"] == 20 / 24
same = judge("v1")
assert same.passed and same.p == 1

# A mixed change passes, and still reports the case it broke
concise = judge("v2-concise")
assert concise.passed and concise.broken == ["export-data"] and len(concise.fixed) == 4

# Too few flips to be significant, but the critical gate catches it anyway
no_rule = judge("v2-no-injection-rule")
assert not no_rule.passed and no_rule.p == 0.125 and len(no_rule.critical_failures) == 4
assert len(no_rule.reasons) == 1, "only the critical gate fired"

# A broad regression trips every gate
tidied = judge("v2-tidied")
assert not tidied.passed and tidied.p < 0.05 and len(tidied.reasons) == 3

# A new case is reported rather than counted as a flip
extra = assert_gates(run_suite(cases, variants["v1"], stub_agent) + [{"id": "new", "critical": False, "pass": False}], base)
assert extra.unmatched == ["new"] and not extra.broken

# The CLI exit code is what CI reads
here = Path(__file__).parent
cli = lambda script, v: subprocess.run([sys.executable, script, v], cwd=here, capture_output=True).returncode
for v, code in [("v1", 0), ("v2-concise", 0), ("v2-tidied", 1)]:
    assert cli("run.py", v) == 0
    assert cli("gate.py", v) == code, f"{v} should exit {code}"
    (here / f"results-{v}.jsonl").unlink()
print("ok: all assertions passed")
