import { pack, render, estimate, type Budget, type Item } from "./budgeter.ts";
import { chooseModel } from "./model.ts";
import { items } from "./scenario.ts";
import { stub } from "./stub.ts";

const { name, complete } = await chooseModel(stub);
const total = items.reduce((n, i) => n + estimate(i.text), 0);
console.log(`model: ${name}. Unpacked context is ${total} tokens.\n`);

async function show(title: string, input: Item[], budget: Budget) {
  const p = pack(input, budget);
  console.log(`--- ${title}: window ${budget.window}, reserve ${budget.reserveOutput}, limit ${p.limit}, used ${p.used}`);
  const changed = p.decisions.filter((d) => d.action !== "kept");
  for (const d of changed) console.log(`  ${d.action.padEnd(9)} ${d.id.padEnd(12)} ${d.before} -> ${d.after}`);
  if (!changed.length) console.log("  everything kept");
  console.log("  by layer:", Object.entries(p.byLayer).map(([k, v]) => `${k} ${v}`).join(", "));
  const res = await complete({ prompt: render(p), maxTokens: budget.reserveOutput });
  console.log(`  answer: ${res.text}\n`);
}

await show("roomy", items, { window: 8000, reserveOutput: 1000, safety: 0.05 });
await show("tight", items, { window: 3500, reserveOutput: 500, safety: 0.05 });

// The same tight budget with a bad relevance ranking: the document holding the answer is
// scored lowest, so the packer drops it first and does exactly what it was told.
const misranked = items.map((i) => (i.layer === "retrieved" ? { ...i, priority: i.id === "doc-refunds" ? 10 : 80 } : i));
await show("tight, relevance ranked wrongly", misranked, { window: 3500, reserveOutput: 500, safety: 0.05 });
