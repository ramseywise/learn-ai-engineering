---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://developers.openai.com/api/docs/guides/compaction
  - https://github.com/davidkimai/Context-Engineering (00_COURSE/02_context_processing/01–02, 00_COURSE/03_context_management/01–04) — snapshot 2026-08-14)
  - "Bojie Li, AI Agents in Depth (2026), ch. 2 — https://github.com/bojieli/ai-agent-book"
  - https://arxiv.org/abs/2610.28577
  - https://arxiv.org/abs/2310.08560
  - https://arxiv.org/abs/2608.22752
  - https://arxiv.org/abs/2608.11242
  - https://arxiv.org/abs/2610.02163
  - https://papers.voltropy.com/LCM
  - https://arxiv.org/abs/2609.37725
  - https://arxiv.org/abs/2512.24601
confidence: high
cleaned: 2026-10-31
---
# 5 — Compression and Compaction

> What to do when the window fills anyway. The technique that makes long-horizon agents possible.

---

## Compaction

**Compaction** is an orchestration process that transforms a large interaction history into a smaller continuation state. Near the context limit, summarize what has happened, reinitialize the window with the summary, and continue.

It is the difference between an agent that dies at the window limit and one that runs for hours. Without it, a long task ends when the window fills. With it, the task continues at a fraction of the token cost.

### Compress for quality, not only for length

The second reason to compress applies before the window fills. **In-context learning behaves more like retrieval than reasoning.** Ten searches scattered across 50k tokens make the model hunt for fragments at every decision. One structured summary ("Known: A…, B…; still missing: C") turns a conclusion that had to be reasoned into one that can be looked up. The usual failure is not a window that is too small but **information density that is too low**: occasionally needed knowledge loaded on every call, stable rules mixed in with dynamic state. That is *context rot*: everything fits, but the key fact can't be found ([11](11-failure-modes.md#context-rot)). The status bar *adds* distilled conclusions; compression *replaces* raw records with them ([02](02-context-anatomy.md#runtime-state-the-agent-status-bar)).

### The pipeline

```
Raw interaction history
        ↓
Prune irrelevant content          <- abandoned branches, superseded attempts
        ↓
Replace bulky tool outputs        <- keep the conclusion, drop the payload
        ↓
Extract structured task state     <- files touched, decisions, open TODOs
        ↓
Summarize older reasoning         <- compress the middle, lossy but bounded
        ↓
Preserve recent messages verbatim <- the last N turns stay untouched
        ↓
Compact continuation context
```

The final step matters most. Recent turns stay **verbatim** because the agent's immediate working state lives there — half-finished edits, the error it is currently debugging. Summarizing the last three turns is how a compaction loses the thread.

### Retention priority

What survives compaction, in order:

1. **Architectural decisions — do not summarize.** "We chose X over Y because Z" must survive verbatim. Lose the reasoning and the agent re-litigates a settled decision, or silently contradicts it.
2. **User constraints and safety rules — pin verbatim, outside the summary.** "Don't delete emails until I confirm." "Patient is allergic to penicillin." A rule stops being enforceable once it is paraphrased.
3. **Modified files and critical changes.** The diff-so-far is state, not history.
4. **Verification status — pass/fail.** Which tests ran and what happened.
5. **Unresolved TODOs and rollback notes.** Everything not yet done.
6. **Tool output — deletable.** Retain the pass/fail conclusion, discard the payload.

The asymmetry between 1–2 and 6 is the core insight. A 40k-token test output compresses to "17 passed, 2 failed: `test_auth_retry`, `test_token_refresh`" with essentially no loss. A one-sentence architectural rationale cannot be compressed at all without losing what makes it useful.

