// Exercise 1. Implement the event-stream parser from the HTML Living Standard,
// section 9.2.6. Run: TARGET=exercises node --test tests/sse.test.ts
// Keep this interface. A chunk can end anywhere, even inside a character.
// Leave `id` out of an event until one has been seen: the tests compare with
// deepEqual, which treats `id: undefined` as different from no `id` at all.

export type SseEvent = { event: string; data: string; id?: string };

export class SseParser {
  push(_chunk: Uint8Array | string): SseEvent[] {
    throw new Error("TODO: exercise 1");
  }

  end(): SseEvent[] {
    throw new Error("TODO: exercise 1");
  }
}
