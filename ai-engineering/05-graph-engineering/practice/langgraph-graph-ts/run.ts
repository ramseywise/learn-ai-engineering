// Same tickets, graph and report as the Python lab in ../langgraph-graph.
import { readFileSync } from "node:fs";
import { Command, MemorySaver } from "@langchain/langgraph";
import { buildGraph } from "./graph.ts";
import { chooseModel } from "./model.ts";
import { stub } from "./stub.ts";

const tickets: { id: string; text: string }[] = JSON.parse(readFileSync(new URL("../langgraph-graph/tickets.json", import.meta.url), "utf8"));
const { name, complete } = await chooseModel(stub);
console.log(`model: ${name}\n`);

const saver = new MemorySaver(); // in memory: the lesson is the mechanism. Production uses a database saver.
const outbox: string[] = [];
const decisions: Record<string, string> = { t2: "approve", t5: "deny" };

for (const t of tickets) {
  const config = { configurable: { thread_id: t.id } };
  let graph = buildGraph(complete, saver, outbox);
  await graph.invoke({ ticket: t.text }, config);
  const pending = await graph.getState(config);
  if (pending.next.length) {
    const value = pending.tasks[0].interrupts[0].value as { draft: string };
    console.log(`${t.id} paused at ${pending.next[0]}: ${value.draft}`);
    console.log(`   outbox holds ${outbox.length}. A new graph object resumes from the checkpoint with: ${decisions[t.id]}`);
    graph = buildGraph(complete, saver, outbox); // as if the process had restarted
    await graph.invoke(new Command({ resume: decisions[t.id] }), config);
  }
  const s = (await graph.getState(config)).values as { label: string; status: string; trail: string[]; tokens: number };
  console.log(`${t.id} [${s.label}] ${s.status}: ${s.trail.join(" > ")} (${s.tokens} tokens)`);
}

console.log(`\noutbox: ${outbox.length} sent`);
for (const line of outbox) console.log(`  ${line}`);
