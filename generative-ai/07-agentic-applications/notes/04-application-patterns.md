---
origin: book-condensed
sources:
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 11"
  - "Denis Rothman, Context Engineering for Multi-Agent Systems (Packt, 2025), ch. 9"
  - https://arxiv.org/abs/2502.16810
  - https://arxiv.org/abs/2503.16527
confidence: medium
cleaned: 2026-10-31
---
# 4 — Application Patterns: Where the Agent Meets the User

> Notes 01–03 are about what the agent does. This note is about where it sits in someone's work: beside it (chatbot), inside it (collaborative editing) or behind it (ambient), and what each position forces you to build. It ends with a worked example of one engine reused across domains.

---

## The interface problem

Productivity software is a **palette** of tools and primitives plus a **canvas** where the user arranges them. That design assumes the software's capabilities are known in advance, because an engineer coded every tool. An LLM-heavy application breaks the assumption. It is also forgiving of input that's "slightly off" and liable to produce output that's slightly off, which no earlier UI conventions were built for (*Learning LangChain*, ch. 11).

Oshin and Campos ask what an LLM-native word processor would look like, and give three answers that apply to most LLM applications. They differ mainly in **concurrency**: who is working when.

| Pattern | Who works when | Example | Hardest part |
|---|---|---|---|
| **Interactive chatbot** | Turn-taking: the user asks, the agent answers | Copilot Chat in a VS Code sidebar | Giving it safe write access to the canvas |
| **Collaborative editing** | Both at once, on the same artifact | An always-on completion copilot; an async "drafter" sent off to research a section | Merging the agent's edits with the user's |
| **Ambient** | The agent works in the background while the user does something else | Price alerts, saved-search alerts, infrastructure anomaly alerts, with LLM judgement replacing hand-written rules | Defining "interesting" so alerts are useful without endless rule-writing |

The patterns go from easiest to add to an existing app to hardest. The same ordering appears as autonomy rungs in [04-loop note 07](../../../ai-engineering/04-loop-engineering/notes/07-autonomy-ladder.md): turn-based, then goal-based, then triggered by a clock or event.

---

## Interactive chatbot

The minimum is a chat model plus conversation history, so the bot can "get past hello". Beyond that (*Learning LangChain*, ch. 11):

- **Streaming output**, token by token or by sentence, to hide model latency.
- **Tools that reach the canvas**, such as "get selected text" and "insert text at end of doc". This is the step from a sidekick that talks about your work to one that changes it.
- **Human-in-the-loop** as soon as any tool can modify the canvas. The user confirms or edits before the insert lands. In LangGraph that's an `interrupt` before the write node ([graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#human-in-the-loop-with-interrupt)).

The authors add a prediction worth keeping in mind: streaming chat may end up as the command line of the LLM era. It would stay the most direct way to drive the model and become a niche interface, while most users meet LLMs embedded in other UIs.

---

## Collaborative editing

Software collaboration comes in three levels, and an LLM agent can join any of them as one more "user":

| Level | How editors coordinate | Example |
|---|---|---|
| **Save and send** | One editor at a time, passing the file along | Emailing a Word document |
| **Version control** | Editors work in parallel, unaware of each other, and merge afterwards (merge strategies plus conflict resolution) | Git |
| **Real-time** | Editors work on the same document at once and see each other's changes | Google Docs |

Treating the agent as a full collaborator means building six things (*Learning LangChain*, ch. 11):

