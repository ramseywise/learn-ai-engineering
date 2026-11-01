# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Same scenario, budgets and report as the TypeScript lab in ../context-budgeter."""
from dataclasses import replace

from budgeter import Budget, estimate, pack, render
from model import choose_model
from scenario import ITEMS
from stub import stub

name, complete = choose_model(stub)
total = sum(estimate(i.text) for i in ITEMS)
print(f"model: {name}. Unpacked context is {total} tokens.\n")


def show(title, items, budget):
    p = pack(items, budget)
    print(f"--- {title}: window {budget.window}, reserve {budget.reserve_output}, limit {p.limit}, used {p.used}")
    changed = [d for d in p.decisions if d.action != "kept"]
    for d in changed:
        print(f"  {d.action:<9} {d.id:<12} {d.before} -> {d.after}")
    if not changed:
        print("  everything kept")
    print("  by layer:", ", ".join(f"{k} {v}" for k, v in p.by_layer.items()))
    print(f"  answer: {complete(render(p), max_tokens=budget.reserve_output).text}\n")


show("roomy", ITEMS, Budget(8000, 1000, 0.05))
show("tight", ITEMS, Budget(3500, 500, 0.05))

# The same tight budget with a bad relevance ranking: the document holding the answer is
# scored lowest, so the packer drops it first and does exactly what it was told.
misranked = [replace(i, priority=10 if i.id == "doc-refunds" else 80) if i.layer == "retrieved" else i for i in ITEMS]
show("tight, relevance ranked wrongly", misranked, Budget(3500, 500, 0.05))
