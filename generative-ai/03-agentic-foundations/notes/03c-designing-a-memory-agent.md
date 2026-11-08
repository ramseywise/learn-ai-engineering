---
origin: synthesis
sources:
  - https://arxiv.org/abs/2607.26637
  - https://github.com/firstbatchxyz/mem-agent/blob/main/main.pdf
  - https://arxiv.org/abs/2409.07429
  - https://arxiv.org/abs/2502.12110
  - https://arxiv.org/abs/2508.09736
  - https://arxiv.org/abs/2601.01885
  - https://arxiv.org/abs/2601.03192
  - "Zhou et al. 2025, Memento — https://arxiv.org/abs/2508.16153"
  - "Agashe et al. 2024, Agent S — https://arxiv.org/abs/2410.08164"
  - "Wang et al. 2023, JARVIS-1 — https://arxiv.org/abs/2311.05997"
  - "Salama et al. 2025, MemInsight — https://arxiv.org/abs/2503.21760"
  - "Hu et al. 2023, ChatDB — https://arxiv.org/abs/2306.03901"
  - "Wang et al. 2026, Memex(RL) — https://arxiv.org/abs/2603.04257"
  - "Xu et al. 2026, Contextual Agentic Memory is a Memo — https://arxiv.org/abs/2604.27707"
  - "Zhou et al. 2026, Are We Ready For An Agent-Native Memory System — https://arxiv.org/abs/2606.24775"
  - https://arxiv.org/abs/2602.02007
  - https://arxiv.org/abs/2609.23986
  - https://arxiv.org/abs/2602.07755
confidence: high
cleaned: 2026-11-08
---

# 3c — Designing a memory agent

> The four levers you control, and what the 2023 to 2026 studies say about how much the memory agent should curate, what to write and how to retrieve it.

[Note 03](03-memory-as-an-operating-system.md) built the OS analogy and the Letta mechanics: tiers, self-editing blocks and heartbeats. This note is about the design decisions on top: how much the agent should curate, whether to keep raw records or distilled ones, how to retrieve, and whether to train the manager. Most results are small benchmarks from 2025 and 2026 preprints; each paragraph says what it was measured on.

---


From the course conclusion, the four things you control:

| Lever | Question |
|---|---|
| Prompts | What does the system prompt say about when to save and search? |
| Tools | Which memory tools exist, and do any have side effects outside memory? |
| Memory management | Block sizes, eviction policy, what gets summarized |
| Memory content | Initial persona and human blocks, preloaded archival documents |

