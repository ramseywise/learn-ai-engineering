# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from dataclasses import replace

from loop import Limits, prompt_for, run_loop
from scorekeeper import HELD_OUT, VISIBLE, score
from stub import SYMBOLS, gamer, honest, overfit, scripted, stuck

limits = Limits()
wrong = "lambda s: 1"

# The scorekeeper
assert score("lambda s: s", VISIBLE).passed == 0  # the identity function matches none of the four slugs
assert score(SYMBOLS, VISIBLE).passed == 4 and score(SYMBOLS, HELD_OUT).passed == 3
assert "does not load" in score("not code", VISIBLE).failures[0]
assert score("lambda s: [0 for _ in iter(int, 1)]", VISIBLE, timeout_s=0.5).passed == 0, "an infinite loop is a failure, not a hang"
assert len(score("lambda s: 1/0", VISIBLE).failures) == 4

# Each stop reason
a = run_loop(honest(), limits)
assert a.stop == "passed" and len(a.iterations) == 3 and a.best
g = run_loop(gamer(), limits)
assert g.stop == "gamed" and g.best is None, "a gamed run ships nothing"
assert run_loop(overfit(), limits).stop == "gamed"
s = run_loop(stuck(), limits)
assert s.stop == "no_progress" and len(s.iterations) == 3
assert run_loop(scripted([wrong]), replace(limits, patience=99, max_iterations=2)).stop == "max_iterations"
assert run_loop(scripted([wrong]), replace(limits, patience=99, max_tokens=150)).stop == "budget"
original = HELD_OUT[0]["want"]


def tamper(n: int) -> None:
    HELD_OUT[0]["want"] = "tampered"


t = run_loop(scripted([wrong]), limits, tamper)
HELD_OUT[0]["want"] = original
assert t.stop == "tampered"

# The maker never sees held-out inputs
after = run_loop(scripted(["lambda s: s"]), replace(limits, max_iterations=1))
p = prompt_for(after.iterations[0])
for c in HELD_OUT:
    assert c["input"] not in p, f"held-out input leaked: {c['input']}"
print("ok: all assertions passed")
