// Phase 1: run one variant and write results-<variant>.jsonl.  npx tsx run.ts v1 [--write-baseline]
import { writeFileSync } from "node:fs";
import { chooseAgent } from "./agent.ts";
import { loadCases, loadVariants, runSuite, toBaseline } from "./suite.ts";

const variant = process.argv[2] ?? "v1";
const system = loadVariants()[variant];
if (!system) throw new Error(`unknown variant: ${variant}`);
const { name, agent } = await chooseAgent();
const rows = await runSuite(loadCases(), system, agent);
writeFileSync(new URL(`./results-${variant}.jsonl`, import.meta.url), rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
console.log(`${name}, ${variant}: ${rows.filter((r) => r.pass).length}/${rows.length} passed, wrote results-${variant}.jsonl`);
if (process.argv.includes("--write-baseline")) {
  writeFileSync(new URL("./baseline.json", import.meta.url), JSON.stringify(toBaseline(variant, rows), null, 2) + "\n");
  console.log("wrote baseline.json");
}
