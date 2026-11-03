import { test } from "node:test";
import assert from "node:assert/strict";
import type { Action, Exchange, State } from "../solutions/state.ts";

const target = process.env.TARGET ?? "solutions";
const { reducer, initialState, isBusy, danglingMarkers, citedSources, markers } = await import(`../${target}/state.ts`);

const run = (actions: Action[], from: State = initialState): State => actions.reduce(reducer, from);
const live = (s: State) => s.live as Extract<Exchange, { status: "streaming" }> & Record<string, unknown>;
const cit = (id: number) => ({ id, title: `t${id}`, url: `/d#${id}`, quote: `q${id}` });
const ask: Action = { type: "submit", id: "a", question: "q" };
const text = (t: string): Action => ({ type: "delta", id: "a", text: t });

test("submit goes to waiting, first delta goes to streaming", () => {
  assert.equal(run([ask]).live.status, "waiting");
  assert.equal(run([ask, text("x")]).live.status, "streaming");
  assert.equal(isBusy(run([ask]).live), true);
});

test("slow only changes waiting", () => {
  assert.equal((run([ask, { type: "slow", id: "a" }]).live as { slow: boolean }).slow, true);
  const streaming = run([ask, text("x")]);
  assert.equal(reducer(streaming, { type: "slow", id: "a" }), streaming, "streaming state is returned unchanged");
});

test("deltas append in order and citations keep arriving during streaming", () => {
  const s = run([ask, text("a"), { type: "citation", id: "a", citation: cit(1) }, text("b")]);
  assert.equal(live(s).text, "ab");
  assert.equal(live(s).citations.length, 1);
  assert.equal(run([ask, { type: "citation", id: "a", citation: cit(1) }]).live.status, "waiting", "a citation is not yet text");
});

test("markers finds whole bracketed numbers and nothing else", () => {
  assert.deepEqual(markers("a [1] b [12] in 2026, not [x] or [3"), [1, 12]);
});

test("a repeated citation id is ignored", () => {
  const c: Action = { type: "citation", id: "a", citation: cit(1) };
  assert.equal(live(run([ask, c, c])).citations.length, 1);
});

test("strong evidence with every marker backed is complete", () => {
  const s = run([ask, { type: "citation", id: "a", citation: cit(1) }, text("x [1]"), { type: "done", id: "a", stop: "end", evidence: "strong" }]);
  assert.equal(s.live.status, "complete");
});

test("weak and missing evidence are uncertain, whatever the text claims", () => {
  for (const [evidence, reason] of [["weak", "weak-evidence"], ["none", "no-evidence"]] as const) {
    const s = run([ask, text("confident claim"), { type: "done", id: "a", stop: "end", evidence }]);
    assert.equal(s.live.status, "uncertain");
    assert.equal((s.live as { reason: string }).reason, reason);
  }
});

test("a marker with no source downgrades a confident answer", () => {
  const s = run([ask, { type: "citation", id: "a", citation: cit(1) }, text("a [1] b [4]"), { type: "done", id: "a", stop: "end", evidence: "strong" }]);
  assert.equal((s.live as { reason: string }).reason, "unsupported-citation");
  assert.deepEqual(danglingMarkers("a [1] b [4] c [4]", [cit(1)]), [4]);
});

test("an answer with no markers at all is unsupported", () => {
  const s = run([ask, text("plain claim"), { type: "done", id: "a", stop: "end", evidence: "strong" }]);
  assert.equal(s.live.status, "uncertain");
});

test("retrieved but unused sources are not listed", () => {
  assert.deepEqual(citedSources("x [2]", [cit(1), cit(2)]).map((c: { id: number }) => c.id), [2]);
});

test("length and refusal stops are their own states", () => {
  assert.equal(run([ask, text("x"), { type: "done", id: "a", stop: "length", evidence: "strong" }]).live.status, "truncated");
  assert.equal(run([ask, text("x"), { type: "done", id: "a", stop: "length", evidence: "weak" }]).live.status, "truncated", "cut off comes before weak evidence");
  assert.equal(run([ask, text("x"), { type: "done", id: "a", stop: "refusal", evidence: "none" }]).live.status, "refused");
});

test("a failure keeps the partial text and the question", () => {
  const s = run([ask, text("partial"), { type: "fail", id: "a", kind: "dropped", retryable: true }]);
  assert.equal(s.live.status, "error");
  assert.equal(live(s).text, "partial");
  assert.equal(live(s).question, "q");
});

test("a stop keeps the partial text", () => {
  const s = run([ask, text("partial"), { type: "stopped", id: "a" }]);
  assert.equal(s.live.status, "stopped");
  assert.equal(live(s).text, "partial");
});

test("retry-after survives into state", () => {
  const s = run([ask, { type: "fail", id: "a", kind: "busy", retryable: true, retryAfterS: 30 }]);
  assert.equal((s.live as { retryAfterS: number }).retryAfterS, 30);
});

test("late events from an abandoned request change nothing", () => {
  const stale: Action[] = [
    { type: "delta", id: "old", text: "stale" },
    { type: "citation", id: "old", citation: cit(9) },
    { type: "done", id: "old", stop: "end", evidence: "strong" },
    { type: "fail", id: "old", kind: "dropped", retryable: true },
    { type: "stopped", id: "old" },
  ];
  const s = run([ask, text("fresh")]);
  for (const a of stale) assert.equal(reducer(s, a), s, a.type);
});

test("events after the end change nothing", () => {
  const s = run([ask, { type: "stopped", id: "a" }]);
  assert.equal(reducer(s, text("late")), s);
});

test("a second submit while busy is ignored", () => {
  const s = run([ask]);
  assert.equal(reducer(s, { type: "submit", id: "b", question: "r" }), s);
});

test("a new question moves the last one into history, a retry replaces it", () => {
  const failed = run([ask, text("p"), { type: "fail", id: "a", kind: "server", retryable: true }]);
  assert.equal(reducer(failed, { type: "submit", id: "b", question: "r" }).history.length, 1);
  assert.equal(reducer(failed, { type: "submit", id: "b", question: "q", replace: true }).history.length, 0);
});

test("handoff runs none, sending, sent and resets on a new question", () => {
  const done = run([ask, text("x"), { type: "stopped", id: "a" }]);
  const sending = reducer(done, { type: "handoff-start" });
  assert.equal(sending.handoff.status, "sending");
  const sent = reducer(sending, { type: "handoff-sent", ticket: "H-1" });
  assert.deepEqual(sent.handoff, { status: "sent", ticket: "H-1" });
  const next = reducer(sent, { type: "submit", id: "b", question: "r" });
  assert.equal(next.handoff.status, "none");
  assert.equal(reducer(next, { type: "handoff-sent", ticket: "H-2" }), next, "a late reply cannot mark the new question as sent");
  assert.equal(reducer(next, { type: "handoff-failed" }), next);
  assert.equal(reducer(initialState, { type: "handoff-start" }), initialState, "nothing to hand off yet");
});

test("handoff cannot start while an answer is streaming, and can fail", () => {
  const s = run([ask, text("x")]);
  assert.equal(reducer(s, { type: "handoff-start" }), s);
  const done = run([ask, text("x"), { type: "stopped", id: "a" }, { type: "handoff-start" }]);
  assert.equal(reducer(done, { type: "handoff-failed" }).handoff.status, "failed");
});
