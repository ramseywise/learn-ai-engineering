// Turns one HTTP response into reducer actions. Uses fetch rather than
// EventSource because EventSource can only issue a GET with no body.

import { SseParser } from "./sse.ts";
import type { Action, Citation, Evidence, FailKind, Stop } from "./state.ts";

export type AskOptions = {
  id: string;
  question: string;
  scenario: string;
  signal: AbortSignal;
  dispatch: (action: Action) => void;
  url?: string;
  slowMs?: number; // no first token by now: say so
  stallMs?: number; // no bytes at all for this long: give up. Keep it well above the server's keep-alive interval.
};

function classify(status: number): { kind: FailKind; retryable: boolean } {
  if (status === 429 || status === 503 || status === 529) return { kind: "busy", retryable: true };
  if (status >= 500) return { kind: "server", retryable: true };
  return { kind: "rejected", retryable: false };
}

export async function ask(o: AskOptions): Promise<void> {
  const { id, dispatch } = o;
  const slowMs = o.slowMs ?? 1000;
  const stallMs = o.stallMs ?? 45000;

  // Two reasons to abort: the Stop button, and the stall watchdog below.
  const inner = new AbortController();
  let stalled = false;
  const onOuterAbort = () => inner.abort();
  o.signal.addEventListener("abort", onOuterAbort);

  let watchdog: ReturnType<typeof setTimeout> | undefined;
  const feedWatchdog = () => {
    clearTimeout(watchdog);
    watchdog = setTimeout(() => {
      stalled = true;
      inner.abort();
    }, stallMs);
  };
  const slowTimer = setTimeout(() => dispatch({ type: "slow", id }), slowMs);

  const fail = (kind: FailKind, retryable: boolean, retryAfterS?: number) => {
    const action: Action = { type: "fail", id, kind, retryable };
    if (retryAfterS !== undefined) action.retryAfterS = retryAfterS;
    dispatch(action);
  };

  let responded = false; // fetch rejecting before any response is a different failure from a dropped stream
  try {
    feedWatchdog();
    const res = await fetch(o.url ?? "/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json", accept: "text/event-stream" },
      body: JSON.stringify({ question: o.question, scenario: o.scenario }),
      signal: inner.signal,
    });
    responded = true;
    if (!res.ok) {
      const { kind, retryable } = classify(res.status);
      const after = Number(res.headers.get("retry-after"));
      fail(kind, retryable, after > 0 ? after : undefined);
      return;
    }
    // A proxy's login page can arrive as a 200. It is still not an answer.
    if (!(res.headers.get("content-type") ?? "").startsWith("text/event-stream") || !res.body) {
      fail("protocol", true);
      return;
    }

    const parser = new SseParser();
    const reader = res.body.getReader();
    let finished = false;

    const handle = (name: string, data: string): void => {
      switch (name) {
        case "delta":
          clearTimeout(slowTimer);
          dispatch({ type: "delta", id, text: (JSON.parse(data) as { text: string }).text });
          break;
        case "citation":
          dispatch({ type: "citation", id, citation: JSON.parse(data) as Citation });
          break;
        case "done": {
          const d = JSON.parse(data) as { stop: Stop; evidence: Evidence };
          dispatch({ type: "done", id, stop: d.stop, evidence: d.evidence });
          finished = true;
          break;
        }
        case "error":
          // HTTP already said 200. This is the only channel left for failure.
          fail("server", (JSON.parse(data) as { retryable?: boolean }).retryable ?? true);
          finished = true;
          break;
        default:
          break; // ping and anything newer than this client: ignore
      }
    };

    while (!finished) {
      const { done, value } = await reader.read();
      feedWatchdog(); // any byte, including a keep-alive comment, proves life
      const events = done ? parser.end() : parser.push(value);
      for (const e of events) handle(e.event, e.data);
      if (done) break;
    }
    if (finished) await reader.cancel().catch(() => {});
    else fail("dropped", true); // clean EOF with no terminal event is a failure
  } catch (err) {
    if (stalled) fail("stalled", true);
    else if (o.signal.aborted) dispatch({ type: "stopped", id });
    else if (err instanceof SyntaxError) fail("protocol", true);
    else fail(responded ? "dropped" : "network", true);
  } finally {
    clearTimeout(slowTimer);
    clearTimeout(watchdog);
    o.signal.removeEventListener("abort", onOuterAbort);
  }
}

export type HandoffPayload = {
  question: string;
  answer: string;
  citations: Citation[];
  status: string;
  earlier: { question: string; answer: string }[];
  scenario: string;
};

export async function requestHandoff(p: HandoffPayload, url = "/api/handoff"): Promise<string> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(p),
  });
  if (!res.ok) throw new Error(`handoff returned ${res.status}`);
  return ((await res.json()) as { ticket: string }).ticket;
}

// Only http and https may become links. Everything else, javascript: above
// all, stays as visible text. Relative URLs resolve against the page.
export function safeHref(url: string, base: string): string | undefined {
  try {
    const u = new URL(url, base);
    return u.protocol === "http:" || u.protocol === "https:" ? u.href : undefined;
  } catch {
    return undefined;
  }
}