Item 2 is the one that general-purpose compactors drop. A summarizer cannot tell which sentence is a rule, so it compresses rules at the same rate as everything around them. On 20 production agent configurations, "Claude Code's /compact prompt on Sonnet 4.6 preserves 53% of safety rules after one compaction round and 10% after five" at 50% compression per round. No type-blind strategy the authors tested beat 0.53 recall in a single round ([arXiv:2608.22752](https://arxiv.org/abs/2608.22752) (Zerhoudi et al., 2026-08)). A separate study of several compactors found they keep only 17% of injected user constraints on average. In one inbox test (gpt-oss-120b, compacting at 100K tokens), the agent deleted emails without approval in 30 of 100 sessions after compaction, against none before it ([arXiv:2608.11242](https://arxiv.org/abs/2608.11242) (Wang et al., 2026-08)). Having the user restate the rule in the first turn after compaction only got that down to 13 of 100.

Both papers fix it the same way: take the rules out of the summary's hands.
- **Wang et al.** use a small extractor (Qwen3.5-9B) to build a constraint registry and append it verbatim after the summary. Retention rose to 90–95%, and compliance came within a few points of the uncompacted upper bound.
- **Zerhoudi et al.** classify each line by type and pin constraints and procedures unchanged. Their TypeCompact held 0.96 recall over five rounds. A deterministic check then confirms every pinned rule survived. That check matters: without it, configurations that reported 1.00 recall had silently dropped a mean 57% of the constraints. Classification has its own blind spot. Rules phrased as plain facts, like the penicillin allergy, were recognized only 62% of the time by gpt-5.4-mini.

![Constraint recall over five sequential compaction rounds: TypeCompact vs. Sonnet 4.6 /compact vs. gpt-5.4-mini](../sources/images/zerhoudi-compaction-cliff-fig3.png)

*Image Source: Zerhoudi, Mitrović & Granitzer, [The Compaction Cliff in Long-Running AI Agent Memory](https://arxiv.org/abs/2608.22752) (2026), Fig. 3*

### Trigger points

- Approaching the window limit (~80% is a common threshold)
- **Phase boundaries** — a completed plan step, a finished skill invocation, a focus switch
- Before spawning subagents that will re-derive context
- After large reads that won't be needed again

Phase boundaries are the better trigger. Compacting at a natural seam produces a clean summary; compacting mid-edit at 95% occupancy forces a summary of an incoherent state.

A model can learn to pick the seam itself, but prompting alone does not get it there. In AutoCompact's experiments, "the base model rarely invoked compact() before the context limit, even when compaction rules were specified." After SFT and RL on when and what to compact, Qwen3-Coder-30B-A3B scored 39.6% on SWE-bench Verified. The same model scored 30.4% keeping full history in a 256K window, and 28.8% compacting at a fixed 16K length ([arXiv:2610.02163](https://arxiv.org/abs/2610.02163) (Zhang et al., 2026-10)). Proactive compaction helped even in the 256K setting, where nothing overflows. Dropping stale context is worth doing for quality, not only for room.

**Identifiers survive verbatim.** UUIDs, hashes, IPs, ports, URLs, filenames, PR numbers. Change one digit and the next tool call fails. Summarizers also tend to drop what *looks* re-acquirable: early decisions, the reasons behind constraints, and failed paths. Those are exactly what retention items 1–5 protect.

`~/.claude/rules/context-health.md` codifies this: sessions past 150k cost ~5× per turn with no cache benefit on the overflow. Compaction is one turn; carrying stale context is a cost on every subsequent turn.

---

## The component techniques

Compaction composes these; each is usable independently.

| Technique | What it does | Loss profile |
|---|---|---|
| **Sliding window** | Keep the last N turns, drop older | Total loss of dropped content |
| **Summarization** | LLM-compress a span into prose | Lossy, unpredictable — depends on the summarizer |
| **Pruning** | Delete content by rule (dead branches, superseded attempts) | Total but targeted; safest when rule-driven |
| **State extraction** | Pull structured facts into a compact record | Lossless for what's extracted, total for what isn't |
| **Tool-result clearing** | Replace raw tool output with its conclusion | Near-lossless for verbose output |

**Tool-result clearing** is the highest-value / lowest-risk of these — a lightweight compaction that strips raw tool outputs from history while keeping the fact that the call happened and what it concluded. Tool output is usually the largest and least reusable content in an agent's window. Clear it first, before reaching for lossy summarization. Clear it **in batches**, though, not every turn: each clearing rewrites the prefix ([below](#prompt-caching-interaction)).

### Six strategies compared

![Comparison of Context Compression Strategies](../sources/images/li-ai-agents-in-depth-fig2-16.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter2.md) (2026), Figure 2-16: Comparison of Context Compression Strategies (Apache-2.0)*

Li's Experiment 2-9 tracks OpenAI co-founders' current roles with Kimi K3 capped at a 128K window. Seven searches returned about 367k characters.

| Strategy | Result |
|---|---|
| No compression | Overflowed at iteration 5. Task failed |
| Summarize each result separately (10.9%) | Done in 12 iterations, 277k tokens; repeated facts across pages |
| One combined summary (4.3%) | 10 iterations, 93k tokens; very long inputs truncated at the tail |
| **Context-aware** (prompt includes the query and the known state) (~3.0%) | **7 iterations, 40k tokens**. One 148k-char page compressed to 2k chars and kept every name and role change |
| Context-aware + citations (4.1%) | 223k tokens. Lossy content, lossless index back to the sources |
| Adaptive window: batch at 80%, `[COMPRESSED]` marker so nothing is compressed twice | 175k tokens; full fidelity during the early broad-gathering phase |

The design principles: information value is uneven (decision points > evidence > noise). Keep semantics intact ("Sutskever left OpenAI in May 2024", not "Sutskever left"). The same text should compress differently for different tasks. And *compression is understanding*, so the compressor needs near-main-model capability. Context-aware compression cut tokens by more than 75%. Lab: [2-9 context-compression](https://github.com/bojieli/ai-agent-book/tree/main/chapter2/context-compression).

### The production ladder

Claude Code layers five mechanisms, cheapest and most cache-controllable first:

1. **Tool-result budget.** Large outputs go to disk and the model sees a preview. The replacement is frozen so the cache stays consistent.
2. **Delete noise outright.** Summarizing junk wastes tokens.
3. **API-level micro-compaction** (server-side context editing). Free to implement, but it still breaks the cache after the edit point, so save it for near-overflow.
4. **Archival per-turn summaries** ("`git log`, not `git squash`"), which keep the thread of the conversation.
5. **Full LLM compaction**, as a last resort. Session memory is tried first, and a **circuit breaker** stops sessions stuck in compaction-failure loops.

Lossless Context Management (LCM) applies the same ideas outside Claude Code ([papers.voltropy.com/LCM](https://papers.voltropy.com/LCM) (Ehrlich & Blackman, 2026-02)). Every message and tool result goes to an immutable store. The summaries the model sees are "a derived cache; the immutable history remains the sole source of truth", and the agent can grep or expand back into the originals. Its compaction escalates through three levels, and the last one is a deterministic 512-token truncation with "No LLM involved". That guarantees each pass shrinks the context, which is the same job Claude Code's circuit breaker does. LCM's authors are a vendor, and they report a single benchmark. On OOLONG with Opus 4.6, their agent averaged 74.8 against Claude Code's 70.3 across 8K–1M tokens. Claude Code was slightly ahead at 8K and 16K. The paper also concedes that "we cannot deterministically guarantee that the agent will always" recover what it needs from the store.

### Letting the model edit its own context

The ladder above is a harness deciding what the model sees. **Context Language Models** (CLMs) hand that job to the model. The live context is exposed as a file, which the model reads and rewrites with ordinary shell commands. It decides when to drop, summarize, or restore a span ([arXiv:2609.37725](https://arxiv.org/abs/2609.37725) (Shao et al., 2026-09)). Run zero-shot on Qwen3.6-27B with a 32K limit, CLMs scored 59.4% on BrowseComp-Plus. That was 11.4% (relative) above the strongest baseline, Codex-style summarization, and used 21.5% fewer prefix-reuse FLOPs. Three caveats:
- A small model needs training first. Qwen3.5-9B as a CLM trailed the summary harness until online RL.
- An edit in the middle of the context invalidates the prefix cache from that point ([below](#prompt-caching-interaction)). The authors' serving fix, Suffix Cache Reuse, cut server compute by 35% but needs a self-served engine.
- "Editable context can become another channel through which prompt injections or self-generated instructions persist across turns."

### Isolation beats compression

Compression removes bulk after it has landed. **Sub-agent isolation** keeps it out of the window altogether. "Find the payment-callback handler" done in the main loop drags in dozens of files. Delegated, it costs two messages: the task, and "`handle_callback` in `src/payment/callbacks.py`, plus 2 call sites". It needs no extra summarizer call and leaves the parent's prefix untouched. The price is a self-contained brief, because the sub-agent doesn't see the parent's context ([10](10-tools-and-multi-agent.md)).

The same idea applies to the input itself. A **Recursive Language Model** (RLM) never puts a long prompt in the window. The prompt sits as a variable in a Python REPL. The model writes code to inspect and slice it, and calls sub-models on the pieces ([arXiv:2512.24601](https://arxiv.org/abs/2512.24601) (Zhang et al., 2025-12)). On OOLONG-Pairs at 32K tokens, where the answer depends on pairs of lines throughout the input, GPT-5 scored 0.1 F1 both alone and with a summarize-on-overflow agent. As an RLM, with GPT-5-mini handling the sub-calls, it scored 58.0. On BrowseComp-Plus over 1,000 documents (6–11M tokens), the RLM reached 91.3% against the compaction agent's 70.5%. The authors' conclusion: "compaction is rarely expressive enough for tasks that require dense access throughout the prompt." Compaction decides once what to keep. An RLM keeps everything and decides per query what to read. The costs are latency (the sub-calls run one after another), a long tail of expensive runs, and weaker results with weaker models.

**State extraction** is what makes compaction safe. If task state lives in a structured record — files touched, decisions, open items — rather than being implicit in the prose of the conversation, then summarizing the prose costs little. Agents that write their state down survive compaction; agents that keep it in the transcript do not.

---

## Compression vs. compaction

Different scopes, often conflated:

- **Compression** — reducing an individual artifact before it enters the window (a query-conditional document summary, a truncated tool result). Applies per-item, pre-injection. See [04-retrieval.md](04-retrieval.md).
- **Compaction** — reducing the accumulated *history* into a continuation state. Applies to the whole window, mid-session.

You need both. Compression bounds what each item costs; compaction bounds what the session costs.

---

## API-level support

OpenAI's Responses API exposes compaction directly: after appending output items, drop items preceding the most recent compaction item. The latest compaction item carries the context needed to continue, so earlier items are dead weight — removing them shrinks requests and cuts long-tail latency.

The general pattern: **the compaction item is a checkpoint**, and everything before a checkpoint is discardable.

---

## Crash recovery

Related failure mode with the same solution. For long-running tasks, write task progress **to disk**, not just to context. Then a crash, a context overflow, or a deliberate restart resumes from the last checkpoint instead of restarting the task.

Rule of thumb: past roughly thirty minutes of agent runtime, crash recovery is mandatory rather than optional. The probability of *some* interruption over a long run approaches one.

This is the same mechanism as structured note-taking — see [06-memory.md](06-memory.md). State on disk survives everything that happens to a context window.

---

## Prompt caching interaction

Compaction **invalidates the cache from the compaction point forward** — you have rewritten the prefix. That is fine and worth it, but it means:

- Don't compact more often than necessary; each compaction pays a full re-prefill
- Structure the post-compaction window so the stable parts (system prompt, tools) still lead, preserving a cacheable prefix for subsequent turns
- Compacting at phase boundaries amortizes this cost across the phase that follows

**Rolling edits are the expensive case.** Trimming text on every turn, for example keeping only the last 12 tool responses, rewrites the prefix each round. With GPT-OSS-120B on 100 BrowseComp-Plus tasks, that cost **1.85× the full-context baseline**, because every turn re-prefilled. Summarizing at a 48K threshold was about 7% cheaper than full context but lost 5 accuracy points ([arXiv:2610.28577](https://arxiv.org/abs/2610.28577) (Fu et al., 2026-10)). The same rolling drop done on the KV cache instead of the text came out ahead on both: **+1.7 points at 27.7% lower cost** than threshold summarization, averaged over 3 open-weight models and 4 agent benchmarks. That requires a self-served engine ([03](03-budgeting-the-window.md#cache-engineering-edit-the-kv-cache-not-the-text)). On a hosted API the lesson runs the other way: rewrite the history rarely and in large blocks.

---

## Memory hierarchies

The upstream management module borrows the CPU cache model. Context lives at levels of decreasing cost and immediacy:

| Level | Holds | Access | Analogy |
|---|---|---|---|
| **L1: window** | Current task, recent turns, active evidence | Free; always attended | Registers / L1 cache |
| **L2: session store** | Compacted summaries, tool results, scratch files | One tool call | RAM |
| **L3: long-term** | Memory store, indexed corpus | Retrieval | Disk |

MemGPT made this design concrete: the agent manages its own tiers through tool calls, and summarized history is evicted to a searchable recall store. In its multi-session recall test, GPT-4 went from 32.1% to 92.5%, against a baseline that saw only a summary of past sessions ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560) (Packer et al., 2023-10); mechanics and caveats in [agentic foundations 03](../../../generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system.md#the-os-analogy)).

The useful habit is thinking in **promotion and demotion**. Compaction demotes content from L1 to L2. Retrieval promotes it back. A good design makes both moves cheap and explicit, rather than letting the window be the only tier ([06](06-memory.md)).

---

## Compression techniques beyond summarisation

| Technique | How | Notes |
|---|---|---|
| **Extractive** | Keep the sentences that matter verbatim | Faithful; cites cleanly; less compression |
| **Abstractive** | Rewrite into a shorter form | Higher ratio; can introduce errors |
| **Hierarchical summarisation** | Summarise chunks, then summarise the summaries | Scales to very long inputs; detail lost at each level |
| **Token pruning** (LLMLingua-style) | A small model drops low-information tokens | 2–5× with modest loss on many tasks; output is unreadable to humans |
| **Query-conditioned** | Compress *relative to the current question* | Highest relevance per token; must be redone per query |

### Self-refinement as a compaction pass

The upstream processing module describes self-refinement (generate → critique → revise) as a quality technique. It also works as a compaction step: ask the model to rewrite its working notes into the state schema ([07](07-structured-context.md#2-state-schemas--what-carries-across-turns)), then verify that the required facts survived ([12](12-evaluating-context.md)).

---

## Working reference

`~/.claude/refs/agent-context.md` — the Compress lever, compaction triggers, and what must survive.
`~/.claude/rules/context-health.md` — the 150k threshold and phase-boundary discipline.

---

→ Next: [06-memory.md](06-memory.md) — persisting state outside the window entirely.
