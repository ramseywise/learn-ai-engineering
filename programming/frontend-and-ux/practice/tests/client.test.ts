// The fetch loop against the real mock server, in Node, without a browser.
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { ask, safeHref } from "../solutions/client.ts";
import { initialState, reducer } from "../solutions/state.ts";
import type { Action, Exchange, State } from "../solutions/state.ts";
import { listen } from "./helpers.ts";

let m: Awaited<ReturnType<typeof listen>>;
before(async () => { m = await listen(null, 1); });
after(() => { m.server.closeAllConnections(); m.server.close(); });

let n = 0;
async function run(scenario: string, opts: { stallMs?: number; slowMs?: number; abortAfterMs?: number } = {}) {
  const id = `c${++n}`;
  const question = `q ${id}`;
  let state: State = reducer(initialState, { type: "submit", id, question });
  const seen: Action[] = [];
  const controller = new AbortController();
  if (opts.abortAfterMs) setTimeout(() => controller.abort(), opts.abortAfterMs);
  await ask({
    id, question, scenario,
    url: `${m.url}/api/chat`,
    signal: controller.signal,
    dispatch: (a) => { seen.push(a); state = reducer(state, a); },
    ...opts,
  });
  return { live: state.live as Exchange & Record<string, unknown>, seen };
}

test("a normal answer ends complete, with text and citations", async () => {
  const { live } = await run("answer");
  assert.equal(live.status, "complete");
  assert.match(live.text as string, /30 days \[1\]/);
  assert.equal((live.citations as unknown[]).length, 3);
});

test("each server outcome reaches the matching state", async () => {
  const expected: Record<string, [string, string?]> = {
    uncertain: ["uncertain"],
    "no-evidence": ["uncertain"],
    "dangling-citation": ["uncertain"],
    truncated: ["truncated"],
    refusal: ["refused"],
    "busy-always": ["error", "busy"],
    "proxy-login-page": ["error", "protocol"],
    "server-error": ["error", "server"],
    "mid-stream-error": ["error", "server"],
    dropped: ["error", "dropped"],
    "clean-eof": ["error", "dropped"],
  };
  for (const [scenario, [status, kind]] of Object.entries(expected)) {
    const { live } = await run(scenario);
    assert.equal(live.status, status, scenario);
    if (kind) assert.equal(live.kind, kind, scenario);
  }
});

test("a rejected request is not offered as retryable", async () => {
  const { live } = await run("no-such-scenario");
  assert.equal(live.status, "error");
  assert.equal(live.kind, "rejected");
  assert.equal(live.retryable, false);
});

test("retry-after reaches the state", async () => {
  assert.equal((await run("busy-always")).live.retryAfterS, 30);
});

test("the partial text survives a failure", async () => {
  assert.match((await run("mid-stream-error")).live.text as string, /refunded in full/);
});

test("silence trips the stall watchdog and closes the connection", async () => {
  const { live } = await run("stalled", { stallMs: 100 });
  assert.equal(live.kind, "stalled");
  assert.match(live.text as string, /Annual plans/);
});

test("keep-alive comments hold the watchdog off during a slow start", async () => {
  const { live, seen } = await run("slow-start", { stallMs: 500, slowMs: 200 });
  assert.equal(live.status, "complete");
  assert.ok(seen.some((a) => a.type === "slow"), "the slow signal fired");
});

test("abort becomes stopped, not an error, and the server sees the client go", async () => {
  const { live } = await run("slow-start", { abortAfterMs: 100 });
  assert.equal(live.status, "stopped");
  await new Promise((r) => setTimeout(r, 50));
  assert.equal(m.stats.lastClientGone, true);
});

test("only http and https become links", () => {
  const base = "http://x.test/a";
  assert.equal(safeHref("/docs/r#w", base), "http://x.test/docs/r#w");
  assert.equal(safeHref("https://y.test/", base), "https://y.test/");
  for (const bad of ["javascript:alert(1)", " JaVaScRiPt:alert(1)", "data:text/html,x", "vbscript:x", "http://[bad"]) {
    assert.equal(safeHref(bad, base), undefined, bad);
  }
});

test("a fetch that rejects before any response is a network failure, not a dropped stream", async () => {
  const closed = await listen(null, 1);
  const url = `${closed.url}/api/chat`;
  closed.server.closeAllConnections();
  await new Promise((r) => closed.server.close(r));
  const seen: Action[] = [];
  await ask({ id: "n1", question: "q", scenario: "answer", url, signal: new AbortController().signal, dispatch: (a) => seen.push(a) });
  const fail = seen.find((a) => a.type === "fail");
  assert.equal(fail?.type === "fail" ? fail.kind : null, "network");
});
