# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from dataclasses import replace

from budgeter import Budget, estimate, limit_of, pack, render
from scenario import ITEMS
from stub import stub

tight = Budget(3500, 500, 0.05)
p = pack(ITEMS, tight)
assert limit_of(tight) == 2825
assert p.used <= p.limit, "must fit the limit"
ids = [i.id for i in p.items]
assert "task" in ids and "system" in ids, "pinned items survive"
assert next(d for d in p.decisions if d.id == "turn-1").action == "dropped", "oldest turn goes before newer ones"
assert ids.index("system") < ids.index("task"), "stable prefix first"
turns = [i.turn for i in p.items if i.layer == "history"]
assert turns == sorted(turns), "history stays in order"
assert "30 days" in stub(render(p)).text, "answer survives correct ranking"

wrong = [replace(i, priority=10 if i.id == "doc-refunds" else 80) if i.layer == "retrieved" else i for i in ITEMS]
assert "30 days" not in stub(render(pack(wrong, tight))).text, "wrong ranking loses the answer"

try:
    pack(ITEMS, Budget(400, 100, 0))
except ValueError as e:
    assert "pinned items need" in str(e)
else:
    raise AssertionError("expected pinned items to overflow")

counted = pack(ITEMS, replace(tight, count=lambda s: estimate(s) * 2))
assert counted.used <= counted.limit, "respects an injected counter"
print("ok: all assertions passed")
