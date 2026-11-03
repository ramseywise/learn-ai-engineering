import { test } from "node:test";
import assert from "node:assert/strict";

const target = process.env.TARGET ?? "solutions";
const { SseParser } = await import(`../${target}/sse.ts`);
type E = { event: string; data: string; id?: string };
const enc = new TextEncoder();

function all(...chunks: (string | Uint8Array)[]): E[] {
  const p = new SseParser();
  const out: E[] = [];
  for (const c of chunks) out.push(...p.push(c));
  out.push(...p.end());
  return out;
}

test("a named event with one data line", () => {
  assert.deepEqual(all("event: delta\ndata: hi\n\n"), [{ event: "delta", data: "hi" }]);
});

test("no event name means message", () => {
  assert.deepEqual(all("data: hi\n\n"), [{ event: "message", data: "hi" }]);
});

test("several data lines join with one newline", () => {
  assert.deepEqual(all("data: a\ndata: b\n\n")[0]!.data, "a\nb");
});

test("LF, CRLF and bare CR all end a line", () => {
  for (const nl of ["\n", "\r\n", "\r"]) {
    assert.deepEqual(all(`event: x${nl}data: y${nl}${nl}`, "\n"), [{ event: "x", data: "y" }], JSON.stringify(nl));
  }
});

test("a bare CR as the very last byte still ends the line", () => {
  assert.deepEqual(all("data: x\r\r"), [{ event: "message", data: "x" }]);
});

test("comments are ignored and dispatch nothing", () => {
  assert.deepEqual(all(": keep-alive\n\n: more\n\n"), []);
});

test("only one leading space is stripped from a value", () => {
  assert.equal(all("data:  two\n\n")[0]!.data, " two");
  assert.equal(all("data:none\n\n")[0]!.data, "none");
});

test("a field with no colon has an empty value", () => {
  assert.equal(all("data\n\n")[0]!.data, "");
});

test("unknown fields are ignored", () => {
  assert.deepEqual(all("wat: 1\ndata: x\n\n"), [{ event: "message", data: "x" }]);
});

test("event type with no data dispatches nothing and does not leak", () => {
  assert.deepEqual(all("event: ghost\n\ndata: real\n\n"), [{ event: "message", data: "real" }]);
  assert.equal(all("event: a\ndata: x\n\ndata: y\n\n")[1]!.event, "message", "the type resets after a dispatch too");
});

test("an id persists across events, as the last event ID does", () => {
  const out = all("id: 7\ndata: a\n\ndata: b\n\n");
  assert.equal(out[0]!.id, "7");
  assert.equal(out[1]!.id, "7");
});

test("an id containing NULL is ignored", () => {
  assert.equal(all("id: a\0b\ndata: x\n\n")[0]!.id, undefined);
});

test("an event with no closing blank line is discarded at end of stream", () => {
  assert.deepEqual(all("data: complete\n\ndata: half"), [{ event: "message", data: "complete" }]);
  assert.deepEqual(all("event: done\ndata: {}\n"), []);
});

test("a leading byte order mark is ignored", () => {
  const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
  assert.deepEqual(all(bom, enc.encode("data: x\n\n")), [{ event: "message", data: "x" }]);
  assert.deepEqual(all("\uFEFFdata: x\n\n"), [{ event: "message", data: "x" }], "in a string chunk too");
});

test("cutting the bytes at every position gives the same events", () => {
  const stream = 'event: delta\r\ndata: {"text":"naïve 日本語 🙂"}\r\n\r\n: ping\n\nevent: done\ndata: {}\n\n';
  const bytes = enc.encode(stream);
  const whole = all(bytes);
  assert.equal(whole.length, 2);
  for (let i = 0; i <= bytes.length; i++) {
    assert.deepEqual(all(bytes.slice(0, i), bytes.slice(i)), whole, `cut at byte ${i}`);
  }
});

test("one byte at a time gives the same events", () => {
  const bytes = enc.encode('data: {"text":"日本語 🙂"}\n\ndata: b\n\n');
  const one = Array.from(bytes, (b) => new Uint8Array([b]));
  assert.deepEqual(all(...one), all(bytes));
});
