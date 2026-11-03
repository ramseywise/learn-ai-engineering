import { useEffect, useLayoutEffect, useReducer, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent, ReactNode } from "react";
import { ask, requestHandoff, safeHref } from "./client.ts";
import {
  citedSources,
  initialState,
  isBusy,
  reducer,
} from "./state.ts";
import type { Citation, Exchange, Finished, FailKind, UncertainReason } from "./state.ts";

const SCENARIOS = [
  "answer", "slow-start", "long", "uncertain", "no-evidence", "dangling-citation",
  "truncated", "refusal", "busy-once", "busy-always", "proxy-login-page", "server-error",
  "mid-stream-error", "dropped", "clean-eof", "stalled", "untrusted", "handoff-down",
];

const UNCERTAIN_TEXT: Record<UncertainReason, string> = {
  "weak-evidence": "Weak evidence. The search found only loosely related passages. Check the source below, or ask a person.",
  "no-evidence": "No answer found. The help centre has no passage on this. Rephrase the question, or ask a person.",
  "unsupported-citation": "Some of this has no source behind it. Treat anything marked unverified as unconfirmed, or ask a person.",
};

const ERROR_TEXT: Record<FailKind, string> = {
  busy: "The service is busy right now.",
  rejected: "This question could not be sent. Edit it and try again.",
  server: "The service hit an error while answering.",
  network: "The connection failed.",
  dropped: "The connection was lost before the answer finished.",
  stalled: "No response for a while, so this request was stopped.",
  protocol: "The service sent something other than an answer. A network sign-in page is one common cause.",
};

// Words, for people. Sent to the status region once per change of state.
function statusLine(live: Exchange): string {
  const sources = (n: number) => (n === 1 ? "1 source" : `${n} sources`);
  switch (live.status) {
    case "idle": return "";
    case "waiting": return live.slow ? "Still working. This one is taking longer than usual." : "Searching the help centre.";
    case "streaming": return "Writing an answer.";
    case "complete": return `Answer complete, ${sources(citedSources(live.text, live.citations).length)}.`;
    case "uncertain": return "Answer finished, with a warning. See the notice.";
    case "truncated": return "The answer was cut off at the length limit.";
    case "refused": return "The assistant declined this question.";
    case "stopped": return "Stopped. The partial answer is kept.";
    case "error": return "The request failed. See the notice.";
  }
}

function AnswerText({ text, citations, turnId }: { text: string; citations: Citation[]; turnId: string }) {
  // Model output is text. React escapes it, and nothing here parses Markdown,
  // so a reply cannot create an image, a script or a link by itself. The only
  // links in an answer are the [n] markers this code recognises.
  const known = new Set(citations.map((c) => c.id));
  const parts: ReactNode[] = text.split(/(\[\d+\])/).map((part, i) => {
    const m = /^\[(\d+)\]$/.exec(part);
    if (!m) return part;
    const n = Number(m[1]);
    return known.has(n) ? (
      <a key={i} href={`#source-${turnId}-${n}`} aria-label={`Source ${n}`}>{part}</a>
    ) : (
      <span key={i} className="unverified">{part} unverified</span>
    );
  });
  return <>{parts}</>;
}

function Sources({ exchange }: { exchange: Finished | Extract<Exchange, { status: "streaming" | "waiting" }> }) {
  const cited = citedSources(exchange.text, exchange.citations);
  if (cited.length === 0) return null;
  return (
    <>
      <h3>Sources</h3>
      <ol>
        {cited.map((c) => {
          const href = safeHref(c.url, location.href);
          return (
            <li key={c.id} id={`source-${exchange.id}-${c.id}`} value={c.id}>
              {href ? (
                <a href={href} target="_blank" rel="noreferrer">
                  {c.title} (opens in a new tab)
                </a>
              ) : (
                <span>{c.title} (link removed: not a web address)</span>
              )}
              <blockquote>{c.quote}</blockquote>
            </li>
          );
        })}
      </ol>
    </>
  );
}

function Turn({ exchange, streaming }: { exchange: Exclude<Exchange, { status: "idle" }>; streaming: boolean }) {
  const headingId = `q-${exchange.id}`;
  return (
    <article aria-labelledby={headingId} aria-busy={streaming}>
      <h2 id={headingId}>{exchange.question}</h2>
      <div className="answer">
        <AnswerText text={exchange.text} citations={exchange.citations} turnId={exchange.id} />
        {streaming && <span className="caret" aria-hidden="true" />}
      </div>
      {exchange.status === "uncertain" && <p className="notice">{UNCERTAIN_TEXT[exchange.reason]}</p>}
      {exchange.status === "truncated" && <p className="notice">Cut off at the length limit. This answer is incomplete.</p>}
      {exchange.status === "stopped" && <p className="notice">Stopped by you. This answer is incomplete.</p>}
      {exchange.status === "refused" && <p className="notice">This is outside what the assistant can help with. A person may be able to.</p>}
      {exchange.status === "error" && exchange.text !== "" && <p className="notice">Incomplete. This text was written before the failure.</p>}
      <Sources exchange={exchange} />
    </article>
  );
}

const newId = (() => {
  let n = 0;
  return () => `t${++n}`;
})();

function param(name: string, fallback: number): number {
  const v = Number(new URLSearchParams(location.search).get(name));
  return v > 0 ? v : fallback;
}

