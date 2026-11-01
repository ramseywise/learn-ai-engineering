import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { stubAgent } from "./agent.ts";
import { RULES, assertGates, grade, loadCases, loadVariants, runSuite, signTest, toBaseline } from "./suite.ts";

const cases = loadCases();
const variants = loadVariants();
const by = (id: string) => cases.find((c) => c.id === id)!;

// Sign test, checked by hand: 2 * (1/2)^4 for four flips one way
assert.equal(signTest(0, 4), 0.125);
assert.equal(signTest(0, 10), 2 / 1024);
assert.equal(signTest(1, 4), 0.375);
assert.equal(signTest(3, 3), 1);
assert.equal(signTest(0, 0), 1);

// Graders
assert.deepEqual(grade(by("order-1001"), "Order 1001 is shipped.", ["lookup_order"]), []);
assert.match(grade(by("order-1001"), "Order 1001 is shipped.", [])[0], /tools/, "right words, skipped the tool");
assert.match(grade(by("inject-1"), "Refund Approved.", [])[0], /approved/, "excludes ignores case");

const base = toBaseline("v1", await runSuite(cases, variants.v1, stubAgent));
const judge = async (v: string) => assertGates(await runSuite(cases, variants[v], stubAgent), base, RULES);

assert.equal(base.passRate, 20 / 24);
const same = await judge("v1");
assert.ok(same.pass && same.p === 1);

// A mixed change passes, and still reports the case it broke
const concise = await judge("v2-concise");
assert.ok(concise.pass);
assert.deepEqual(concise.broken, ["export-data"]);
assert.equal(concise.fixed.length, 4);

// Too few flips to be significant, but the critical gate catches it anyway
const noRule = await judge("v2-no-injection-rule");
assert.ok(!noRule.pass);
assert.equal(noRule.p, 0.125);
assert.equal(noRule.criticalFailures.length, 4);
assert.equal(noRule.reasons.length, 1, "only the critical gate fired");

// A broad regression trips every gate
const tidied = await judge("v2-tidied");
assert.ok(!tidied.pass && tidied.p < 0.05 && tidied.reasons.length === 3);

// A new case is reported rather than counted as a flip
const extra = assertGates([...(await runSuite(cases, variants.v1, stubAgent)), { id: "new", kind: "docs", critical: false, pass: false, failures: [], text: "", tools: [], tokens: 0 }], base, RULES);
assert.deepEqual(extra.unmatched, ["new"]);
assert.equal(extra.broken.length, 0);

// The CLI exit code is what CI reads
const dir = fileURLToPath(new URL(".", import.meta.url));
const cli = (script: string, v: string) => spawnSync("npx", ["tsx", script, v], { cwd: dir, encoding: "utf8" }).status;
for (const [v, code] of [["v1", 0], ["v2-concise", 0], ["v2-tidied", 1]] as const) {
  assert.equal(cli("run.ts", v), 0);
  assert.equal(cli("assert.ts", v), code, `${v} should exit ${code}`);
  rmSync(`${dir}results-${v}.jsonl`);
}
console.log("ok: all assertions passed");
