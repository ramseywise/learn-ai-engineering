// A support-triage graph. Every LangGraph primitive the pillar teaches appears once:
// reducers, conditional routing, a cycle, Send fan-out, a checkpointer, interrupt and resume.
import { readFileSync } from "node:fs";
import { Annotation, END, Send, START, StateGraph, interrupt, type BaseCheckpointSaver } from "@langchain/langgraph";
import type { Complete } from "./model.ts";

interface Doc { id: string; source: string; text: string; keywords: string[] }
const KB: Doc[] = JSON.parse(readFileSync(new URL("../langgraph-graph/kb.json", import.meta.url), "utf8"));
const SOURCES = ["docs", "tickets"];
const MAX_DRAFTS = 2;

const add = <T>(a: T[], b: T[]) => a.concat(b);
export const State = Annotation.Root({
  ticket: Annotation<string>,
  label: Annotation<string>,
  reply: Annotation<string>,
  drafts: Annotation<number>,
  approved: Annotation<boolean>,
  status: Annotation<string>,
  // A reducer says how parallel writes merge. Without one, two searches writing the same key
  // in one step is an error. Concatenating means both results survive.
  evidence: Annotation<Doc[]>({ reducer: add, default: () => [] }),
  trail: Annotation<string[]>({ reducer: add, default: () => [] }),
  tokens: Annotation<number>({ reducer: (a, b) => a + b, default: () => 0 }),
});
type S = typeof State.State;

export function buildGraph(complete: Complete, checkpointer: BaseCheckpointSaver, outbox: string[]) {
  const afterCheck = (s: S) => {
    // Deterministic: the draft must cite evidence that was actually retrieved.
    const cited = [...s.reply.matchAll(/\[([\w-]+)\]/g)].map((m) => m[1]);
    if (s.evidence.some((d) => cited.includes(d.id))) return s.label === "billing" ? "approve" : "send";
    return s.drafts < MAX_DRAFTS ? "draft" : "escalate";
  };
  return new StateGraph(State)
    .addNode("classify", async (s: S) => {
      const res = await complete({
        system: "CLASSIFY the ticket. Reply with exactly one word: billing, bug or how_to.",
        prompt: `<ticket>\n${s.ticket}\n</ticket>`,
        maxTokens: 2000,
      });
      return { label: res.text.trim(), trail: ["classify"], tokens: res.inputTokens + res.outputTokens };
    })
    .addNode("search", (s: { ticket: string; source: string }) => {
      const t = s.ticket.toLowerCase();
      return {
        evidence: KB.filter((d) => d.source === s.source && d.keywords.some((k) => t.includes(k))),
        trail: [`search:${s.source}`],
      };
    })
    .addNode("gather", () => ({ trail: ["gather"] })) // the join: runs once, after every search has finished
    .addNode("draft", async (s: S) => {
      const docs = [...s.evidence]
        .sort((a, b) => (a.id < b.id ? -1 : 1))
        .map((d) => `[${d.id}] ${d.text}`)
        .join("\n");
      const retry = s.drafts ? "\n\nYour last draft cited nothing. Cite a document id in square brackets." : "";
      const res = await complete({
        system: "DRAFT a one-sentence reply from the documents only.",
        prompt: `<ticket>\n${s.ticket}\n</ticket>\n\n<documents>\n${docs}\n</documents>${retry}`,
        maxTokens: 2000,
      });
      return { reply: res.text.trim(), drafts: (s.drafts ?? 0) + 1, trail: ["draft"], tokens: res.inputTokens + res.outputTokens };
    })
    .addNode("check", () => ({ trail: ["check"] }))
    .addNode("approve", (s: S) => {
      // On resume the node re-runs from its first line, and `interrupt` returns the resume value
      // this time. So put no side effect above this call: it would run twice.
      // The decision is a string on purpose: LangGraph.js treats a falsy resume value as no input
      // at all, so `new Command({ resume: false })` throws EmptyInputError.
      const decision = interrupt({ ticket: s.ticket, draft: s.reply });
      return { approved: decision === "approve", trail: ["approve"] };
    })
    .addNode("send", (s: S) => {
      outbox.push(s.reply);
      return { status: "sent", trail: ["send"] };
    })
    .addNode("escalate", () => ({ status: "escalated", trail: ["escalate"] }))
    .addEdge(START, "classify")
    // Send starts one parallel `search` per source, each with its own input.
    .addConditionalEdges("classify", (s: S) => SOURCES.map((source) => new Send("search", { ticket: s.ticket, source })), ["search"])
    .addEdge("search", "gather")
    .addConditionalEdges("gather", (s: S) => (s.evidence.length ? "draft" : "escalate"), ["draft", "escalate"])
    .addEdge("draft", "check")
    .addConditionalEdges("check", afterCheck, ["approve", "send", "draft", "escalate"])
    .addConditionalEdges("approve", (s: S) => (s.approved ? "send" : "escalate"), ["send", "escalate"])
    .addEdge("send", END)
    .addEdge("escalate", END)
    .compile({ checkpointer });
}
