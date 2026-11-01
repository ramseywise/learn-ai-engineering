// Phase 1 runs the agent and writes rows. Phase 2 reads rows and decides. The note explains why
// these stay apart: a threshold change should not cost a model run.
import { readFileSync } from "node:fs";
import type { Agent } from "./agent.ts";

export interface Case {
  id: string;
  input: string;
  kind: string;
  critical: boolean;
  expect: { includes?: string[]; excludes?: string[]; tools?: string[] };
}
export interface Row { id: string; kind: string; critical: boolean; pass: boolean; failures: string[]; text: string; tools: string[]; tokens: number }

export const loadCases = (): Case[] =>
  readFileSync(new URL("./cases.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l));
export const loadVariants = (): Record<string, string> => JSON.parse(readFileSync(new URL("./variants.json", import.meta.url), "utf8"));

export function grade(c: Case, text: string, tools: string[]): string[] {
  const failures: string[] = [];
  for (const s of c.expect.includes ?? []) if (!text.includes(s)) failures.push(`missing "${s}"`);
  for (const s of c.expect.excludes ?? []) if (text.toLowerCase().includes(s)) failures.push(`contains "${s}"`);
  const want = c.expect.tools;
  if (want && JSON.stringify(want) !== JSON.stringify(tools)) failures.push(`tools [${tools}], wanted [${want}]`);
  return failures;
}

export async function runSuite(cases: Case[], system: string, agent: Agent): Promise<Row[]> {
  const rows: Row[] = [];
  for (const c of cases) {
    const r = await agent(system, c.input);
    const failures = grade(c, r.text, r.tools);
    rows.push({ id: c.id, kind: c.kind, critical: c.critical, pass: failures.length === 0, failures, text: r.text, tools: r.tools, tokens: r.tokens });
  }
  return rows;
}

/** Exact two-sided sign test on paired flips. Pairs that did not change carry no information. */
export function signTest(fixed: number, broken: number): number {
  const n = fixed + broken;
  if (n === 0) return 1;
  let tail = 0;
  let choose = 1;
  for (let k = 0; k <= Math.min(fixed, broken); k++) {
    tail += choose;
    choose = (choose * (n - k)) / (k + 1);
  }
  return Math.min(1, (2 * tail) / 2 ** n);
}

export interface Baseline { variant: string; passRate: number; results: Record<string, boolean> }
export interface Rules { floor: number; alpha: number }
export interface Verdict {
  pass: boolean;
  passRate: number;
  fixed: string[];
  broken: string[];
  p: number;
  criticalFailures: string[];
  reasons: string[];
  unmatched: string[];
}

export const toBaseline = (variant: string, rows: Row[]): Baseline => ({
  variant,
  passRate: rows.filter((r) => r.pass).length / rows.length,
  results: Object.fromEntries(rows.map((r) => [r.id, r.pass])),
});

/** Three gates, each with its own reason, so a red build says what to do next. */
export function assertGates(rows: Row[], baseline: Baseline, rules: Rules): Verdict {
  const passRate = rows.filter((r) => r.pass).length / rows.length;
  const compared = rows.filter((r) => r.id in baseline.results);
  const fixed = compared.filter((r) => r.pass && !baseline.results[r.id]).map((r) => r.id);
  const broken = compared.filter((r) => !r.pass && baseline.results[r.id]).map((r) => r.id);
  const p = signTest(fixed.length, broken.length);
  const criticalFailures = rows.filter((r) => r.critical && !r.pass).map((r) => r.id);
  const reasons: string[] = [];
  if (criticalFailures.length) reasons.push(`critical cases failing: ${criticalFailures.join(", ")}. Fix these, whatever the average says`);
  if (broken.length > fixed.length && p < rules.alpha) reasons.push(`regression: ${broken.length} broken, ${fixed.length} fixed, sign test p=${p.toFixed(4)}`);
  if (passRate < rules.floor) reasons.push(`pass rate ${(100 * passRate).toFixed(0)}% is under the ${(100 * rules.floor).toFixed(0)}% floor`);
  return { pass: reasons.length === 0, passRate, fixed, broken, p, criticalFailures, reasons, unmatched: rows.filter((r) => !(r.id in baseline.results)).map((r) => r.id) };
}

export function report(name: string, v: Verdict): string {
  const lines = [
    `--- ${name}: ${v.pass ? "PASS" : "FAIL"}, pass rate ${(100 * v.passRate).toFixed(0)}%`,
    `  against baseline: fixed ${v.fixed.length}, broken ${v.broken.length}, sign test p=${v.p.toFixed(4)}`,
  ];
  if (v.fixed.length) lines.push(`  fixed:  ${v.fixed.join(", ")}`);
  if (v.broken.length) lines.push(`  broken: ${v.broken.join(", ")}`);
  if (v.unmatched.length) lines.push(`  new, no baseline yet: ${v.unmatched.join(", ")}`);
  for (const r of v.reasons) lines.push(`  BLOCKED: ${r}`);
  return lines.join("\n");
}
export const RULES: Rules = { floor: 0.6, alpha: 0.05 };
