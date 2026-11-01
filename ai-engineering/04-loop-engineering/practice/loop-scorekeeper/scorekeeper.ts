import { createHash } from "node:crypto";
import { createContext, Script } from "node:vm";

export interface Check { input: string; want: string }
export interface Score { passed: number; total: number; failures: string[] }

/** The task: a slugify function. The maker sees `visible`. It never sees `heldOut`. */
export const visible: Check[] = [
  { input: "Hello World", want: "hello-world" },
  { input: "  Trim me  ", want: "trim-me" },
  { input: "Already-slugged", want: "already-slugged" },
  { input: "Rock & Roll!", want: "rock-roll" },
];
export const heldOut: Check[] = [
  { input: "Crème Brûlée", want: "creme-brulee" },
  { input: "a---b", want: "a-b" },
  { input: "!!!", want: "" },
  { input: "Mixed_Case 42", want: "mixed-case-42" },
];

/**
 * Deterministic: the same code gets the same score, and no model is asked its opinion. The
 * candidate runs in a vm context with a timeout, so an infinite loop costs one failed iteration.
 * vm is not a security boundary. It stops accidents, not attackers.
 */
export function score(code: string, checks: Check[]): Score {
  const failures: string[] = [];
  let fn: (s: string) => string;
  const ctx = createContext({});
  try {
    fn = new Script(`(${code})`).runInContext(ctx, { timeout: 200 });
    if (typeof fn !== "function") throw new Error("not a function");
  } catch (e: any) {
    return { passed: 0, total: checks.length, failures: [`does not load: ${e.message}`] };
  }
  let passed = 0;
  for (const c of checks) {
    ctx.fn = fn;
    ctx.input = c.input;
    try {
      const got = new Script("fn(input)").runInContext(ctx, { timeout: 200 });
      if (got === c.want) passed++;
      else failures.push(`slugify(${JSON.stringify(c.input)}) gave ${JSON.stringify(got)}, wanted ${JSON.stringify(c.want)}`);
    } catch (e: any) {
      failures.push(`slugify(${JSON.stringify(c.input)}) threw: ${e.message}`);
    }
  }
  return { passed, total: checks.length, failures };
}

/** Fingerprints the checks. If they change during a run, the maker moved the goalposts. */
export const fingerprint = () => createHash("sha256").update(JSON.stringify([visible, heldOut])).digest("hex");
