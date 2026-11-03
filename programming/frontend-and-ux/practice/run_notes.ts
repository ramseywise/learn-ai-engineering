// Runs the code in the track's notes, so a note cannot drift from what it prints.
//
//   ts, js    run in Node. A ```text fence straight after is the expected stdout.
//   html      loaded in Chromium; console output is compared the same way, and
//             an uncaught exception fails the block.
//   tsx       bundled with React, `export default` mounted in Chromium; the
//             rendered text is compared with a following ```text fence.
//   css       parsed by esbuild.
//   text, mermaid, http, sh and anything else are not run.
//
// Put <!-- no-run: why --> on the line before a fence to skip it; skips are counted.
// Usage: node run_notes.ts [--no-browser]
import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build, transform } from "esbuild";
import type { Browser } from "playwright-core";
import { launch } from "./tests/browser-kit.ts";

const here = dirname(fileURLToPath(import.meta.url));
const notesDir = resolve(here, "../notes");
const work = resolve(here, ".out/notes");
mkdirSync(work, { recursive: true });
const noBrowser = process.argv.includes("--no-browser");

type Block = { file: string; line: number; lang: string; code: string; expected?: string; skip?: string };

function blocks(file: string): Block[] {
  const lines = readFileSync(resolve(notesDir, file), "utf8").split("\n");
  const found: Block[] = [];
  for (let i = 0; i < lines.length; i++) {
    const open = lines[i]!.match(/^```(\w*)\s*$/);
    if (!open) continue;
    const start = i + 1;
    let end = start;
    while (lines[end] !== "```") end++;
    const prev = lines[i - 1]?.match(/<!-- no-run: (.+) -->/);
    const block: Block = { file, line: start, lang: open[1]!, code: lines.slice(start, end).join("\n") };
    if (prev) block.skip = prev[1];
    let next = end + 1;
    while (lines[next]?.trim() === "") next++;
    if (lines[next] === "```text") {
      let close = next + 1;
      while (lines[close] !== "```") close++;
      block.expected = lines.slice(next + 1, close).join("\n");
    }
    found.push(block);
    i = end;
  }
  return found;
}

function compare(b: Block, got: string): string | null {
  if (b.expected === undefined) return null;
  if (got.trim() === b.expected.trim()) return null;
  return `printed:\n${got.trim()}\nthe note says:\n${b.expected.trim()}`;
}

let browser: Browser | undefined;
async function page() {
  browser ??= await launch();
  const p = await browser.newPage();
  const logs: string[] = [];
  const errors: string[] = [];
  p.on("console", (m) => (m.type() === "error" ? errors : logs).push(m.text()));
  p.on("pageerror", (e) => errors.push(String(e)));
  return { p, logs, errors };
}

async function run(b: Block, n: number): Promise<string | null> {
  if (b.lang === "ts" || b.lang === "js") {
    const path = resolve(work, `block-${n}.${b.lang === "ts" ? "ts" : "mjs"}`);
    writeFileSync(path, b.code);
    const r = spawnSync(process.execPath, [path], { encoding: "utf8", timeout: 15000 });
    if (r.status !== 0) return `exit ${r.status}\n${r.stderr}`;
    return compare(b, r.stdout);
  }
  if (b.lang === "css") {
    await transform(b.code, { loader: "css" });
    return null;
  }
  if (b.lang === "html") {
    const { p, logs, errors } = await page();
    await p.setContent(b.code, { waitUntil: "load" });
    await p.close();
    if (errors.length) return errors.join("\n");
    return compare(b, logs.join("\n"));
  }
  if (b.lang === "tsx") {
    const path = resolve(work, `block-${n}.tsx`);
    const entry = resolve(work, `entry-${n}.tsx`);
    const out = resolve(work, `bundle-${n}.js`);
    writeFileSync(path, b.code);
    writeFileSync(entry, `import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import App from "./block-${n}.tsx";
flushSync(() => createRoot(document.getElementById("root")!).render(<App />));`);
    await build({ entryPoints: [entry], bundle: true, outfile: out, format: "iife", jsx: "automatic",
      define: { "process.env.NODE_ENV": '"development"' }, logLevel: "silent" });
    const { p, errors } = await page();
    await p.setContent('<!doctype html><div id="root"></div>');
    await p.addScriptTag({ path: out });
    await p.waitForTimeout(50); // let effects and any state they set settle
    const shown = await p.locator("#root").innerText();
    await p.close();
    if (errors.length) return errors.join("\n");
    return compare(b, shown);
  }
  return null;
}

const runnable = new Set(["ts", "js", "css", "html", "tsx"]);
let ran = 0, compared = 0, skipped = 0, unbrowsed = 0, failed = 0, n = 0;
const files = readdirSync(notesDir).filter((f) => f.endsWith(".md")).sort();
for (const file of files) {
  for (const b of blocks(file)) {
    n++;
    if (!runnable.has(b.lang)) continue;
    if (b.skip) { skipped++; continue; }
    if (noBrowser && (b.lang === "html" || b.lang === "tsx")) { unbrowsed++; continue; }
    const problem = await run(b, n);
    ran++;
    if (b.expected !== undefined) compared++;
    if (problem) {
      failed++;
      console.error(`FAIL  ${file}:${b.line} (${b.lang})\n${problem}\n`);
    }
  }
}
await browser?.close();
console.log(`${ran} blocks run from ${files.length} notes, ${compared} with output compared, ${skipped} marked no-run, ${unbrowsed} browser blocks not run, ${failed} failed`);
process.exit(failed || files.length === 0 ? 1 : 0);
