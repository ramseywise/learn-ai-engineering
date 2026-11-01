// Every variant through both phases, in memory, against the stub. Writes nothing.
import { readFileSync } from "node:fs";
import { stubAgent } from "./agent.ts";
import { RULES, assertGates, loadCases, loadVariants, report, runSuite, type Baseline } from "./suite.ts";

const baseline: Baseline = JSON.parse(readFileSync(new URL("./baseline.json", import.meta.url), "utf8"));
const cases = loadCases();
const variants = loadVariants();
console.log(`${cases.length} cases, ${cases.filter((c) => c.critical).length} critical. Baseline: ${baseline.variant}, ${(100 * baseline.passRate).toFixed(0)}%.\n`);
for (const [name, system] of Object.entries(variants)) {
  const rows = await runSuite(cases, system, stubAgent);
  console.log(report(name, assertGates(rows, baseline, RULES)) + "\n");
}
