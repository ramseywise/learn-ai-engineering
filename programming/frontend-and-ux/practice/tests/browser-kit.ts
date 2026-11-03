import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { chromium, type Browser, type Page } from "playwright-core";

const require = createRequire(import.meta.url);
const AXE = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

export async function launch(): Promise<Browser> {
  return chromium.launch({ headless: true });
}

export type AxeSummary = { violations: { id: string; nodes: number }[]; incomplete: string[]; passes: number };

// page.evaluate goes over the debugger protocol, so the page's CSP does not block it.
export async function runAxe(page: Page): Promise<AxeSummary> {
  await page.evaluate(AXE);
  return page.evaluate(async () => {
    const r = await (window as unknown as { axe: { run: (o: unknown) => Promise<any> } }).axe.run({
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"] },
    });
    return {
      violations: r.violations.map((v: any) => ({ id: v.id, nodes: v.nodes.length })),
      incomplete: r.incomplete.map((v: any) => v.id),
      passes: r.passes.length,
    };
  });
}
