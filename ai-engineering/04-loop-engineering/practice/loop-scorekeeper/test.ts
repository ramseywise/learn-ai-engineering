import assert from "node:assert/strict";
import { promptFor, runLoop, type Limits } from "./loop.ts";
import { heldOut, score, visible } from "./scorekeeper.ts";
import { gamer, honest, overfit, scripted, stuck } from "./stub.ts";

const limits: Limits = { maxIterations: 6, maxTokens: 4000, patience: 2 };
const fresh = (attempts: string[]) => scripted(attempts);

// The scorekeeper
assert.equal(score("function (s) { return s; }", visible).passed, 0);
assert.match(score("not code", visible).failures[0], /does not load/);
assert.equal(score("function (s) { while (true) {} }", visible).passed, 0, "an infinite loop is a failure, not a hang");
assert.equal(score("function (s) { throw new Error('x'); }", visible).failures.length, 4);

// Each stop reason
const a = await runLoop(honest, limits);
assert.equal(a.stop, "passed");
assert.equal(a.iterations.length, 3);
assert.ok(a.best);
const g = await runLoop(gamer, limits);
assert.equal(g.stop, "gamed");
assert.equal(g.best, null, "a gamed run ships nothing");
assert.equal((await runLoop(overfit, limits)).stop, "gamed");
const s = await runLoop(stuck, limits);
assert.equal(s.stop, "no_progress");
assert.equal(s.iterations.length, 3);
assert.equal((await runLoop(fresh(["function (s) { return 1; }"]), { ...limits, patience: 99, maxIterations: 2 })).stop, "max_iterations");
assert.equal((await runLoop(fresh(["function (s) { return 1; }"]), { ...limits, patience: 99, maxTokens: 150 })).stop, "budget");
const original = heldOut[0].want;
const t = await runLoop(fresh(["function (s) { return 1; }"]), limits, () => { heldOut[0].want = "tampered"; });
heldOut[0].want = original;
assert.equal(t.stop, "tampered");

// The maker never sees held-out inputs
const after = await runLoop(fresh(["function (s) { return s; }"]), { ...limits, maxIterations: 1 });
const p = promptFor(after.iterations[0]);
for (const c of heldOut) assert.ok(!p.includes(c.input), `held-out input leaked: ${c.input}`);
console.log("ok: all assertions passed");
