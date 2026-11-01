import { readFileSync } from "node:fs";
import { flips, runVariant, type Case } from "./harness.ts";
import { chooseModel } from "./model.ts";
import { stub } from "./stub.ts";
import { variants } from "./variants.ts";

const cases: Case[] = JSON.parse(readFileSync(new URL("./cases.json", import.meta.url), "utf8"));
const { name, complete } = await chooseModel(stub);
console.log(`model: ${name}, ${cases.length} cases\n`);

const results = [];
for (const v of variants) results.push(await runVariant(v, cases, complete));

const pct = (x: number) => `${(100 * x).toFixed(0)}%`.padStart(4);
console.log("variant          pass   95% CI       json  known  correct  tokens");
for (const r of results) {
  const b = r.byGrader;
  console.log(
    `${r.name.padEnd(16)} ${pct(r.passRate)}  [${pct(r.ci95[0])},${pct(r.ci95[1])}]  ${pct(b.valid_json)}  ${pct(b.known_label)}    ${pct(b.correct_label)}  ${String(r.tokens).padStart(6)}`,
  );
}
for (let i = 1; i < results.length; i++) {
  const { fixed, broken } = flips(results[i - 1], results[i]);
  console.log(`\n${results[i - 1].name} -> ${results[i].name}\n  fixed:  ${fixed.join(", ") || "none"}\n  broken: ${broken.join(", ") || "none"}`);
}
const last = results.at(-1)!;
const failing = last.results.filter((r) => Object.keys(r.failures).length);
console.log(`\nstill failing in ${last.name}: ${failing.length}`);
for (const r of failing) console.log(`  ${r.id}: ${Object.values(r.failures)[0]}`);
