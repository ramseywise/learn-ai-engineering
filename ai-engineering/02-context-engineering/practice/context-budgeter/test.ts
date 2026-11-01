import assert from "node:assert/strict";
import { estimate, limitOf, pack, render, type Budget } from "./budgeter.ts";
import { items } from "./scenario.ts";
import { stub } from "./stub.ts";

const tight: Budget = { window: 3500, reserveOutput: 500, safety: 0.05 };
const p = pack(items, tight);
assert.equal(limitOf(tight), 2825);
assert.ok(p.used <= p.limit, "must fit the limit");
assert.ok(p.items.some((i) => i.id === "task") && p.items.some((i) => i.id === "system"), "pinned items survive");
assert.equal(p.decisions.find((d) => d.id === "turn-1")!.action, "dropped", "oldest turn goes before newer ones");
assert.ok(p.items.findIndex((i) => i.id === "system") < p.items.findIndex((i) => i.id === "task"), "stable prefix first");

const turns = p.items.filter((i) => i.layer === "history").map((i) => i.turn!);
assert.deepEqual(turns, [...turns].sort((a, b) => a - b), "history stays in order");

assert.match((await stub({ prompt: render(p) })).text, /30 days/, "answer survives correct ranking");

const wrong = items.map((i) => (i.layer === "retrieved" ? { ...i, priority: i.id === "doc-refunds" ? 10 : 80 } : i));
assert.doesNotMatch((await stub({ prompt: render(pack(wrong, tight)) })).text, /30 days/, "wrong ranking loses the answer");

assert.throws(() => pack(items, { window: 400, reserveOutput: 100, safety: 0 }), /pinned items need/);

const counted = pack(items, { ...tight, count: (s) => estimate(s) * 2 });
assert.ok(counted.used <= counted.limit, "respects an injected counter");
console.log("ok: all assertions passed");
