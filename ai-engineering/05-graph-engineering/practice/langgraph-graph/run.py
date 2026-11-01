# /// script
# requires-python = ">=3.10"
# dependencies = ["langgraph>=1.0,<2"]
# ///
"""Same tickets, graph and report as the TypeScript lab in ../langgraph-graph-ts."""
import json
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from graph import build_graph
from model import choose_model
from stub import stub

tickets = json.loads((Path(__file__).parent / "tickets.json").read_text())
name, complete = choose_model(stub)
print(f"model: {name}\n")

saver = MemorySaver()  # in memory: the lesson is the mechanism. Production uses a database saver.
outbox: list[str] = []
decisions = {"t2": "approve", "t5": "deny"}

for t in tickets:
    config = {"configurable": {"thread_id": t["id"]}}
    graph = build_graph(complete, saver, outbox)
    graph.invoke({"ticket": t["text"]}, config)
    pending = graph.get_state(config)
    if pending.next:
        value = pending.tasks[0].interrupts[0].value
        print(f"{t['id']} paused at {pending.next[0]}: {value['draft']}")
        print(f"   outbox holds {len(outbox)}. A new graph object resumes from the checkpoint with: {decisions[t['id']]}")
        graph = build_graph(complete, saver, outbox)  # as if the process had restarted
        graph.invoke(Command(resume=decisions[t["id"]]), config)
    s = graph.get_state(config).values
    print(f"{t['id']} [{s['label']}] {s['status']}: {' > '.join(s['trail'])} ({s['tokens']} tokens)")

print(f"\noutbox: {len(outbox)} sent")
for line in outbox:
    print(f"  {line}")
