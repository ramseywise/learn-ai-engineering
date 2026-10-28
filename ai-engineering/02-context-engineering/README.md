# 02 — Context Engineering

> Depth layer. Summary: [interviewing/guides/5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
> Position in the stack: *each loop step assembles context*.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Context engineering is the discipline of composing what goes *into* the model's context window on each call: which documents to include, which memory to surface, which tool outputs to inject, how much history to keep, and how to spend the token budget across all of it. Prompt engineering ends at the instructions themselves ([01-prompt-engineering](../01-prompt-engineering/README.md)). Context engineering begins with the surrounding content those instructions act on.

Memory and tool design are **sub-components of this layer and the harness layer**, not sibling pillars.

**Inherits the weaknesses of:** prompt engineering. A well-assembled window can't compensate for poorly written instructions inside it.

Overview note: [context-engineering.md](context-engineering.md), covering the thesis, the four levers, the prompt ↔ context boundary and context types.

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

---

## Rules of thumb

The rules from the topic notes on one page. Each group links to the chapter that explains it.

**Assembling the window** ([02](notes/02-context-anatomy.md), [03](notes/03-budgeting-the-window.md))
- **Stable before dynamic.** System prompt and memory summaries first, then history, retrieved content and the query, so the cache prefix holds.
- **Reserve output space first**, then give every growing component (history, tool results) a ceiling.
- Two to five **diverse, canonical examples** beat an exhaustive rule list.

**Getting content in** ([04](notes/04-retrieval.md))
- Prefer **just-in-time** retrieval through lightweight identifiers (paths, IDs, queries) over pre-loading everything.
- Use **hybrid search plus a reranker** as the default. Retrieve small chunks and return their parent section.
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

- **New to this:** read [context-engineering.md](context-engineering.md), then chapters 01–06 in order, running the matching [notebooks](#notebooks).
- **Building an agent now:** [02](notes/02-context-anatomy.md), [05](notes/05-compression-compaction.md), [10](notes/10-tools-and-multi-agent.md), then the design order of questions in [13](notes/13-putting-it-together.md#designing-a-context-system-the-order-of-questions).
- **Debugging one:** [11 — failure modes](notes/11-failure-modes.md), then [12 — evaluating context](notes/12-evaluating-context.md).

---

## Layout

```
02-context-engineering/
├── README.md               ← you are here: summary, rules of thumb, chapter index
├── context-engineering.md  ← pillar overview
├── notes/                  ← the chapters (read in order), plus the 99 appendix
├── notebooks/              ← runnable Python labs
├── practice/               ← offline labs adapted from AI Agents in Depth
├── templates/              ← copyable schemas, prompt programs and prompt templates
├── sources/                ← PDFs of the papers the chapters cite
└── references.md           ← papers and further reading, mapped to chapters
```

### Topic notes ([notes/](notes/))

**Foundations**
1. [Why context is finite](notes/01-why-context-is-finite.md) — attention budget, n² attention, context rot, diminishing returns.
2. [The anatomy of effective context](notes/02-context-anatomy.md) — system prompt altitude, the five layers, stable-before-dynamic ordering, the formal `C = A(…)` view, example selection, a worked deep-research example.
3. [Budgeting the window](notes/03-budgeting-the-window.md) — the window as an economy, allocation frameworks, per-component reduction, budgeting with a cache, measuring token efficiency.

**The levers**

4. [Retrieval strategies](notes/04-retrieval.md) — pre-computed vs. just-in-time, the pre-retrieval pipeline, RAG architectures (modular, agentic, graph), chunking, hybrid search, framing retrieved content.
5. [Compression and compaction](notes/05-compression-compaction.md) — the compaction pipeline, tool-result clearing, state extraction, memory hierarchies, compression techniques, crash recovery.
6. [Memory](notes/06-memory.md) — memory types, structured note-taking, index-plus-detail, hygiene, MemOS-style lifecycle, MEM1, reconstructive memory.
7. [Structured context and schemas](notes/07-structured-context.md) — choosing a format, input/state/output schemas, knowledge graphs, schema design principles.
8. [Cognitive tools and prompt programs](notes/08-cognitive-tools.md) — the IBM cognitive-tools result, template families, the self-correction loop, prompt programs.
9. [Protocols](notes/09-protocols.md) — protocol shells, Pareto-lang, the protocol catalogue: context engineering without code.
10. [Multi-agent context and tool design](notes/10-tools-and-multi-agent.md) — sub-agent isolation, orchestrator-holds-plan, token-efficient tools, tool-integration patterns, orchestration and coordination.

**Practice**

11. [Context failure modes](notes/11-failure-modes.md) — rot, poisoning, distraction, clash, injection, and the diagnostic flow.
12. [Evaluating context](notes/12-evaluating-context.md) — the failure chain, metrics per lever, long-context sweeps, ablation, building the eval set.
13. [Putting it together](notes/13-putting-it-together.md) — the maturity ladder (atoms → cognitive systems), recurring patterns, four reference architectures, a capstone exercise.

**Appendix:** [99 — the speculative field track](notes/99-speculative-field-track.md) — neural fields, attractors, resonance, quantum semantics and the mental models, with what's grounded and what isn't (`confidence: low`).

### Notebooks

[notebooks/](notebooks/README.md) holds runnable Python labs from the upstream course:

| Lab | Pairs with |
|---|---|
| [01_min_prompt.py](notebooks/01_min_prompt.py) | [01](notes/01-why-context-is-finite.md), [02](notes/02-context-anatomy.md) |
| [02_expand_context.py](notebooks/02_expand_context.py) | [02](notes/02-context-anatomy.md), [03](notes/03-budgeting-the-window.md) |
| [03_control_loops.py](notebooks/03_control_loops.py) | [08](notes/08-cognitive-tools.md#the-self-correction-loop) |
| [04_rag_recipes.py](notebooks/04_rag_recipes.py) | [04](notes/04-retrieval.md) |
| [05_prompt_programs.py](notebooks/05_prompt_programs.py) | [08](notes/08-cognitive-tools.md#prompt-programs) |
| [06_schema_design.py](notebooks/06_schema_design.py) | [07](notes/07-structured-context.md) |
| [07_recursive_patterns.py](notebooks/07_recursive_patterns.py) | [08](notes/08-cognitive-tools.md), [99](notes/99-speculative-field-track.md) |

### Practice

| Lab | Notes |
|---|---|
| [01 — BM25 from scratch](practice/01-bm25-from-scratch/README.md): inverted index, IDF and saturation, with every score traceable (Li, Exp. 3-5). Offline, no API key | [04](notes/04-retrieval.md#hybrid-retrieval) |

### Templates

[templates/](templates/): `minimal_context.yaml`, schema templates ([YAML](templates/schema_template.yaml), [JSON](templates/schema_template.json)), [prompt_program_template.py](templates/prompt_program_template.py), [control_loop.py](templates/control_loop.py), [scoring_functions.py](templates/scoring_functions.py), and [prompt templates](templates/prompts/) (chain of thought, few-shot, minimal context, verification loop, expert guides).

### Related
- [memory-augmented-rag-notion-export.md](sources/memory-augmented-rag-notion-export.md) — memory depth: in-context, external, episodic, semantic.
- [skills-design.md](../03-harness-engineering/skills-design.md) — skills as a harness primitive; relies on the progressive disclosure covered in [04](notes/04-retrieval.md).

### Interviewing guide
- [5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md) — compressed summary for interview prep.

### Course code
- [LLMs-as-Operating-Systems--Agent-Memory-main](../../generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main/) — memory as an OS primitive.
- [Long-Term-Agentic-Memory-With-LangGraph-main](../../generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main/) — long-term memory patterns.

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
