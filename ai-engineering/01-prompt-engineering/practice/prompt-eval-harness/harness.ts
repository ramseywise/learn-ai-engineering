import type { Complete } from "./model.ts";

export interface Case { id: string; ticket: string; label: string }
export interface Variant { name: string; system?: string; render: (ticket: string) => string }

export const LABELS = ["billing", "account", "bug", "how_to"];

/** A grader returns null on pass, or the reason for failing. */
export type Grader = (output: string, c: Case) => string | null;

/** Parses the output as {"label": ...}. Prose around the JSON is a failure: downstream code parses this. */
export function parseLabel(output: string): string | null {
  try {
    const v = JSON.parse(output.trim());
    return typeof v?.label === "string" ? v.label : null;
  } catch {
    return null;
  }
}

export const graders: Record<string, Grader> = {
  valid_json: (o) => (parseLabel(o) === null ? "not JSON with a string `label`" : null),
  known_label: (o) => {
    const l = parseLabel(o);
    return l !== null && LABELS.includes(l) ? null : `label outside the set: ${l}`;
  },
  correct_label: (o, c) => {
    const l = parseLabel(o);
    return l === c.label ? null : `wanted ${c.label}, got ${l}`;
  },
};

export interface CaseResult { id: string; failures: Record<string, string>; output: string }
export interface VariantResult {
  name: string;
  results: CaseResult[];
  passRate: number;
  ci95: [number, number];
  byGrader: Record<string, number>;
  tokens: number;
}

/** Wilson interval: stays honest at small n, where a plain +/- would leave [0, 1]. */
export function wilson(k: number, n: number, z = 1.96): [number, number] {
  if (n === 0) return [0, 1];
  const p = k / n;
  const d = 1 + (z * z) / n;
  const mid = (p + (z * z) / (2 * n)) / d;
  const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / d;
  return [Math.max(0, mid - half), Math.min(1, mid + half)];
}

export async function runVariant(v: Variant, cases: Case[], complete: Complete): Promise<VariantResult> {
  const results: CaseResult[] = [];
  let tokens = 0;
  for (const c of cases) {
    const res = await complete({ system: v.system, prompt: v.render(c.ticket), maxTokens: 256 });
    tokens += res.inputTokens + res.outputTokens;
    const failures: Record<string, string> = {};
    for (const [name, grade] of Object.entries(graders)) {
      const why = grade(res.text, c);
      if (why) failures[name] = why;
    }
    results.push({ id: c.id, failures, output: res.text });
  }
  const passed = results.filter((r) => Object.keys(r.failures).length === 0).length;
  const byGrader = Object.fromEntries(
    Object.keys(graders).map((g) => [g, results.filter((r) => !(g in r.failures)).length / results.length]),
  );
  return { name: v.name, results, passRate: passed / results.length, ci95: wilson(passed, results.length), byGrader, tokens };
}

/** Cases where the second variant changed the outcome. Aggregates hide these. */
export function flips(a: VariantResult, b: VariantResult): { fixed: string[]; broken: string[] } {
  const ok = (r: CaseResult) => Object.keys(r.failures).length === 0;
  const fixed: string[] = [];
  const broken: string[] = [];
  a.results.forEach((r, i) => {
    if (!ok(r) && ok(b.results[i])) fixed.push(r.id);
    if (ok(r) && !ok(b.results[i])) broken.push(r.id);
  });
  return { fixed, broken };
}
