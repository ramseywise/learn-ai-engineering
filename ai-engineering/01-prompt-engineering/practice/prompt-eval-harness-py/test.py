# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import json
from pathlib import Path

from harness import GRADERS, flips, parse_label, run_variant, wilson
from stub import stub
from variants import VARIANTS

cases = json.loads((Path(__file__).parent / "../prompt-eval-harness/cases.json").read_text())

assert parse_label('{"label":"bug"}') == "bug"
assert parse_label('Sure! {"label":"bug"}') is None, "prose around JSON must fail"
assert GRADERS["known_label"]('{"label":"spam"}', cases[0]) == "label outside the set: spam"
lo, hi = wilson(6, 12)
assert 0.25 < lo < 0.3 and 0.7 < hi < 0.75, (lo, hi)

bare, fmt, shots = [run_variant(v, cases, stub) for v in VARIANTS]
assert bare.by_grader["valid_json"] == 0, "bare prompt gets no JSON"
assert fmt.pass_rate > bare.pass_rate
assert shots.pass_rate == 1
assert "edge-4" in flips(fmt, shots)[0], "rule resists the injected instruction"
assert shots.tokens > fmt.tokens, "better prompt costs tokens: report it"
print("ok: all assertions passed")