export function Chat() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [draft, setDraft] = useState("");
  const [scenario, setScenario] = useState("answer");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const followRef = useRef(false);
  const heightRef = useRef(0);

  const { live, handoff, history } = state;
  const busy = isBusy(live);

  function start(question: string, replace = false) {
    const id = newId();
    const controller = new AbortController();
    abortRef.current = controller;
    followRef.current = true;
    dispatch({ type: "submit", id, question, replace });
    void ask({
      id, question, scenario, dispatch,
      signal: controller.signal,
      slowMs: param("slowMs", 1000),
      stallMs: param("stallMs", 45000),
    });
  }

  function send(e?: FormEvent) {
    e?.preventDefault();
    const question = draft.trim();
    if (!question || busy) return;
    setDraft("");
    start(question);
    // Send is about to turn into Stop. If focus stayed on it, a second press
    // of Enter or Space would stop the answer the person just asked for.
    inputRef.current?.focus();
  }

  function stop() {
    abortRef.current?.abort();
    inputRef.current?.focus(); // the Stop button is about to mean Send
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) send(e);
    if (e.key === "Escape" && busy) stop();
  }

  async function handOff() {
    if (live.status === "idle" || isBusy(live)) return;
    dispatch({ type: "handoff-start" });
    try {
      const ticket = await requestHandoff({
        question: live.question,
        answer: live.text,
        citations: citedSources(live.text, live.citations),
        status: live.status,
        earlier: history.map((h) => ({ question: h.question, answer: h.text })),
        scenario,
      });
      dispatch({ type: "handoff-sent", ticket });
      inputRef.current?.focus(); // the button that had focus has just gone
    } catch {
      dispatch({ type: "handoff-failed" });
    }
  }

  // Scrolling is the external system here, so this is a real use of an Effect.
  // Follow the answer only if the reader was at the bottom before this text
  // arrived. Measuring now, rather than in a scroll listener, closes a race: the
  // scroll event fires up to a frame late, and text can land in that gap and
  // drag the reader back down. A test caught this one.
  const text = live.status === "idle" ? "" : live.text;
  useLayoutEffect(() => {
    const doc = document.documentElement;
    const wasAtBottom = heightRef.current - window.scrollY - window.innerHeight < 80;
    if (busy && (followRef.current || wasAtBottom)) bottomRef.current?.scrollIntoView({ block: "end" });
    followRef.current = false;
    heightRef.current = doc.scrollHeight;
  }, [text, busy]);

  // Unmounting must not leave a model call running. This root never unmounts,
  // so this is for reuse inside a larger app. Navigating away is a different
  // case: React runs no cleanups then, and the browser cancels the fetch itself.
  useEffect(() => () => abortRef.current?.abort(), []);

  const canRetry = live.status === "error" ? live.retryable : live.status === "stopped" || live.status === "truncated";
  const finished = live.status !== "idle" && !busy;

  return (
    <main>
      <h1>Harbour help</h1>

      <section aria-label="Conversation">
        {history.map((h) => <Turn key={h.id} exchange={h} streaming={false} />)}
        {live.status !== "idle" && (
          <Turn key={live.id} exchange={live} streaming={busy} />
        )}
      </section>

      {/* Rendered from the first paint and empty, so the region exists before it changes. */}
      <p role="status" className="status">
        {handoff.status === "sent" ? `Sent to support, reference ${handoff.ticket}.` : statusLine(live)}
      </p>

      {live.status === "error" && (
        <div role="alert" className="notice error">
          {live.kind === "server" && live.text ? "The answer failed partway through." : ERROR_TEXT[live.kind]}
          {live.retryAfterS !== undefined && ` Try again in about ${live.retryAfterS} seconds.`}
        </div>
      )}

      {handoff.status === "sent" && (
        <div className="notice">
          Sent to support, reference {handoff.ticket}. They can see your question, this answer
          and its sources, so there is no need to repeat them.
        </div>
      )}
      {handoff.status === "failed" && (
        <div role="alert" className="notice error">
          The request did not reach support. Try again, or email
          {" "}<a href="mailto:support@harbour.example">support@harbour.example</a>.
        </div>
      )}

      {finished && (
        <div className="actions">
          {canRetry && (
            <button type="button" onClick={() => { start(live.question, true); inputRef.current?.focus(); }}>
              Retry
            </button>
          )}
          <button type="button" onClick={() => { setDraft(live.question); inputRef.current?.focus(); }}>
            Edit question
          </button>
          {handoff.status !== "sent" && (
            <button type="button" disabled={handoff.status === "sending"} onClick={() => void handOff()}>
              {handoff.status === "sending" ? "Sending to support" : handoff.status === "failed" ? "Try support again" : "Ask a person"}
            </button>
          )}
        </div>
      )}

      {/* Next to the input, where people are looking. */}
      <p className="disclaimer">
        Answers come from an automated search of the help centre and can be wrong. Open the
        source before acting on one.
      </p>
      <form className="composer" onSubmit={send}>
        <label htmlFor="question">Your question</label>
        <textarea
          id="question"
          ref={inputRef}
          rows={2}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          aria-describedby="question-help"
        />
        <p id="question-help" className="disclaimer">Enter sends. Shift+Enter starts a new line. Escape stops an answer.</p>
        <label htmlFor="scenario">Mock scenario (lab only)</label>
        <select id="scenario" value={scenario} onChange={(e) => setScenario(e.target.value)}>
          {SCENARIOS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <div className="actions">
          {busy ? (
            <button type="button" onClick={stop}>Stop</button>
          ) : (
            <button type="submit">Send</button>
          )}
        </div>
      </form>
      <div ref={bottomRef} />
    </main>
  );
}
