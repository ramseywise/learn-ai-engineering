# 02 — Context Engineering

> Depth layer. Summary: [interviewing/guides/5-context-cost](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/5-context-cost/00-overview.md)
> Position in the stack: *each loop step assembles context*.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Context engineering is the discipline of composing what goes *into* the model's context window on each call: which documents to include, which memory to surface, which tool outputs to inject, how much history to keep, and how to spend the token budget across all of it. Prompt engineering ends at the instructions themselves ([01-prompt-engineering](../01-prompt-engineering/README.md)). Context engineering begins with the surrounding content those instructions act on.

Memory and tool design are **sub-components of this layer and the harness layer**, not sibling pillars.

**Inherits the weaknesses of:** prompt engineering. A well-assembled window can't compensate for poorly written instructions inside it.

### Where the boundaries are

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside the instructions |
| How you phrase the task, format requests, structure XML | Which documents, memory, tool outputs and history to inject |
| Role setting, CoT, few-shot, output format | Window composition, token budget, retrieval strategy |

Once you're deciding *what* is in the window rather than *how* to phrase what's already there, you're doing context engineering. The other edge: once assembly becomes stateful and conditional, a loop that decides *when* to retrieve, compact or spawn, you've crossed into the harness ([03-harness](../03-harness-engineering/README.md)).

### What goes in

| Type | Source | Volatility |
|---|---|---|
| Static | Role, instructions, rules | Stable across sessions |
| Dynamic | Date and time, user, environment | Per turn |
| Retrieved | Vector store, search, file reads | Per query |
| Historical | Prior states, revisions, outputs | Grows monotonically |

