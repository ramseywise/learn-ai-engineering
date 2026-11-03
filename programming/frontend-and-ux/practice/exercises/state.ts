// Exercise 2. Write the reducer. The types are given: they are the design.
// Run: TARGET=exercises node --test tests/state.test.ts

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

export function isBusy(live: Exchange): live is Extract<Exchange, { status: "waiting" | "streaming" }> {
  return live.status === "waiting" || live.status === "streaming";
}

export function markers(_text: string): number[] {
  throw new Error("TODO: exercise 2");
}

export function danglingMarkers(_text: string, _citations: Citation[]): number[] {
  throw new Error("TODO: exercise 2");
}

export function citedSources(_text: string, _citations: Citation[]): Citation[] {
  throw new Error("TODO: exercise 2");
}

export function reducer(_state: State, _action: Action): State {
  throw new Error("TODO: exercise 2");
}
