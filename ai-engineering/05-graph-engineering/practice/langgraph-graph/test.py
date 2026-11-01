# /// script
# requires-python = ">=3.10"
# dependencies = ["langgraph>=1.0,<2"]
# ///
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from graph import build_graph
from model import Completion
from stub import stub


def run(text, thread, complete=stub, saver=None, outbox=None):
    saver = saver or MemorySaver()
    outbox = [] if outbox is None else outbox
    config = {"configurable": {"thread_id": thread}}
    graph = build_graph(complete, saver, outbox)
    graph.invoke({"ticket": text}, config)
    return graph, config, saver, outbox


# Fan-out and reducer: both searches ran, both writes survived, one join.
g, c, _, out = run("I was charged twice, please refund it.", "a")
s = g.get_state(c)
assert {"search:docs", "search:tickets"} <= set(s.values["trail"])
assert s.values["trail"].count("gather") == 1, "the join runs once"
assert {d["id"] for d in s.values["evidence"]} == {"doc-refunds", "tkt-double-charge"}, "the reducer kept both"

# Interrupt: paused before any side effect
assert s.next == ("approve",) and out == [], "nothing sent while waiting for a human"

# Durable: a different graph object resumes from the same checkpointer
_, _, saver, out = run("I was charged twice, please refund it.", "b")
g2 = build_graph(stub, saver, out)
g2.invoke(Command(resume="approve"), {"configurable": {"thread_id": "b"}})
final = g2.get_state({"configurable": {"thread_id": "b"}}).values
assert final["status"] == "sent" and len(out) == 1

# Denied approval escalates and sends nothing
g3, c3, _, out3 = run("Refund my annual plan.", "c")
g3.invoke(Command(resume="deny"), c3)
assert g3.get_state(c3).values["status"] == "escalated" and out3 == []

# Cycle: an uncited draft goes round once, then passes
g4, c4, _, _ = run("The invoice page shows a blank screen.", "d")
v = g4.get_state(c4).values
assert v["trail"].count("draft") == 2 and v["status"] == "sent"

# The cycle is bounded: a maker that never cites stops at MAX_DRAFTS
never = lambda p, system="", max_tokens=0: Completion("how_to" if system.startswith("CLASSIFY") else "No citation.", 1, 1)
g5, c5, _, _ = run("How do I add a seat?", "e", never)
v = g5.get_state(c5).values
assert v["trail"].count("draft") == 2 and v["status"] == "escalated"

# No evidence: no draft at all, so nothing is invented
g6, c6, _, _ = run("What does your roadmap look like?", "f")
v = g6.get_state(c6).values
assert "draft" not in v["trail"] and v["status"] == "escalated"

# Threads are isolated
assert g6.get_state({"configurable": {"thread_id": "other"}}).values == {}
print("ok: all assertions passed")