Historical is the only type without a natural bound, and compaction exists to bound it ([02 — context types](notes/02-context-anatomy.md#context-types-taxonomy), [05](notes/05-compression-compaction.md)).

**Security.** Context has no type system: instructions and data are the same tokens. Prompt injection is therefore a context-layer problem as much as a prompt-layer one, and every added context source is added attack surface ([11 — prompt injection](notes/11-failure-modes.md#prompt-injection)).

---

## The mental model

**Find the smallest set of high-signal tokens that maximises the likelihood of the outcome you want** (Anthropic). It's a *minimisation*: attention divides a fixed budget across n² token pairs, so every added token has a cost, and past a point returns turn negative ([01](notes/01-why-context-is-finite.md)).

Four levers respond to that constraint. Apply them in order, because cost rises left to right:

| Lever | Question | Chapters |
|---|---|---|
| **Write** | Can this live outside the window? | [06](notes/06-memory.md), [07](notes/07-structured-context.md) |
| **Select** | What comes back in, and when? | [04](notes/04-retrieval.md) |
| **Compress** | Can this be smaller? | [03](notes/03-budgeting-the-window.md), [05](notes/05-compression-compaction.md) |
| **Isolate** | Does this need a separate window? | [10](notes/10-tools-and-multi-agent.md) |

Isolate is last because it costs the most: real tokens multiply, and context is lost between agents.

---

## Rules of thumb

The rules from the topic notes on one page. Each group links to the chapter that explains it.

**Assembling the window** ([02](notes/02-context-anatomy.md), [03](notes/03-budgeting-the-window.md))
- **Stable before dynamic.** System prompt and memory summaries first, then history, retrieved content and the query, so the cache prefix holds.
- **Reserve output space first**, then give every growing component (history, tool results) a ceiling.
- Two to five **diverse, canonical examples** beat an exhaustive rule list.

**Getting content in** ([04](notes/04-retrieval.md))
- Prefer **just-in-time** retrieval through lightweight identifiers (paths, IDs, queries) over pre-loading everything.
- Decide **retrieve, cache or load it all** before building a pipeline. When you do retrieve: hybrid search plus a reranker, retrieve wide and send narrow ([pipeline mechanics](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md)).
- Wrap retrieved text in tags with source and date, and tell the model to say when the answer isn't there.

**Keeping it small** ([05](notes/05-compression-compaction.md), [06](notes/06-memory.md), [07](notes/07-structured-context.md))
- **Clear tool results first**, before any lossy summarisation.
- Keep task state in a **small, structured, overwritten block**, not in the transcript. Agents that write state down survive compaction.
- Distil episodic memory into semantic facts, and give every memory a source, a date and a scope.

**Reasoning and procedures** ([08](notes/08-cognitive-tools.md), [09](notes/09-protocols.md))
- Separate *understanding*, *solving* and *verifying* into distinct calls. End verifiers with a machine-readable verdict and bound the loop.
- Use a deterministic check (tests, a parser, a calculator) over a model verifier wherever one exists.

**Multiple agents** ([10](notes/10-tools-and-multi-agent.md))
- Try Compress before Isolate. **The orchestrator holds the plan**; sub-agents get a bounded task, minimal context and a return shape.
- Tool outputs are context. Make them concise, paginated and unambiguous.

**Shipping** ([11](notes/11-failure-modes.md), [12](notes/12-evaluating-context.md), [13](notes/13-putting-it-together.md))
- When an agent misbehaves, look in the window before the weights: rot, poisoning, distraction, clash, injection.
- Instrument each stage (exists → retrieved → survived → used). **Ablate components** to set the budget by evidence.
- Climb the maturity ladder only when the rung below fails measurably.

---

## Where to start

- **Lecture deck:** [slides/context-engineering.pptx](slides/context-engineering.pptx) — the notes as a 3-part talk (source: [slides/deck.yaml](slides/deck.yaml); rebuild with `make slides PILLAR=02-context-engineering`).
- **New to this:** read [the mental model](#the-mental-model) above, then chapters 01–06 in order, running the code snippets in each note.
- **Building an agent now:** [02](notes/02-context-anatomy.md), [05](notes/05-compression-compaction.md), [10](notes/10-tools-and-multi-agent.md), then the design order of questions in [13](notes/13-putting-it-together.md#designing-a-context-system-the-order-of-questions).
- **Debugging one:** [11 — failure modes](notes/11-failure-modes.md), then [12 — evaluating context](notes/12-evaluating-context.md).

---

## Layout

```
02-context-engineering/
├── README.md               ← you are here: summary, rules of thumb, chapter index
├── notes/                  ← the chapters (read in order), plus the 99 appendix; figures and code inline
├── slides/                 ← lecture deck built from the notes (deck.yaml → context-engineering.pptx)
├── sources/                ← PDFs of the papers the chapters cite; images/ holds every figure the notes use
└── references.md           ← papers and further reading, mapped to chapters
```

### Topic notes ([notes/](notes/))

**Foundations**
1. [Why context is finite](notes/01-why-context-is-finite.md) — attention budget, n² attention, context rot, diminishing returns.
2. [The anatomy of effective context](notes/02-context-anatomy.md) — system prompt altitude, the five layers, stable-before-dynamic ordering, the formal `C = A(…)` view, example selection, a worked deep-research example.
3. [Budgeting the window](notes/03-budgeting-the-window.md) — the window as an economy, allocation frameworks, per-component reduction, budgeting with a cache, measuring token efficiency.

**The levers**

4. [Retrieval: one lever on the window](notes/04-retrieval.md) — retrieve vs. cache vs. load it all, just-in-time retrieval, how much to retrieve, where results land and how they're framed, contextual retrieval, index-time distillation, caching, validation. Pipeline mechanics (chunking, hybrid search, PRINCE, RAG architectures) are in [genai 02 — rag.md](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md).
5. [Compression and compaction](notes/05-compression-compaction.md) — the compaction pipeline, tool-result clearing, state extraction, memory hierarchies, compression techniques, crash recovery.
6. [Memory](notes/06-memory.md) — memory types, structured note-taking, index-plus-detail, hygiene, MemOS-style lifecycle, MEM1, reconstructive memory.
7. [Structured context and schemas](notes/07-structured-context.md) — choosing a format, input/state/output schemas, knowledge graphs, schema design principles.
8. [Cognitive tools and prompt programs](notes/08-cognitive-tools.md) — the IBM cognitive-tools result, template families, the self-correction loop, prompt programs.
9. [Protocols](notes/09-protocols.md) — protocol shells, Pareto-lang, the protocol catalogue: context engineering without code.
10. [Multi-agent context and tool design](notes/10-tools-and-multi-agent.md) — sub-agent isolation, orchestrator-holds-plan, token-efficient tools, tool-integration patterns, MCP as context plumbing (who controls each primitive, transports, server design), orchestration and coordination.

**Practice**

11. [Context failure modes](notes/11-failure-modes.md) — rot, poisoning, distraction, clash, injection, and the diagnostic flow.
12. [Evaluating context](notes/12-evaluating-context.md) — the failure chain, metrics per lever, long-context sweeps, ablation, building the eval set.
13. [Putting it together](notes/13-putting-it-together.md) — the maturity ladder (atoms → cognitive systems), recurring patterns, four reference architectures, a capstone exercise.

**Appendix:** [99 — the speculative field track](notes/99-speculative-field-track.md) — neural fields, attractors, resonance, quantum semantics and the mental models, with what's grounded and what isn't (`confidence: low`).

### Code in the notes

The upstream course's Python labs and the DAIR caching notebook are folded into the notes as short snippets, each credited where it appears:

| Code | Now in |
|---|---|
| Layer-by-layer token cost (`02_expand_context.py`), drop-oldest history fit (upstream `control_loop.py`) | [03 — measuring token efficiency](notes/03-budgeting-the-window.md#measuring-token-efficiency), [history](notes/03-budgeting-the-window.md#history) |
| Contextual-retrieval prefix, explicit caching (`gemini-context-caching.ipynb`, ported to `google-genai`) | [04 — contextual retrieval](notes/04-retrieval.md#contextual-retrieval), [caching](notes/04-retrieval.md#caching) |
| Overlap chunker and hybrid fusion (`04_rag_recipes.py`), retrieved few-shot (`pe-rag.ipynb`) | [genai rag.md — chunking](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#chunking), [hybrid retrieval](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#hybrid-retrieval), [Text-to-SQL](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#text-to-sql-is-a-retrieval-strategy) |
| Memoria-style memory wrapper and decay weighting | [06 — production memory designs](notes/06-memory.md#production-memory-designs) |
| Minimal context YAML (`minimal_context.yaml`), schema-in-prompt, validate and retry (`06_schema_design.py`) | [07 — input schemas](notes/07-structured-context.md#1-input-schemas--how-a-task-is-presented), [output schemas](notes/07-structured-context.md#3-output-schemas--what-comes-back) |
| External validator loop (`03_control_loops.py`), operations-as-data program (`05_prompt_programs.py`), self-graded stop caution (`07_recursive_patterns.py`) | [08 — self-correction loop](notes/08-cognitive-tools.md#the-self-correction-loop), [prompt programs](notes/08-cognitive-tools.md#prompt-programs) |

### Worked examples elsewhere

BM25 from scratch and retrieved few-shot (`pe-rag`) are worked examples in [genai rag.md](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#bm25-from-scratch), next to the pipeline material they exercise.

### Related
- [genai 02 — RAG & retrieval](../../generative-ai/02-rag-retrieval/README.md) — the retrieval pipeline in depth, conversational RAG, and the BM25 worked example.
- [03-harness — progressive disclosure: skills](../03-harness-engineering/notes/03-tool-design.md#progressive-disclosure-skills) — skills as a harness primitive; relies on the progressive disclosure covered in [04](notes/04-retrieval.md).

### Interviewing guide
- [5-context-cost](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/5-context-cost/00-overview.md) — compressed summary for interview prep.

### Course code
- [LLMs-as-Operating-Systems--Agent-Memory-main](../../generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system.md) — memory as an OS primitive.
- [Long-Term-Agentic-Memory-With-LangGraph-main](../../generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph.md) — long-term memory patterns.

### Next layer
→ [03-harness-engineering/](../03-harness-engineering/README.md) — the harness wraps the loops that assemble context.

---

## References

Papers with local PDFs, mapped to chapters: [references.md](references.md). PDFs: [sources/](sources/). **★** marks the ones to read first.

### Origin readings
Where the term "context engineering" came from (mid-2025), and the essays that shaped it:
- ★ Anthropic, [*Effective context engineering for AI agents*](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): the backbone of chapters 01, 02, 04–06 and 10
- Karpathy, [the "context engineering" post](https://x.com/karpathy/status/1937902205765607626): "the delicate art and science of filling the context window"
- LangChain, [*The rise of context engineering*](https://blog.langchain.com/the-rise-of-context-engineering/)
- ★ Lance Martin, [*Context engineering for agents*](https://rlancemartin.github.io/2025/06/23/context_engineering/), the source of the Write → Select → Compress → Isolate levers
- Phil Schmid, [*The new skill in AI is not prompting, it's context engineering*](https://www.philschmid.de/context-engineering)
- Walden Yan (Cognition), [*Don't build multi-agents*](https://cognition.ai/blog/dont-build-multi-agents): share full context, not messages
- HumanLayer, [*12-factor agents*](https://github.com/humanlayer/12-factor-agents): "own your context window"
- DAIR, [*Context Engineering Guide*](https://www.promptingguide.ai/guides/context-engineering-guide), the source of the worked example in [02](notes/02-context-anatomy.md#worked-example-tuning-a-deep-research-agent)
- Drew Breunig, [*How contexts fail and how to fix them*](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html): the failure taxonomy in [11](notes/11-failure-modes.md)

### Course material
- davidkimai, [*Context Engineering*](https://github.com/davidkimai/Context-Engineering) (snapshot 2026-08-14): the upstream course, synthesized into chapters 03, 07–09, 12, 13 and 99. The raw files were deleted; see [references.md](references.md#about-the-upstream-course).

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-context.md`
Conventions for what goes in the context window, in what order, and what gets evicted first — and how a long-running agent stays under the window limit without losing decisions.

Key topics for this pillar:
- Four-lever model: Write → Select → Compress → Isolate (apply in order; isolate is highest cost)
- Content priority ordering: stable content (system prompt, memory summaries) before ephemeral content (history, tool results, scratch reasoning)
- Compaction strategy: trigger points (80% limit, phase boundaries, before subagent spawn), what to compact, what must survive
- Prompt versioning: prompts as versioned artifacts with `PROMPT_VERSION` identifiers; version bumps invalidate eval baselines
- Progressive disclosure: loading task-specific instruction blocks only when active; the `skills/` directory as a practice of this pattern
- Subagent context isolation: what the subagent receives vs. what it does not; orchestrator-holds-plan as the settled default
