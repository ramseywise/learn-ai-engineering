# Context Engineering & Cost/Latency — Study Guide

"Context engineering" has replaced "prompt engineering" as the interview keyword: managing
what the model sees across a whole system, plus the cost/latency consequences. Root problem
to name: **context rot** — transformer attention degrades as context fills; more context is
not better context.

## 1. The five context layers (organize any answer with this)

Manage information by **usage frequency, stability, and enforcement requirement** — keep the
active context small, retrieve the rest on demand:

1. **Persistent instruction layer** — identity, invariants, safety constraints, project
   conventions. Short, stable, always loaded (the CLAUDE.md/AGENTS.md role).
2. **On-demand knowledge layer** — skills, playbooks, long references. **Progressive
   disclosure**: only name + description ("what + when") stay visible; full content loads
   when activated.
3. **Runtime injection layer** — date, user/tenant, permissions, task status. Assembled
   programmatically per turn, never baked into the system prompt.
4. **Long-term memory layer** — compact index + retrievable topic files, not a transcript;
   editable and auditable (wrong memories must be removable).
5. **Deterministic system layer** — things the model must *never* get wrong don't belong in
   context at all: encode as hooks, validators, permissions, schemas. "The model may ignore
   an instruction; a code-level control won't."

## 2. Compaction (long-conversation survival)

Pipeline: prune irrelevant → replace bulky tool outputs → extract structured task state →
summarize older reasoning → keep recent messages verbatim → compact continuation state.

Retention priority when compacting: (1) architectural decisions — never summarize away,
(2) modified files/critical changes, (3) verification pass/fail status, (4) open TODOs +
rollback notes, (5) tool outputs — drop, keep only conclusions.

Related mechanics: sliding windows; summarization nodes (e.g. trigger at N messages with
overlap, done by a small model); **tool-call offloading** — keep head+tail of big tool
outputs in context, full output to filesystem; post-compaction request trimming (drop items
before the latest compaction item — cuts long-tail latency).

## 3. Prompt / prefix caching (the cost answer)

Mechanism: inference = **prefill** (process prompt) + **decode** (generate). Caching saves
the prefill KV state and reuses it when a future prompt shares a **byte-identical prefix**.

Consequences you should recite:
- **Ordering matters enormously: static content first, dynamic last.** System prompt + tool
  schemas up top; user query + retrieved chunks at the end.
- Anything injected per-turn into the "static" region (timestamps, callables) silently
  breaks caching.
- Savings: ~90% of input cost and proportional TTFT on cache hits; TTLs are short
  (minutes) — cadence matters.
- Verify, don't assume: check `cache_read_input_tokens` in API usage stats.
- Architecture implication: a **single agent with a stable prefix caches better than N
  agents each with their own context** — a real reason to prefer skills-based single-agent
  over multi-agent topologies.

**Semantic caching** (different thing): cache *answers* keyed by query similarity — a
zero-retrieval-cost path for paraphrase queries, with threshold tuning to avoid serving
wrong cached answers. Know both and distinguish them; interviewers conflate deliberately.

## 4. Skills design (progressive disclosure done right)

- Write skill descriptions like routing logic: when to use, when *not* to, outputs/success
  criteria — in ~10 tokens, not 45.
- Add negative examples ("don't invoke when…") to cut misfires.
- Put templates/examples *inside* the skill — free when unused.
- When determinism matters, tell the model explicitly to use the skill.
- Skills close the accuracy gap between single-tool calls and multi-tool orchestration by
  making tool reasoning procedural — without bloating the system prompt.

## 5. Cost/latency levers (rank-ordered)

1. Prefix caching (free money if prompt ordering is right)
2. Model routing — small model for classification/rewrite/grading, big model for synthesis
3. Streaming (perceived latency; also required inside serverless timeout budgets)
4. Semantic cache for repeat/paraphrase traffic
5. Compaction + tool-output offloading (smaller requests = faster + cheaper)
6. Output-length discipline and structured outputs (decode tokens cost more than prefill)
7. Batch/offline jobs for non-interactive work (overnight embedding refresh, summaries)

