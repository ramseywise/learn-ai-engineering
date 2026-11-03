// The whole chat as a pure function: (state, action) -> state. No React, no
// network, no clock, so every transition is testable without a browser.

export type Citation = { id: number; title: string; url: string; quote: string };
export type Evidence = "strong" | "weak" | "none";
export type Stop = "end" | "length" | "refusal";
export type FailKind = "busy" | "rejected" | "server" | "network" | "dropped" | "stalled" | "protocol";
export type UncertainReason = "weak-evidence" | "no-evidence" | "unsupported-citation";

type Body = { id: string; question: string; text: string; citations: Citation[] };

export type Exchange =
  | { status: "idle" }
  | ({ status: "waiting"; slow: boolean } & Body)
  | ({ status: "streaming" } & Body)
  | ({ status: "complete" } & Body)
  | ({ status: "uncertain"; reason: UncertainReason } & Body)
  | ({ status: "truncated" } & Body)
  | ({ status: "refused" } & Body)
  | ({ status: "stopped" } & Body)
  | ({ status: "error"; kind: FailKind; retryable: boolean; retryAfterS?: number } & Body);

export type Finished = Exclude<Exchange, { status: "idle" | "waiting" | "streaming" }>;

export type Handoff =
  | { status: "none" }
  | { status: "sending" }
  | { status: "sent"; ticket: string }
  | { status: "failed" };

export type State = { history: Finished[]; live: Exchange; handoff: Handoff };

export type Action =
  | { type: "submit"; id: string; question: string; replace?: boolean }
  | { type: "slow"; id: string }
  | { type: "delta"; id: string; text: string }
  | { type: "citation"; id: string; citation: Citation }
  | { type: "done"; id: string; stop: Stop; evidence: Evidence }
  | { type: "stopped"; id: string }
  | { type: "fail"; id: string; kind: FailKind; retryable: boolean; retryAfterS?: number }
  | { type: "handoff-start" }
  | { type: "handoff-sent"; ticket: string }
  | { type: "handoff-failed" };

export const initialState: State = {
  history: [],
  live: { status: "idle" },
  handoff: { status: "none" },
};

type InFlight = Extract<Exchange, { status: "waiting" | "streaming" }>;

export function isBusy(live: Exchange): live is InFlight {
  return live.status === "waiting" || live.status === "streaming";
}

export function markers(text: string): number[] {
  return [...text.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1]));
}

// A marker with no source behind it. The model wrote "[3]" and retrieval
// returned no third passage. Derived from text and citations, so never stored.
export function danglingMarkers(text: string, citations: Citation[]): number[] {
  const known = new Set(citations.map((c) => c.id));
  return [...new Set(markers(text))].filter((n) => !known.has(n));
}

// Retrieved is not the same as used. List only sources the answer refers to.
export function citedSources(text: string, citations: Citation[]): Citation[] {
  const used = new Set(markers(text));
  return citations.filter((c) => used.has(c.id));
}

function finish(body: Body, stop: Stop, evidence: Evidence): Finished {
  if (stop === "refusal") return { status: "refused", ...body };
  if (stop === "length") return { status: "truncated", ...body };
  if (evidence === "none") return { status: "uncertain", reason: "no-evidence", ...body };
  if (evidence === "weak") return { status: "uncertain", reason: "weak-evidence", ...body };
  const unsupported =
    danglingMarkers(body.text, body.citations).length > 0 || markers(body.text).length === 0;
  if (unsupported) return { status: "uncertain", reason: "unsupported-citation", ...body };
  return { status: "complete", ...body };
}

function bodyOf(e: Exclude<Exchange, { status: "idle" }>): Body {
  return { id: e.id, question: e.question, text: e.text, citations: e.citations };
}

export function reducer(state: State, action: Action): State {
  const live = state.live;

  if (action.type === "submit") {
    if (isBusy(live)) return state; // one request at a time
    const keep = live.status !== "idle" && !action.replace;
    return {
      history: keep ? [...state.history, live as Finished] : state.history,
      live: {
        status: "waiting",
        slow: false,
        id: action.id,
        question: action.question,
        text: "",
        citations: [],
      },
      handoff: { status: "none" },
    };
  }

  if (action.type === "handoff-start") {
    if (live.status === "idle" || isBusy(live)) return state;
    return { ...state, handoff: { status: "sending" } };
  }
  if (action.type === "handoff-sent") {
    if (state.handoff.status !== "sending") return state;
    return { ...state, handoff: { status: "sent", ticket: action.ticket } };
  }
  if (action.type === "handoff-failed") {
    if (state.handoff.status !== "sending") return state;
    return { ...state, handoff: { status: "failed" } };
  }

  // Everything below belongs to one request. A late event from an abandoned
  // request carries the old id and must not write into the current answer.
  if (!isBusy(live) || live.id !== action.id) return state;
  const body = bodyOf(live);

  switch (action.type) {
    case "slow":
      return live.status === "waiting" ? { ...state, live: { ...live, slow: true } } : state;
    case "delta":
      return { ...state, live: { status: "streaming", ...body, text: body.text + action.text } };
    case "citation": {
      if (body.citations.some((c) => c.id === action.citation.id)) return state;
      const next = { ...body, citations: [...body.citations, action.citation] };
      return { ...state, live: { ...live, ...next } };
    }
    case "done":
      return { ...state, live: finish(body, action.stop, action.evidence) };
    case "stopped":
      return { ...state, live: { status: "stopped", ...body } };
    case "fail": {
      const failed: Exchange = {
        status: "error",
        ...body, // the partial text stays; the user may have read it
        kind: action.kind,
        retryable: action.retryable,
      };
      if (action.retryAfterS !== undefined) failed.retryAfterS = action.retryAfterS;
      return { ...state, live: failed };
    }
  }
}