| Need | Why | Where it's covered |
|---|---|---|
| **Shared state** | The agent must parse the document and emit edits in the same format the human editor uses | [graph note 03](../../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md) |
| **Task manager** | A useful edit is multi-step, slow, and can fail halfway, so it needs queueing, error recovery and control over running jobs | [graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#checkpointers) |
| **Merging forks** | The user keeps editing after tasking the agent, so its output must merge with their work, by hand (Git-style) or automatically with CRDT or operational transformation (OT) | — |
| **Concurrency** | Interrupt, cancel, reroute ("do this instead") and queue ("do this as well") | [harness note 07](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md#asynchronous-agents-events-and-safe-points) |
| **Undo/redo** | Users change their minds, and the agent has to follow them back to an earlier state | Checkpoint history, i.e. time travel ([graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#time-travel)) |
| **Intermediate output** | Small, piecemeal edits merge far more easily than one large diff at the end | Streaming node updates |

The book stops at the list. Two consequences are worth stating:

- **Merging is where the levels differ.** At version-control level, the agent works on a branch and the user reviews a diff. That is what coding agents do with worktrees and pull requests. At real-time level, the agent's edits have to go through the same CRDT/OT layer as human keystrokes, or they will clobber the user's text. Pick the level before building the agent. It decides the state format.
- **The agent should edit, not overwrite.** Whole-document rewrites can't be merged. Have the agent emit targeted operations (insert at, replace range, comment on) against an anchor that survives concurrent edits.

---

## Ambient agents

The obstacle to ambient software has always been defining "interesting" ahead of time in a way that is both **useful** (it fires when you'd want it to) and **practical** (nobody has to write hundreds of rules). LLM judgement can make the definition broader and replace most of the setup. Building it takes five things (*Learning LangChain*, ch. 11):

- **Triggers.** A push or poll source of new information. That source is the reason to build an ambient agent at all.
- **Long-term memory.** You can't tell that something is new or interesting without a record of what came before ([context note 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md)).
- **Reflection.** After each interesting event, the agent updates its memory and possibly its own rules for what counts as interesting next time.
- **Summarised output.** A background agent produces far more than anyone wants to read. Surface only what's new or noteworthy.
- **Task manager.** Continuous work needs queued runs and error recovery, the same requirement as collaborative editing.

Reflection is the risky one. An agent that rewrites its own idea of "interesting" from its own outcomes drifts, and the user never sees the alerts it stopped sending. Log every rule change, and keep a fixed set of events the agent must always surface, which reflection is not allowed to edit. That set is an anchor in the sense of [graph note 07](../../../ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale.md#anchors).

The book closes with: "There's no shortcut here. You really do need to build something (s)crappy, speak to users, and rinse and repeat."

---

## Worked example: one engine, a new domain

Rothman's *Context Engineering for Multi-Agent Systems* (ch. 9) re-tasks the Context Engine built in earlier chapters, from legal research to marketing. The engine is a Planner, an Executor, and Librarian, Researcher, Summarizer and Writer agents, with moderation on both ends. Its internals are in [harness note 07](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md#a-plan-execute-engine-end-to-end) and its moderation in [harness note 04](../../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md#moderation-around-the-whole-engine).

![Context Engine end to end: raw documents are chunked, tagged and embedded into a Pinecone knowledge base; a user goal passes a pre-flight moderation check, the Planner/Executor runs Researcher, sanitize and Writer agents against the knowledge base, and the output passes a post-flight moderation check before delivery](../sources/images/context-engineering-multi-agent-systems-fig9-1.png)
*Image Source: Denis Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), Fig. 9.1*

**The claim: change the knowledge, not the code.** Moving to marketing took three steps:

1. Copy the ingestion notebook and point it at a new folder.
2. Write seven source documents: a brand style guide, a product spec sheet, a competitor press release, a social-media brief, SEO keywords, customer-interview notes and an email-nurture outline.
3. Give the engine new goals through the same generic "Control Deck" templates.

`engine.py` doesn't change. If an agent registry with good capability descriptions and a domain-agnostic ingestion pipeline is already in place, a new domain costs a new corpus and new goals. It doesn't need new agents.

The four runs:

| Goal | Plan the engine chose | Result |
|---|---|---|
| Summarise the QuantumDrive (safeguard check) | Researcher → Librarian → Writer | Cited summary; pre- and post-flight moderation both `flagged: False` |
| Summarise the competitor's messaging | Librarian → Researcher → Summarizer → Writer | Cited summary in **69.63 s** |
| Spec sheet → marketing description | Researcher → Summarizer → Librarian → Writer | Structured copy with inline citations to the spec sheet |
| Persuasive pitch for the brand guide | Librarian → Researcher → Writer | A full pitch with "ROI levers", objections and an implementation plan |

### What to take from it

- **Latency pushes the UX toward ambient.** Seventy seconds is too slow for a chat turn. Rothman's answer is batching many goals, which turns the engine into a background job that delivers a set of assets. That is the ambient pattern above. Design the interface for the latency you have.
- **The domain lives in the corpus, so curating the corpus is the job.** Rothman's conclusion is that the practitioner's work becomes choosing domains, curating knowledge bases and turning business goals into precise engine goals. It is the same argument as [context engineering](../../../ai-engineering/02-context-engineering/README.md), applied to a product.

### Where the chapter overclaims

- **The persuasive pitch is a grounding failure, not a success.** The brand guide holds only rules (use active voice, avoid hedging), with nothing on business value. The Researcher pulled in the SEO and email documents, and the Writer produced claims such as "stronger engagement and conversion" and "faster onboarding" that no source states. Rothman calls this the chapter's most important result, because the engine "synthesized" instead of reporting that the information was missing. But the guide the engine retrieved forbids "specific, quantitative promises that cannot be universally guaranteed", and an ROI pitch made of inferred benefits is close to exactly that. A pipeline that cites sources for its facts but not for its inferences gives the reader no way to tell the two apart. When a goal asks for something the corpus doesn't contain, the output should say so, and any inferred claims should be labelled separately from cited ones ([06-eval note 07](../../../ai-engineering/06-eval/notes/07-evaluating-rag-and-grounding.md#faithfulness-claim-by-claim)).
- **One run per use case.** Each result is a single sampled output, and the chapter itself notes that LLM responses vary from run to run. "Our high-fidelity RAG is working perfectly" means it worked once.
- **The text and the questions disagree.** The end-of-chapter questions ask about a "brand voice enforcement use case" with a `BrandChecker` agent and an email-nurture use case. Neither appears in the chapter. The summary also mentions "intelligent failure", but every run shown succeeds.

The chapter cites two papers, not yet read for this course: Wu et al., *Grounded Persuasive Language Generation for Automated Marketing* ([arXiv:2502.16810](https://arxiv.org/abs/2502.16810)), and, as further reading, Li et al., *LLM Generated Persona is a Promise with a Catch* ([arXiv:2503.16527](https://arxiv.org/abs/2503.16527)). The second title is relevant to the interview → persona task the chapter's corpus is set up for.

---

## Choosing a pattern

| If… | Build |
|---|---|
| The user is already in an app and needs help on demand | A chatbot with read tools; add write tools behind confirmation |
| The output is an artifact the user keeps editing | Collaborative editing; choose the merge level first |
| The work is slow (tens of seconds or more) and nobody is waiting on it | Ambient or batch, delivered as a summary |
| You can't say ahead of time what should trigger the agent | Ambient with reflection, plus anchors reflection can't edit |
| A second domain needs the same capability | Reuse the engine; write a new corpus and new goals, not new agents |

---

→ Back to [01 — Internet search agent](01-internet-search-agent.md), or on to the engineering layer in [ai-engineering](../../../ai-engineering/README.md).
