// Phase 2: read results and baseline, print the verdict, exit 1 on failure. No model involved.
import { readFileSync } from "node:fs";
import { RULES, assertGates, report, type Baseline, type Row } from "./suite.ts";

const variant = process.argv[2] ?? "v1";
const rows: Row[] = readFileSync(new URL(`./results-${variant}.jsonl`, import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const baseline: Baseline = JSON.parse(readFileSync(new URL("./baseline.json", import.meta.url), "utf8"));
const verdict = assertGates(rows, baseline, RULES);
console.log(report(variant, verdict));
process.exit(verdict.pass ? 0 : 1);