Have one number ready: p95 budget decomposition of your own pipeline (see the
[rag guide](../3-rag/interview-guide.md) §5 for a worked budget).

**Report cost per *successful* task, not cost per call.** An agent that retries three times
and still fails is cheap per call and infinitely expensive per outcome; the per-call number
hides it. Track cost per step → per conversation → per successful task, and quote the last
one — it's the only figure that moves with quality as well as spend.

## 6. Question bank (answer sketches)

- *"Your token bill doubled — walk me through it."* — usage stats: cache hit rate first
  (ordering regression?), then per-route token histograms (agent circling → long dialogues),
  tool-output bloat in context, model-routing drift; then fix in lever order.
- *"How do you keep a 100-turn conversation coherent?"* — compaction pipeline + retention
  priorities + state externalization to files; memory index for cross-session facts.
- *"System prompt is 8K tokens and growing."* — split by the five layers: invariants stay,
  knowledge → skills (progressive disclosure), dynamic → runtime injection, enforcement →
  code. Measure cache hit rate before/after.
- *"Where do you put retrieved context and why?"* — after the static prefix (caching), close
  to the question (recency/attention), with token budget enforcement + summarization
  fallback.

### From *AI Agents in Depth* (Li)

Condensed from the book's [reference answers](https://github.com/bojieli/ai-agent-book/blob/main/book-en/reference-answers.md) to its chapter thought questions; the book flags them as AI-drafted with light human review.

- *"A sliding window made the agent repeat tool calls, full history explodes — design?"* —
  append only; at ~80% of the window, compress old tool results once; persist large outputs
  to disk with a summary; isolate intermediate work in sub-agents. That keeps the KV-cache
  prefix intact.
- *"Reasoning content across hundreds of tool calls?"* — keep recent reasoning in full and
  roll older reasoning into a structured status (goal, confirmed facts, ruled-out paths,
  to-dos) once, at a fixed point. DeepSeek R1 stripped history CoT (cheap, cache-friendly,
  but no long-range plan); V4 mandates passing it back. For agents, reasoning is state.
- *"148K characters compressed to 2K — irreversible loss?"* — yes, so pair lossy compression
  with lossless indexing: source URLs per fact, raw outputs on disk, verbatim retention of
  decisions, dates, names and IDs.
- *"The status bar itself is wrong?"* — the model trusts it unconditionally. Maintain it in
  code, never by an LLM counting history; track its accuracy as a metric; feed it only from
  real observations.
- *"Many people edit one system prompt — how does it stay clean?"* — prompts as code with
  review; benchmark regressions before and after; enforced structure (SOP, XML/Markdown
  layers); fragments labelled cacheable vs cache-breaking; bloat split into Skills.
- *"The model can't know which Skill it needs?"* — keep Skill names and descriptions
  resident, and write descriptions as routing conditions ("use when / don't use when").
- *"Where should a loaded Skill be injected?"* — system prompt: strongest adherence, breaks
  the cache. Mid-context as a file read: cache-safe, weaker adherence. End of context: good
  adherence, recomputed every call.
- *"Large, changing tool set — maximise cache hits?"* — a small frozen core of tools in
  fixed order in the static prefix, a generic executor, capabilities via Skills; sub-agents
  share the parent's prefix.

## Sources

- notes: [notes/](../../../ai-engineering/02-context-engineering/notes/) (5 layers + compaction + caching notes), [context-engineering.md](../../../ai-engineering/02-context-engineering/context-engineering.md) (skills tips), [agent-harness.md](../../../ai-engineering/03-harness-engineering/agent-harness.md) (offloading, progressive disclosure)
- librarian wiki: Prefix Caching · Semantic Cache Pipeline · ADK Context Engineering · Summarization Node · HistoryCondenser · Multi-Agent Orchestration Patterns (caching-driven topology choice)
- readings: `ai_engineering/multiagent context/`
- external: developers.openai.com compaction guide · openai skills-shell-tips post
