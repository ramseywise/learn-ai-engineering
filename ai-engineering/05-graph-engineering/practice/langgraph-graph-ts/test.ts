import assert from "node:assert/strict";
import { Command, MemorySaver } from "@langchain/langgraph";
import { buildGraph } from "./graph.ts";
import type { Complete } from "./model.ts";
import { stub } from "./stub.ts";

type V = { label: string; status: string; trail: string[]; evidence: { id: string }[] };
const cfg = (id: string) => ({ configurable: { thread_id: id } });
async function run(text: string, thread: string, complete: Complete = stub) {
  const saver = new MemorySaver();
  const outbox: string[] = [];
  const graph = buildGraph(complete, saver, outbox);
  await graph.invoke({ ticket: text }, cfg(thread));
  return { graph, saver, outbox };
}
const values = async (g: ReturnType<typeof buildGraph>, id: string) => (await g.getState(cfg(id))).values as V;

// Fan-out and reducer: both searches ran, both writes survived, one join.
{
  const { graph, outbox } = await run("I was charged twice, please refund it.", "a");
  const s = await graph.getState(cfg("a"));
  const v = s.values as V;
  assert.ok(v.trail.includes("search:docs") && v.trail.includes("search:tickets"));
  assert.equal(v.trail.filter((x) => x === "gather").length, 1, "the join runs once");
  assert.deepEqual(v.evidence.map((d) => d.id).sort(), ["doc-refunds", "tkt-double-charge"], "the reducer kept both");
  // Interrupt: paused before any side effect
  assert.deepEqual([...s.next], ["approve"]);
  assert.equal(outbox.length, 0, "nothing sent while waiting for a human");
}
// Durable: a different graph object resumes from the same checkpointer
{
  const { saver, outbox } = await run("I was charged twice, please refund it.", "b");
  const g2 = buildGraph(stub, saver, outbox);
  await g2.invoke(new Command({ resume: "approve" }), cfg("b"));
  assert.equal((await values(g2, "b")).status, "sent");
  assert.equal(outbox.length, 1);
}
// Denied approval escalates and sends nothing
{
  const { graph, outbox } = await run("Refund my annual plan.", "c");
  await graph.invoke(new Command({ resume: "deny" }), cfg("c"));
  assert.equal((await values(graph, "c")).status, "escalated");
  assert.equal(outbox.length, 0);
}
// Cycle: an uncited draft goes round once, then passes
{
  const { graph } = await run("The invoice page shows a blank screen.", "d");
  const v = await values(graph, "d");
  assert.equal(v.trail.filter((x) => x === "draft").length, 2);
  assert.equal(v.status, "sent");
}
// The cycle is bounded: a maker that never cites stops at MAX_DRAFTS
{
  const never: Complete = async ({ system = "" }) => ({ text: system.startsWith("CLASSIFY") ? "how_to" : "No citation.", inputTokens: 1, outputTokens: 1 });
  const { graph } = await run("How do I add a seat?", "e", never);
  const v = await values(graph, "e");
  assert.equal(v.trail.filter((x) => x === "draft").length, 2);
  assert.equal(v.status, "escalated");
}
// No evidence: no draft at all, so nothing is invented
{
  const { graph } = await run("What does your roadmap look like?", "f");
  const v = await values(graph, "f");
  assert.ok(!v.trail.includes("draft"));
  assert.equal(v.status, "escalated");
  // Threads are isolated
  assert.deepEqual((await graph.getState(cfg("other"))).values, {});
}
console.log("ok: all assertions passed");
