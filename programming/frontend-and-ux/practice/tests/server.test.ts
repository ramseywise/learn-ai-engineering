import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { DOCS, SCENARIOS } from "../server/mock-server.ts";
import { SseParser } from "../solutions/sse.ts";
import { listen } from "./helpers.ts";

let m: Awaited<ReturnType<typeof listen>>;
before(async () => { m = await listen(null, 1); });
after(() => { m.server.closeAllConnections(); m.server.close(); });

const post = (path: string, body: unknown) =>
  fetch(m.url + path, { method: "POST", body: JSON.stringify(body) });

async function events(scenario: string) {
  const res = await post("/api/chat", { question: `q-${scenario}`, scenario });
  const p = new SseParser();
  const out = [];
  try {
    for await (const chunk of res.body!) out.push(...p.push(chunk));
  } catch { /* the dropped scenario ends this way */ }
  out.push(...p.end());
  return { res, out };
}

test("the answer stream has the headers a streaming response needs", async () => {
  const { res } = await events("answer");
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type")!, /^text\/event-stream/);
  assert.equal(res.headers.get("cache-control"), "no-cache");
});

test("every quote the server cites appears in the document it links to", async () => {
  for (const s of ["answer", "uncertain", "truncated", "mid-stream-error"]) {
    const { out } = await events(s);
    const cites = out.filter((e) => e.event === "citation").map((e) => JSON.parse(e.data));
    assert.ok(cites.length > 0, s);
    for (const c of cites) {
      const page = await (await fetch(m.url + c.url.split("#")[0])).text();
      assert.ok(page.includes(c.quote), `${s}: ${c.quote}`);
      assert.ok(page.includes(`id="${c.url.split("#")[1]}"`), `${s}: anchor`);
    }
  }
});

test("mid-stream failure is a 200 followed by an error event", async () => {
  const { res, out } = await events("mid-stream-error");
  assert.equal(res.status, 200);
  assert.equal(out.at(-1)!.event, "error");
  assert.ok(out.some((e) => e.event === "delta"));
});

test("dropped and clean-eof streams have no terminal event", async () => {
  for (const s of ["dropped", "clean-eof"]) {
    const { out } = await events(s);
    assert.ok(!out.some((e) => e.event === "done" || e.event === "error"), s);
  }
});

test("busy-once fails once with retry-after, then answers", async () => {
  const body = { question: "same", scenario: "busy-once" };
  const first = await post("/api/chat", body);
  assert.equal(first.status, 503);
  assert.equal(first.headers.get("retry-after"), "2");
  const second = await post("/api/chat", body);
  assert.equal(second.status, 200);
  await second.text();
});

test("bad requests are 4xx and leave no stream open", async () => {
  assert.equal((await post("/api/chat", { question: "  " })).status, 400);
  assert.equal((await post("/api/chat", { question: "x", scenario: "nope" })).status, 400);
  assert.equal((await fetch(m.url + "/api/chat", { method: "POST", body: "{" })).status, 400);
  assert.equal((await post("/api/chat", { question: "x".repeat(70_000) })).status, 413);
});

test("every response carries a content security policy", async () => {
  for (const path of ["/", "/docs/refunds", "/missing"]) {
    assert.match((await fetch(m.url + path)).headers.get("content-security-policy")!, /script-src 'self'/);
  }
});

test("handoff returns a ticket and records what it was given", async () => {
  const res = await post("/api/handoff", { question: "q", answer: "a" });
  assert.match(((await res.json()) as { ticket: string }).ticket, /^H-\d+$/);
  assert.deepEqual(m.stats.handoffs.at(-1), { question: "q", answer: "a" });
  assert.equal((await post("/api/handoff", { scenario: "handoff-down" })).status, 503);
});

test("every doc has passages and the answer scenario exists", async () => {
  for (const doc of Object.values(DOCS)) assert.ok(Object.keys(doc.passages).length > 0);
  assert.ok(SCENARIOS.includes("answer"));
});