How much should the memory agent curate? A controlled comparison of filesystem memory stores ([arXiv:2607.26637](https://arxiv.org/abs/2607.26637), Zhou et al., 2026-07) says less than you'd think. With gpt-5.4-mini building and searching the store, a verbatim dump of the conversations or one file per session matched or beat an agent-curated store on all four conversational benchmarks; on PersonaMem at 32k tokens, curation scored 37.5% against 78.1% for the dump, because the curator left superseded preferences standing as current (the right fact was still in the store for all 13 misses). Asking the agent to reorganize a store silently condensed it unless told to keep every fact: on REALTALK, a condensing reorganization dropped correctness from 77.6% to 41.2%, while a fact-preserving one held at 77.6%. Two budget rules follow. Spend model strength on the reader, not the writer: a stronger searcher raised mean correctness from about 62% (gpt-5.4-nano) to 79% (gpt-5.4), while a stronger builder "buys a more elaborate store, not a more useful one." And match stored experience to the executor: on ALFWorld, raw episode logs helped a gpt-4.1 executor most (87.1% vs. 73.6% with no store), but a gpt-4.1-mini executor did better with distilled task guidance (76.4% vs. 66.4% with logs). The study uses single build runs and 32–158 questions per benchmark tier, so read differences of a few points as ties.

The safe kind of curation edits the index, not the facts. A-MEM ([arXiv:2502.12110](https://arxiv.org/abs/2502.12110) (Xu et al., NeurIPS 2025)) stores each interaction as a Zettelkasten-style note: the raw content plus LLM-written keywords, tags and a one-line context, linked to related notes. When a new note arrives, the agent may rewrite its neighbours' keywords, tags and context, but never their content. On LoCoMo with GPT-4o-mini, scored by token F1, removing the linking and rewriting steps cut multi-hop F1 from 27.0 to 9.7. Against the whole conversation in context, the result looks like Mem0's. With GPT-4o, A-MEM won on temporal questions (39.4 vs. 9.1 F1) using about 1.2k tokens per question instead of 16.9k. It lost on single-hop questions (48.4 vs. 61.6) and on adversarial ones (36.4 vs. 52.6).

The verbatim result assumes there is a verbatim record to keep. For a video or audio stream there isn't one, so the writer has to extract something. M3-Agent ([arXiv:2508.09736](https://arxiv.org/abs/2508.09736) (Long et al., 2025-08, preprint)) turns each 30-second clip into episodic memory (what happened) and semantic memory (what it implies, such as "Alice likes coffee in the morning"), keyed to face and voice identities. With the reader held fixed, **dropping the semantic memories cut VideoMME-long accuracy from 61.8% to 48.7%**, and dropping the face–voice identity links cut it to 52.1%. On the authors' robot-view benchmark, dropping semantic memory cut accuracy from 30.7% to 13.6%. Here the writer mattered too. A Qwen2.5-Omni-7B fine-tuned to write memories beat prompted Gemini-1.5-Pro in the same role (61.8% vs. 52.7% on VideoMME-long), so the "spend on the reader" rule applies to text conversations, where the raw record can be stored as it is.

Memory of *how to do a task* raises the same choice between keeping the trajectory and keeping a distilled routine. Agent Workflow Memory ([arXiv:2409.07429](https://arxiv.org/abs/2409.07429) (Wang et al., ICML 2025)) turns successful trajectories into reusable workflows and adds them to the prompt. Example-specific values become placeholders such as `{product-name}`. In the online setting it learns from its own test-time runs, keeping those an LLM evaluator judges successful. With GPT-4 on WebArena, success rose from 15.0% (BrowserGym with the same accessibility-tree input) to 35.5%. The paper's own ablation agrees with Zhou et al., though. **Deduplicated raw trajectories did as well as LM-abstracted workflows on WebArena (35.6% vs. 35.5%)**, and on Mind2Web abstraction added 1.7 points of step success (43.4% to 45.1%). Wrapping workflows as callable tools changed little, because the agent called them in only 18.5% of tasks.

Retrieval is the other half. When stored experiences look alike, similarity is a poor proxy for usefulness. MemRL ([arXiv:2601.03192](https://arxiv.org/abs/2601.03192) (Zhang et al., 2026-01, preprint)) gives each stored experience a utility score. Each time the experience is used, task reward updates the score with a Monte Carlo rule, Q ← Q + α(r − Q). Candidates are first recalled by similarity, then re-ranked by an equal mix of similarity and utility. This is Generative Agents' importance score learned from outcomes instead of rated once at write time, and the idea goes back to episodic control in RL (Pritzel et al., ICML 2017). The model stays frozen. With GPT-4o-mini on Lifelong Agent Bench OS tasks, MemRL reached 78.8% success after 10 epochs, against 69.0% for similarity-only RAG and 73.6% for MemP. With GPT-5-mini on ALFWorld it reached 94.9%, against 88.7% for RAG. It needs a reward for every task, and the gain needs tasks that resemble each other. On HLE, where questions share little, cross-task retrieval tied reflecting on the same task alone (60.6% vs. 61.0%).

Memento ([arXiv:2508.16153](https://arxiv.org/abs/2508.16153) (Zhou et al., 2025-08, preprint)) is the same idea with a trained scorer: a frozen LLM planner (GPT-4.1) reads from a bank of (state, action, reward) cases, written once per finished task, successes and failures alike. Retrieval is by embedding similarity, or by a two-layer MLP trained as a success classifier. On DeepResearcher data over five passes, accuracy ended at 85.44 with the learned retriever, 84.85 with similarity and 84.47 with no case memory, so the retriever matters less than having cases at all (no seeds reported). Retrieving 4 cases was best (64.5 F1 across seven datasets, against 59.9 with none and 63.9 with 32), which the authors put down to noise from irrelevant cases.

Agent S ([arXiv:2410.08164](https://arxiv.org/abs/2410.08164) (Agashe et al., 2024-10, preprint)) splits experience by who uses it. A planner reads *narrative* memory, abstract summaries of whole tasks with the actions removed, and the executor reads *episodic* memory, grounded plans for subtasks that succeeded, both written by a self-evaluator without ground truth. On a 65-task subset of OSWorld with GPT-4o, the full system scored 26.15%; removing episodic memory gave 18.46, narrative memory 21.41, web knowledge 16.80 and all three 13.85. Storing full trajectories instead of evaluated summaries gave 18.46, and skipping the self-supervised exploration that seeds the memory gave 15.38. On all 369 OSWorld tasks it reached 20.58% against 11.21% for the best GPT-4o baseline. With 65 tasks, single-point gaps are noisy, and the exploration tasks come from the same environments as the test.

MemInsight ([arXiv:2503.21760](https://arxiv.org/abs/2503.21760) (Salama et al., 2025-03, preprint)) puts the structure in an annotation layer instead of the store. A zero-shot LLM mines attributes and values for each memory (turn-level or session-level) and, in its *priority* mode, orders them by relevance. The query is annotated the same way, and retrieval matches attributes or embeds the annotations. On LoCoMo question answering, with embedding retrieval at k=5 and Claude-3-Sonnet as annotator, **recall@5 was 60.5 overall against 26.5 for a DPR baseline**, and priority beat unordered annotation (48.8). The gain does not carry through to answers: F1 was 30.1 against 28.7 for DPR, and DPR won the adversarial questions (89.9 vs 75.3). On movie recommendation (LLM-REDIAL, 200 conversations) attribute filtering retrieved about 90% less memory than the baseline at comparable recall, and recall and NDCG did not improve. The authors name no cost or latency of annotating, run a single time, and compare against none of MemGPT, Mem0 or A-Mem. Annotation quality depends on the annotating model: they report 99.14% of Claude-3-Sonnet annotations grounded in the dialogue, with visible hallucinated attributes from Llama and Mistral.

ChatDB ([arXiv:2306.03901](https://arxiv.org/abs/2306.03901) (Hu et al., 2023-06, preprint)) goes further and makes the store symbolic: an LLM controller turns a request into a chain of SQL operations (insert, update, delete, select) on a database, rewriting later steps from earlier results, so state is current and arithmetic is done by the database. On a synthetic shop dataset (70 records, about 3.3k tokens, 50 questions) with GPT-3.5 Turbo at temperature 0, **ChatDB answered 41 of 50 (82%) against 11 of 50 (22%)** for the same model with the records in its prompt; on the 35 hard questions the gap was 28 against 1. It is one run on one synthetic set, the baseline is full-context prompting rather than RAG or MemGPT, and the claim that vector memory fails on multi-hop questions is argued, not measured.

JARVIS-1 ([arXiv:2311.05997](https://arxiv.org/abs/2311.05997) (Wang et al., 2023-11, preprint)) shows the lifelong version in Minecraft. Memory is a key-value store of tasks and observations mapped to plans that worked, and only successes are kept. An LLM first generates the sub-goals to look up, then candidates are ranked by visual similarity to the current state. Against DEPS, a memory-less planner baseline, the diamond-task group averaged 8.99% against 2.42%, with 2 to 3 re-planning rounds instead of more than 6. It had gathered 425 successful trajectories over four epochs, with no weight updates. The memory is filled on the same task pool it is tested on, never evicts, and the game was run in an easier mode (peaceful, permanent daytime), so the transfer claim is partly overlap.

The memory manager can also be a small model trained for the job. mem-agent from Dria ([mem-agent](https://github.com/firstbatchxyz/mem-agent/blob/main/main.pdf) (Tekparmak & Kaya, 2025-10)) trained Qwen3-4B-Thinking with GSPO to retrieve, update and ask for clarification over an Obsidian-style folder of markdown files, using Python file tools. On the authors' 56-sample md-memory-bench, scored by an LLM judge, the overall score rose from 0.39 to 0.75. That put it second of 11 models, behind Qwen3-235B-Thinking at 0.79 and ahead of GPT-5 at 0.63 and Claude Opus 4.1 at 0.55. The engineering lessons travel better than the leaderboard:
- **Format rewards get farmed.** Paying per well-formed turn taught the model to use all 8 turns. The fix was rewards that shrink each turn until halfway, then turn negative, plus double the reward for success.
- **Diffs are hard for small models.** A diff-based update tool failed, and they switched to `update_file(path, old_content, new_content)`.
- **Quantization costs judgment first.** The 4- and 8-bit builds sometimes invent facts instead of asking the user for clarification.

The benchmark is small and handmade, and the training data is synthetic from the same team, so treat 0.75 as an existence proof, not a ranking.

Two larger studies make the same point: tools let the agent manage memory, but they don't teach it when to. AgeMem ([arXiv:2601.01885](https://arxiv.org/abs/2601.01885) (Yu et al., 2026-01, preprint)) gives the agent MemGPT-style tools for both tiers: add, update and delete for the long-term store, and retrieve, summarize and filter for the context. It trains them with GRPO on HotpotQA only. When Qwen2.5-7B-Instruct was only prompted to use these tools, it never updated or deleted a memory (0.00 calls per episode). It averaged 33.4% across ALFWorld, SciWorld, PDDL, BabyAI and HotpotQA, against 28.1% with no memory and 37.1% with Mem0. **After RL it averaged 42.0%**, and Qwen3-4B went from 45.6% to 54.3%. The context tools saved only 3–5% of prompt tokens over plain RAG. M3-Agent's controller makes the same point for search. After RL, its 32B controller, which searches memory for up to five rounds, scored 61.8% on VideoMME-long, against 52.5% for the same model prompted. This is MemGPT's weak-function-calling limit again: a memory design works only as well as the model's tool use.

Three 2026 preprints attack the same problem from the structure, the control plane and the design process. All three are LoCoMo-style or game-world results from the authors' own reruns, with no variance reported for xMemory and Jev-Mem (ALMA reports standard error over three deployment runs).

- **Structure: split before you summarize.** xMemory ([arXiv:2602.02007](https://arxiv.org/abs/2602.02007) (Hu et al., 2026-02, preprint)) keeps four levels (messages, segments, extracted memory components, groups of components) and retrieves top-down, adding finer levels only while they lower the reader's answer uncertainty. Groups are split and merged as new components arrive. On LoCoMo with Qwen3-8B (greedy decoding, same model builds and answers), it scored **34.48 BLEU / 43.98 F1 at 4,711 tokens per query, against 31.44 / 40.88 at 7,755 for Nemori** and 27.95 / 36.48 at 8,633 for top-20 chunk RAG. Freezing the structure (no split, no merge) cut F1 to 38.59, and compressing the RAG chunks with LLMLingua-2 lowered F1 to 34.58 from 36.48. Construction is not free: 421.9k tokens against Nemori's 381.3k, so the saving is at query time, and the authors note that with few queries after construction a simpler retriever may be preferable. Tested on LoCoMo and PerLTQA only, at about 18k to 25k tokens of context, with answers capped at a few words.
- **Control: keep the model off the hot path.** Jev-Mem ([arXiv:2609.23986](https://arxiv.org/abs/2609.23986) (Jiang et al., 2026-09, preprint)) lets a small typed-output controller do the frequent bounded decisions (typing a new memory, scoring candidate links, routing a query, deciding when evidence is sufficient) and calls the LLM only to write the answer. On LoCoMo with gpt-4o-mini as the answerer and an LLM judge, it scored 0.777 against 0.700 for the best baseline (MAGMA), built memory in 158 s against 1,044 s for the fastest rival (Nemori), and answered in 0.93 s per query against 1.47 s. There is no ablation of controller against LLM control, the controller is a vendor product (TypeSafe AI's Jev), the run is single, and the authors share a first author with the strongest baseline, so the speed numbers show a configuration, not the principle.
- **Process: let the agent design the memory.** ALMA ([arXiv:2602.07755](https://arxiv.org/abs/2602.07755) (Xiong et al., 2026-02, preprint)) has a meta-agent write memory designs as code (update, storage and retrieval), score them on a learning set, and keep an archive it samples parents from. With a GPT-5-nano agent on four game-world benchmarks (ALFWorld, TextWorld, Baba Is AI, MiniHack), learned designs averaged **12.3% against 6.1% with no memory and 8.6% for the best of four hand-built designs**; moved unchanged to a GPT-5-mini agent they averaged 53.9% against 41.1% and 48.6%. Some hand-built designs hurt: on TextWorld, trajectory retrieval fell from 5.4% to 2.7%. On ALFWorld, archive sampling beat always expanding the best design (87.1% against 77.1% with GPT-5-mini). Designs are learned offline on a fixed set of tasks, three deployment runs, OpenAI models only, and none of the benchmarks is conversational memory.

Memex(RL) ([arXiv:2603.04257](https://arxiv.org/abs/2603.04257) (Wang et al., 2026-03, preprint)) makes the write and read decisions learned. `CompressExperience` replaces the working context with a short summary holding an index map and archives the full text under those indices in a key-value store, and `ReadExperience(index)` restores exactly that span, an exact lookup rather than a similarity match. Trained with GRPO on task reward minus penalties for context overflow, redundant calls and malformed calls, a Qwen3-30B-A3B-Thinking agent went from **24.22% to 85.61% success** on a modified ALFWorld and from 16,934 to 9,634 tokens of peak working context, still above the 8,000-token penalty threshold. Compress calls fell from about 6.5 to 3 per episode and reads rose from about 1 to 6 or 7. The comparison is the same agent before and after RL, with no other memory system as baseline; the environment was changed to force reads (one `look` per episode, summaries capped at 300 tokens), and it is one model with no seeds.

Xu et al. ([arXiv:2604.27707](https://arxiv.org/abs/2604.27707) (2026-04, position paper)) argue that MemGPT-style stores, RAG and Reflexion change only the context, never the model, so competence disappears when the stored trace is not supplied: a memo, not learning. Their theorem is conditional. If a frozen model stays below the target accuracy on held-out combinations of k concepts, retrieval needs on the order of k² stored examples where a parametric learner of complexity d needs about d. It is shown on modular arithmetic as an existence proof, and the authors say they provide no compute-matched frontier-model experiment. The security point is relayed from other papers: persistent writes carry an injection across sessions (MINJA, 98.2% injection success; PoisonedRAG, 90% with five texts per query). Their proposal keeps scoped, deletable episodic retrieval as the default and adds a separate asynchronous consolidation channel into adapters, with provenance, versioned checkpoints and regression guards.

A benchmark of agent memory systems ([arXiv:2606.24775](https://arxiv.org/abs/2606.24775) (Zhou et al., 2026-06, preprint)) compares a dozen of them with long-context and embedding-RAG baselines on LoCoMo, LongMemEval, DB-Bench and LongBench (GPT-5.4 judges LongMemEval). **No design won everywhere**: Zep led LongMemEval judge accuracy (48.0), MemOS led LoCoMo exact match (11.5) and plain long context led DB-Bench (48.20 EM). Keeping original text beat summarising it (LightMem on LoCoMo, 24.2 EM raw against 8.5 summarised), and heavier write-time extraction hurt (MemOS fine against fast memorize on LoCoMo, 2.5 against 25.5 EM). Letta scored 0.0 EM on LoCoMo. Single runs, no variance, many ablation gaps are a few tenths of a point, and the authors are affiliated with MemOS, one of the systems tested.


---

## Where curation can go wrong

```text
write time                    store                     read time
----------                    -----                     ---------
raw turn  -----------------> verbatim record  ------>  search (the reader's job)
   |                              ^
   +--> curator rewrites facts ---+   <- loses detail, leaves old preferences standing
   +--> curator edits index only -+   <- keywords, tags, links: the content is untouched
```

The studies above agree on where to put the judgment. Keep the record whole, let a model edit the index on top, and spend the strong model on reading.

The check below is a toy of our own, not a benchmark. Both stores see the same four turns. One keeps them verbatim and searches by word overlap. The other is "curated" into one summary line per session, which drops the detail the question needs.

```python
turns = [
    "Mon: Acme lead time is 2 weeks for itemB",
    "Tue: supplier Zed quoted 5 days for itemC",
    "Wed: user prefers email over phone",
    "Thu: Acme lead time changed to 4 weeks",      # supersedes Monday
]
summary = ["Discussed supplier lead times and contact preferences"]   # a lossy curation


def search(store, query):
    q = set(query.lower().split())
    return max(store, key=lambda doc: len(q & set(doc.lower().replace(":", "").split())))


q = "what is the Acme lead time"
print("verbatim:", search(turns, q))     # word overlap ranks Monday's stale line first
print("summary :", search(summary, q))   # the number is gone
```

Run it and the verbatim store returns Monday's 2 weeks, not Thursday's 4, because plain word overlap has no notion of which line is newer. That is the superseded-preference failure from Zhou et al. in miniature: keeping everything is not enough, so the index needs a recency or supersession field, which is the kind of edit A-MEM makes safely.

---

## Pitfalls

- **Curating the facts.** A curator that rewrote or condensed the store dropped PersonaMem accuracy to 37.5% against 78.1% for the verbatim dump, and a condensing reorganization cut REALTALK from 77.6% to 41.2%. Edit the index, not the content.
- **Spending the strong model on the writer.** A stronger builder "buys a more elaborate store, not a more useful one". A stronger searcher moved mean correctness from about 62% to 79%.
- **Assuming tools teach when to use them.** Prompted small models rarely updated what they stored (AgeMem). Put memory stats in the context, instruct the behavior, and test it by replaying conversations.
- **Reading a leaderboard from one team's handmade benchmark.** mem-agent's 0.75 is on 56 samples with synthetic training data from the same team, so it is an existence proof.
- **Distilling away the only copy.** Abstracted workflows matched deduplicated raw trajectories on WebArena (35.5% vs. 35.6%). Keep the raw record.
- **Trusting context-only memory to change the agent.** Xu et al. argue that stores, RAG and Reflexion change only the context, not the weights.

---

## Try it

1. Make the toy's recency problem go away without touching the stored turns. What field does the index need, and who writes it?
2. You have budget for one stronger model in a text-conversation memory system. Do you put it on writing the store or on searching it, and what evidence supports that?
3. A video assistant has no verbatim record. What should the writer produce, and which ablation shows it matters?

<details>
<summary>Answers</summary>

1. A timestamp or supersedes link on each entry, written at index time and used to prefer the latest match. The curator edits only that field, as A-MEM edits keywords and links without touching content.
2. The searcher. Zhou et al. moved correctness from about 62% to 79% with a stronger searcher, while a stronger builder gave a more elaborate store but no more useful one.
3. Episodic memory (what happened) and semantic memory (what it implies), keyed to identities. In M3-Agent, dropping the semantic memories cut VideoMME-long accuracy from 61.8% to 48.7%.

</details>

---

## Interview checklist

| Question | Short answer |
|---|---|
| What are the four levers on a memory agent? | Prompts, tools, memory management (block sizes, eviction, summarizing) and memory content (persona, preloaded archive). |
| Should the agent curate its memory? | Mostly not. Verbatim or per-session stores matched or beat agent-curated ones on four benchmarks; curation left stale preferences standing. |
| What is the safe curation? | Edit the index (keywords, tags, links) and leave content untouched, as A-MEM does. |
| Where do you spend model strength? | On the reader. A stronger searcher helped; a stronger builder did not. |
| Raw records or distilled guidance? | Match it to the executor: logs helped a stronger executor, distilled guidance a smaller one. Keep the raw record regardless. |
| Why do tools not make a good memory manager? | They give the ability, not the judgment of when to save or search. That has to be instructed, measured or trained. |
| Can a small model be a memory manager? | With RL, yes in one benchmark (mem-agent, 0.39 to 0.75), but the benchmark is small and handmade. |

---

## Next

→ [03b — learning from experience](03b-learning-from-experience.md) (what to keep from past runs, and whether it transfers), then [04 — multi-agent design patterns](04-multi-agent-design-patterns.md). Back to [03 — memory as an operating system](03-memory-as-an-operating-system.md#pitfalls) for pitfalls.
