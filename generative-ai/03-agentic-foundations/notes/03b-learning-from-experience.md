---
origin: synthesis
sources:
  - "Guan et al. 2026, ContinualSkillBench — https://arxiv.org/abs/2608.03874"
  - "Kim et al. 2026, Memory Transfer Learning — https://arxiv.org/abs/2604.14004"
  - "Tang et al. 2026, From Memory to Skills (MSCE) — https://arxiv.org/abs/2607.16621"
  - "Wu et al. 2026, AutoMem — https://arxiv.org/abs/2607.01224"
  - "Yao et al. 2026, AtomMem — https://arxiv.org/abs/2606.19847"
  - "Ho et al. 2025, ArcMemo — https://arxiv.org/abs/2509.04439"
  - "Chang et al. 2026, MemCollab — https://arxiv.org/abs/2603.23234"
  - "Quek et al. 2026, MEMO: Memory as a Model — https://arxiv.org/abs/2605.15156"
  - "Qiao et al. 2026, Memory Intelligence Agent — https://arxiv.org/abs/2604.04503"
  - "Li et al. 2026, OCR-Memory — https://arxiv.org/abs/2604.26622"
  - "Xiao et al. 2026, Zero-Mem — https://arxiv.org/abs/2607.29377"
  - "Yu et al. 2026, Recuris — https://arxiv.org/abs/2608.24876"
  - "Bousetouane 2026, AI Agents Need Memory Control — https://arxiv.org/abs/2601.11653"
  - "Srinivasan 2026, Stateless Decision Memory — https://arxiv.org/abs/2604.20158"
  - "Piskala 2026, MAPLE — https://arxiv.org/abs/2602.13258"
confidence: medium
cleaned: 2026-11-06
---

# 3b — Learning from experience

> An agent that keeps what it did last time can do better next time, but only if what it keeps transfers. Most of the evidence says keep the raw record, distill sparingly, and test whether the store helps at all.

[Note 03](03-memory-as-an-operating-system.md) gave the restock agent a core and an archive so it remembers *facts*: the supplier's lead time, the manager's name. This chapter is about remembering *how*: the workaround that got a stuck order through, the check that caught a bad forecast. Stored this way, experience becomes a skill file, a list of insights or a bank of past trajectories that the agent reads before its next task. The idea is attractive because it promises learning without training. The risk is a store that grows, costs tokens on every call and teaches the agent nothing it would not have done anyway. [03's memory-agent section](03-memory-as-an-operating-system.md#designing-a-memory-agent) already showed raw trajectories matching distilled workflows (Agent Workflow Memory) and verbatim stores beating curated ones; this chapter asks what to distill, whether it transfers and who should write it.

---

## Skill libraries against plain context

ContinualSkillBench tests the skill-file version directly ([arXiv:2608.03874](https://arxiv.org/abs/2608.03874) (Guan et al., 2026-08, preprint)). Agents worked through ordered streams of 100 tasks per domain in Law, Finance, Healthcare, Office and Math, inside Codex CLI and Claude Code, and after each task they could create or edit `SKILL.md` files from evaluator feedback. The streams do offer reuse: 69.5% of eligible tasks need a core skill seen earlier. Keeping experience across tasks helped. Against a reset before every task, sequential runs raised normalized reward in 14 of 15 model–domain pairs, by 0.078 on average. **But the skills were not what helped.** With GPT-5.3-Codex and Claude Opus 4.7 on Law, Finance and Healthcare, an in-context baseline that saw the same task history and feedback but could not write skills scored 0.585, against 0.582 with skills and 0.469 with neither.

The split by task type tells you when to bother. Skills beat or tied plain context on every exact-match comparison (5 of 6 better, 1 tie) and on 5 of 6 programmatic ones, and lost on 5 of 6 open-ended rubric comparisons, where the authors suspect skills over-specialize to earlier solutions. The writer matters too. Across all five domains, GPT-4o wrote 384 skills averaging 5.68 on a quality rubric and called them less; GPT-5.3-Codex kept 205 averaging 7.94 and reused them more. A bigger library was a worse one. An open-source pilot with Qwen3-32B was stopped after 32 tasks because the agent could not execute reliably (118 of 208 shell commands failed), so there was no signal to learn from. The comparison covers two frontier models and three domains, with LLM-judged rubrics and no variance reported.

For the restock agent: a skill file earns its place for procedures with a fixed output, such as the reorder calculation or the purchase-order format. For judgement calls, the history and feedback in context did as well.

Recuris separates the skill library from a verified record of where the current task stands, and finds the second does most of the work ([arXiv:2608.24876](https://arxiv.org/abs/2608.24876) (Yu et al., 2026-08, preprint)). On τ²-Retail (114 tasks, 4 runs each, one mid-sized deployment model), a base agent with no memory solved 58.1%. **Adding ten distilled skills alone was worth +2.0 points, with a 95% interval of −4.0 to +7.9; adding a verified task-state tracker alone was worth +23.9**, and both together +25.4. How the skills enter matters too. Putting the whole library in the prompt every turn and letting the model decide when to use it scored 65.6%, below the same harness with no skills at all (82.0%), and cost 147k agent tokens per success against 101k when the harness injects a skill only at the step it applies to (83.6%). Memory evolved from 16 failed tasks then raised success on 86 held-out tasks by 9 to 17 points and, shipped unchanged, raised two other frontier models by about 16–18 points with intervals excluding zero (a third, smaller model's interval included zero). The caveats are large. Two byte-identical runs on the 86 held-out Retail tasks differ by up to about ±7 points at 95%, the deployment model's 50-task Airline ablations all have intervals that include zero, and the cost of the evolution loop itself is not reported. On Terminal-Bench, a plain retry budget explained almost all the gain from rewriting memory after a failure (+26.4 points from retrying; +2.3 more from adaptation, p = 0.77). For the restock agent, track the order's state explicitly before you build a skill library, and load a skill when its step comes up, not on every call.

---

## What transfers: insights, not trajectories

Memory Transfer Learning asks the same question across domains ([arXiv:2604.14004](https://arxiv.org/abs/2604.14004) (Kim et al., 2026-04, preprint)). A gpt-5-mini coding agent in mini-swe-agent retrieved its top 3 memories from runs on *other* benchmarks, never the one being tested, across six (LiveCodeBench, Aider-Polyglot, SWE-Bench Verified, Terminal-Bench 2, ReplicationBench, MLGym; up to 100 tasks each). The four memory formats run from raw to distilled: the full trajectory, a workflow of commands (as in Agent Workflow Memory), a Reflexion-style summary, and a one-to-three-sentence insight (as in ReasoningBank). **Average Pass@3 rose with abstraction**: 0.523 with no memory, 0.534 with trajectories, 0.538 workflows, 0.546 summaries and 0.560 insights. Raw trajectories hurt on two benchmarks (Terminal-Bench 2, 0.270 vs 0.315; MLGym, 0.583 vs 0.667), because a command that worked in one environment was replayed where it broke. What carried over was mostly how to work, such as inspect, edit, verify, submit, writing your own tests and respecting the environment; transferred algorithms explained only 5.5% of the gains. Plain embedding retrieval beat LLM reranking and LLM rewriting of the memories (0.630 vs 0.598 and 0.608 on three benchmarks). An agent's own memories helped it more than memories written by another model (Pass@1 0.543 vs 0.528 and 0.518). The gains are a few points on 100-task subsets with one model as agent, writer and judge, and no confidence intervals.

This seems to contradict the verbatim-store results in [03](03-memory-as-an-operating-system.md#designing-a-memory-agent), but the two are about different reuse. Keeping the raw record wins when the next task is about the *same* conversation or environment, where the exact detail is the answer. Distilling wins when the next task is *different*, where the details are noise and only the habit transfers. Keep the raw record as the source of truth either way, and distill an insight layer on top for the cross-task case. The split is not clean, though. AtomMem ([arXiv:2606.19847](https://arxiv.org/abs/2606.19847) (Yao et al., 2026-06, preprint)) rewrites each conversation turn into self-contained atomic facts, with pronouns resolved and dates made absolute. On LoCoMo with GPT-4o-mini, these facts alone beat retrieval over the raw dialogue on the *same* conversation (multi-hop F1 37.0 vs 21.0) with fewer tokens. The full system, which adds events, profiles and a graph, beat Mem0 and LightMem in every question category. The raw baseline is not described beyond "raw dialogue history", and the extractor and settings were tuned on LoCoMo-style data. Grading was by a single judge told to "be generous", with no seeds. Its retrieval sweep makes a point that holds either way: accuracy peaked at 10–20 retrieved facts and fell beyond that, even as recall kept rising. What AtomMem distils is fact-preserving: every fact is kept, only reworded. That is not the condensing that hurt in Zhou et al. Rewriting is safe; dropping is not. Zero-Mem takes the opposite route on the same benchmark ([arXiv:2607.29377](https://arxiv.org/abs/2607.29377) (Xiao et al., 2026-07, preprint)). It keeps raw traces and builds an entity graph and a time hierarchy over them with no LLM calls at all. On LoCoMo it averaged 59.15 F1 with GPT-4o-mini, against 53.75 for the best LLM-written memory (GAM). **Several LLM-distilled systems scored below plain chunk retrieval** (A-Mem 39.65, LightMem 38.44, against RAG 44.73). Memory operations used zero LLM tokens, where GAM used 28.6M. These are single numbers on two QA benchmarks, and latency was compared across different hardware. Read the two papers together: structure built over raw text can beat both raw retrieval and lossy distillation.

---

## Whose experience, and how much compute it saves

Two more results set the limits of distilled experience. ArcMemo stores abstract, reusable concepts from solved puzzles rather than whole solutions ([arXiv:2509.04439](https://arxiv.org/abs/2509.04439) (Ho et al., 2025-09, preprint)). On a 100-puzzle subset of ARC-AGI-1 with o4-mini, a frozen concept memory seeded from 160 human-written solutions raised the official score from 55.17 to 59.33. It was the only memory design the authors tried that beat no memory at every compute setting. **The gain shrank as compute grew.** With two retries, no memory scored 69.00 against 70.83, and a rewritten-cheatsheet baseline beat both (71.33). The authors' explanation is that with more attempts "the model can rediscover ideas through exploration". Matching was by attempts, not tokens, the runs used memory-augmented outputs that were longer, and the baseline's standard deviation (3.18) is close to the gap. Memory, like a team in [4b](04b-when-more-agents-pay.md), has to beat spending the same tokens on more tries.

MemCollab tests whose memories to use ([arXiv:2603.23234](https://arxiv.org/abs/2603.23234) (Chang et al., 2026-03, preprint)). Memory distilled from a Qwen2.5-32B agent's trajectories *hurt* a Qwen2.5-7B agent: HumanEval fell from 42.7 to 34.1 against no memory. That matches Kim et al.'s finding above that an agent's own memories help it more. Their fix pairs a right and a wrong trajectory from *different* models on the same task, and stores only the contrast as a rule ("when …, enforce …; avoid …"), tagged with the models involved. For the 7B agent, that raised the four-benchmark average to 71.6, against 59.8 with its own memories and 57.1 with none. Contrasting two samples from the same model reached 67.5. Building the memory needs several models run on 1,000 training items and a correctness check, and the tests use held-out items from the same math and code benchmarks. Most tables are single runs, and the 7B HumanEval baseline has a standard deviation of 5.3 points across seeds. For the restock agent, a lesson borrowed from a stronger model is a guess until it has been checked against your own model's mistakes.

---

## Who reads the memory, and how much of it

Where memory enters the agent matters as much as what it holds. MIA trains a deep-research agent with a separate planner ([arXiv:2604.04503](https://arxiv.org/abs/2604.04503) (Qiao et al., 2026-04, preprint)). With a Qwen2.5-VL-7B executor on 11 search benchmarks, the memory baselines that inject retrieved past context straight into the prompt (RAG, Mem0, A-Mem) mostly scored *below* no memory, while ReasoningBank's distilled strategies scored above it. The paper's ablation makes the same point within one system. **Handing memory to the executor lowered multimodal accuracy by 0.4 points; handing the same memory to a planner that writes the plan raised it by 3.5.** Updating the planner's weights online on the test stream added about 3 more points. The planner helped strong closed executors less (Claude Sonnet 4.6, +1.7 to +1.8) than weaker ones (GPT-5.4, +6.4 to +8.9). MIA spends far more than its baselines: a 32B manager and judge, 4 rollouts per question, and training. It reports no token, storage or latency numbers, the runs are single, and an LLM judges accuracy.

OCR-Memory keeps the record verbatim and makes it cheaper to search ([arXiv:2604.26622](https://arxiv.org/abs/2604.26622) (Li et al., 2026-04, preprint)). Past trajectory steps are rendered as images, and a fine-tuned 3B vision model picks the relevant segments by index. The agent then receives the stored text of those segments, unchanged, so nothing the model paraphrased can creep in. With a GPT-4 agent on Mind2Web, this cut the text injected per step from 3,980 tokens to 596, and raised element accuracy to 53.8% against 41.3% for text retrieval and 49.1% for Agent Workflow Memory. The cost moved elsewhere: disk per episode grew from 18 KB to 1.47 MB, and retrieval latency from 0.3 s to 1.7 s. The retriever was trained and the text baseline was not, so "optical" and "trained retriever" are confounded. Task success was 2–5% for every method, and the runs are single. Both papers point the same way for the restock agent. Retrieve a few exact records, and give them to whatever writes the plan, not to the step that executes it.

---

## Distill from governed memory, not straight from trajectories

Tang et al. build skills in stages rather than in one step from raw runs ([arXiv:2607.16621](https://arxiv.org/abs/2607.16621) (Tang et al., 2026-07, preprint)). Their MSCE stores step traces, then procedural policies, then facts about the environment. A policy becomes a callable skill only when evidence from at least two episodes supports it and it shows a positive estimated gain. Skills then stay on probation until their pass rate exceeds 0.6, and are archived below 0.2. Their reason is the same failure Memory Transfer Learning found: skills distilled directly "may thus overfit to raw trajectories and be invoked in inappropriate contexts". On EvoAgentBench with a GPT-5.2 agent, **replacing the layered store with one flat retrieved memory cost 15–19 Pass@1 points** across three domains. Removing the skill step cost 6–12. Removing the applicability filter lowered accuracy and raised cost in every domain. Several baselines that reuse memory or skills naively scored *below* the plain agent on some domains (for example 26.92 against 38.46 on software engineering), so a store can hurt. Memory evolved in one domain gave 2.6–5.1 points when reused in another. These are single runs on small per-domain sets, and the authors call their value scores "heuristic governance signals rather than causal credit-assignment estimates". The flat-memory ablation removes several parts at once. The authors also build the MemOS stack the system ships in. For the restock agent, promote a lesson to a skill only after it has worked twice, and retire it when it stops working.

---

## Maintain the store: overwrite, don't append

A store that only grows becomes the problem. Wu et al. gave a Qwen2.5-32B game agent a file-system memory and let a frontier model (Claude Opus 4.6) rewrite the memory scaffold between runs ([arXiv:2607.01224](https://arxiv.org/abs/2607.01224) (Wu et al., 2026-07, preprint)). The first version barely beat a 16-observation sliding window (Crafter progression 25.0% vs 19.6%, with overlapping standard errors), and it bloated. Each step appended another copy of the map. The rewritten scaffold keys map entries by coordinate and overwrites them, and keeps inventory and status in files that sync automatically. **On NetHack that cut memory growth from 138 to 6 characters per step**, and across three games it cut redundant writes by 68–83%. Progression roughly doubled to quadrupled over the first version (Crafter 25.0 → 47.3, MiniHack 7.5 → 27.5, NetHack 0.42 → 1.57), and a small adapter trained to use the memory added a few points more, within one standard error on two of the games. The gains are hard to attribute, though. The authors' appendix shows that much of the rewritten scaffold is game logic the meta-model wrote in, such as crafting preconditions and action blocking. The eval seeds also decided which rewrites were kept. The runs are games only, with 5–10 episodes. This does not overturn "keep the raw record" from [03](03-memory-as-an-operating-system.md#designing-a-memory-agent). An append log is a fine *archive*. But the working files an agent reads every step should hold the current state, updated in place. For the restock agent, keep one row per SKU that you overwrite, and keep the order history as the append-only log beside it.

Bousetouane makes the same split for a single long conversation ([arXiv:2601.11653](https://arxiv.org/abs/2601.11653) (Bousetouane, 2026-01, preprint)). Instead of replaying the transcript, the agent keeps one bounded state with nine typed fields (goal, constraints, focal entities, open uncertainty and so on), which it rewrites every turn. Retrieved records count as evidence and can change that state only through a schema-checked write. Past turns still go to an artifact store. In 600 live 50-turn episodes across IT operations, cybersecurity and healthcare, replayed context grew roughly linearly while the bounded state stayed flat, and an LLM judge found that **hallucination and drift rose with turn count for replay and top-k RAG but stayed near zero for the bounded state**. Take that as a direction, not a size. The results are reported only as plots, with no numbers in the text, no seeds or intervals, and no ablation. The models are not named, and the extra compressor call each turn is not costed.

A running summary that gets updated in place has its own failure mode. Srinivasan compared one with keeping the raw event log and building a memory view from it only at decision time ([arXiv:2604.20158](https://arxiv.org/abs/2604.20158) (Srinivasan, 2026-04, preprint)). The test used ten loan and insurance-claim decisions of 82–96 events each, with Claude Haiku 4.5 as both agent and judge. **When memory had to fit in a twentieth of the trajectory, the projection from the raw log beat the running summary by about 0.5 on fact recall and on reasoning consistency (0.91 vs 0.39 recall, p = 0.001).** The paper's explanation is that a summary that must discard something at every step loses anchors, and the losses compound over the run. At a fifth or half of the trajectory size, the two were indistinguishable. The raw log also leaves less to audit: replaying a decision means capturing 2 model calls rather than 83–97. Even so, temperature 0 on the live API did not give byte-identical replays for either design. This is ten cases, one model family with a same-family judge, a single author and no full-context arm, and the summary arm's dollar costs are estimated. It agrees with [03](03-memory-as-an-operating-system.md#designing-a-memory-agent): keep the raw record, and condense it late, once, for the decision at hand.

---

## The other end: memory in the weights

Everything above stores text and reads it back. MEMO trains it into a model instead ([arXiv:2605.15156](https://arxiv.org/abs/2605.15156) (Quek et al., 2026-05, preprint)). The paper is about a document corpus, not an agent's own experience, but it marks the far end of the distillation scale. A Qwen2.5-14B "memory model" is fine-tuned on question–answer pairs synthesized from the corpus, and a frozen executive model queries it over several turns. On NarrativeQA it reached 26.85% with a Qwen2.5-32B executive, against 21.39% for HippoRAG2 retrieval. On BrowseComp-Plus it lost to HippoRAG2 with the same executive (54.22 vs 56.11). It held steady when distractor documents were added, while retrieval lost about 6 points. Three things make it a poor default. **It cost roughly 330–420 GPU-hours per corpus** to generate the data and train. Adding a second corpus by model merging rather than retraining cut accuracy from 26.85 to 15.81. And the executive's token use was not reported against the single-shot retrieval baselines. The synthesized cross-document pairs carried the result: without them, NarrativeQA accuracy fell from 24.00 to 6.37 in a smaller-model ablation. For an agent whose experience changes every day, text you can edit and delete beats weights you have to retrain.


---

## Building an experience store

The pieces above fit one design. Keep the raw log, maintain a small current-state file, and promote lessons to skills only on evidence.

Run the promotion step off the request path. MAPLE splits a personalization agent into memory, learning and personalization sub-agents, where only retrieval sits in the request path and extraction runs in the background ([arXiv:2602.13258](https://arxiv.org/abs/2602.13258) (Piskala, 2026-02, preprint, AAMAS 2026 ALA workshop submission)). It keeps both the raw episodes and the conclusions drawn from them. Its only test is weak: with 150 synthetic personas, an LLM-judged personalization score rose from 4.17 to 4.78 over a baseline that saw no history at all. There was no full-history baseline and no cost count, so the split is a design argument, not a measured win.

```text
   task run ──► append-only log (raw record, never edited)
                    │
                    ├──► state file: one row per key, overwritten   (read every step)
                    │
                    └──► candidate lesson ──seen in ≥2 episodes──► probation
                                                                     │
                                         used and checked ◄──────────┘
                                         │            │
                                pass rate > 0.6   pass rate < 0.2
                                         │            │
                                      active       archived
                                         │
                       retrieve a few ──► planner (not the executor)
```

The store below implements the promotion rule, with thresholds borrowed from MSCE (two episodes, activate above 0.6, archive below 0.2, Laplace-smoothed pass rate). It is a sketch of the rule, not the paper's system.

```python
from dataclasses import dataclass, field

@dataclass
class Lesson:
    text: str
    episodes: set = field(default_factory=set)   # distinct episodes that support it
    passes: int = 0
    trials: int = 0
    status: str = "candidate"                     # candidate -> probation -> active -> archived

    def reliability(self):
        return (self.passes + 1) / (self.trials + 2)  # Laplace-smoothed pass rate

class SkillStore:
    """Promote a lesson only after it is seen in 2+ episodes; retire it when it stops working."""
    def __init__(self, min_episodes=2, activate=0.6, retire=0.2):
        self.lessons, self.min_episodes = {}, min_episodes
        self.activate, self.retire = activate, retire

    def observe(self, key, text, episode):
        lesson = self.lessons.setdefault(key, Lesson(text))
        lesson.episodes.add(episode)
        if lesson.status == "candidate" and len(lesson.episodes) >= self.min_episodes:
            lesson.status = "probation"

    def record_use(self, key, passed):
        lesson = self.lessons[key]
        lesson.trials += 1
        lesson.passes += passed
        r = lesson.reliability()
        if lesson.status in ("probation", "active"):
            lesson.status = "active" if r > self.activate else lesson.status
            lesson.status = "archived" if r < self.retire else lesson.status

    def injectable(self):
        return [l.text for l in self.lessons.values() if l.status in ("probation", "active")]

store = SkillStore()
store.observe("lead-time", "Check supplier lead time before reordering", episode=1)
print(store.injectable())                      # [] - seen once, not yet a skill
store.observe("lead-time", "Check supplier lead time before reordering", episode=2)
store.observe("round-up", "Round every order up to a full pallet", episode=2)
store.observe("round-up", "Round every order up to a full pallet", episode=3)
for passed in (1, 1, 1):
    store.record_use("lead-time", passed)
for passed in (0, 0, 0, 0, 0):
    store.record_use("round-up", passed)
for k, l in store.lessons.items():
    print(k, l.status, round(l.reliability(), 2))
print(store.injectable())
```

```text
[]
lead-time active 0.8
round-up archived 0.14
['Check supplier lead time before reordering']
```

The lead-time lesson is not injected after one sighting, and becomes active once it has been seen twice and has passed three checks. The pallet rule is archived after five failures and stops reaching the prompt.

---

## Pitfalls

- **No baseline without the store.** Several memory systems scored below no memory (MIA, MSCE baselines). Always run the agent without the store and with the history in context.
- **Skills for open-ended work.** Skill files helped on exact-match and programmatic tasks and lost on rubric-graded ones (ContinualSkillBench).
- **Replaying raw commands in a new environment.** Trajectories carried across benchmarks hurt where commands no longer applied. Transfer insights, not trajectories (Memory Transfer Learning).
- **Borrowing a stronger model's memory.** A 32B agent's memories made a 7B agent worse than no memory (MemCollab).
- **Append-only working memory.** A state file that only grows bloats the prompt with duplicates. Overwrite current state and keep the log separately (AutoMem).
- **Retrieving more and more.** Accuracy peaked at 10–20 retrieved facts and fell beyond that while recall rose (AtomMem).
- **Counting attempts, not tokens.** Memory gains shrank as retries grew (ArcMemo). Compare against the same tokens spent on more tries.

---

## Try it

1. In the `SkillStore` example, lower `min_episodes` to 1 and feed it a lesson that fails twice and then passes. What does it inject, and when?
2. Your restock agent's skill library has 300 entries after a month, and accuracy is flat. Name two measurements that tell you whether to prune it.
3. You want to reuse memories written by GPT-class model A in a smaller model B. What would you test first?

<details>
<summary>Answers</summary>

1. It goes to probation on the first sighting, so it is injected at once. After two failures the pass rate is 1/4 = 0.25, still above the 0.2 retire line, so it stays in. After the pass it is 2/5 = 0.4, so it stays on probation and is never activated. Requiring two episodes would have kept a one-off lesson out of the prompt until it had more support.
2. Accuracy with the library against accuracy with the same task history in context but no skills (the ContinualSkillBench comparison). And how often each skill is retrieved and whether its uses pass, so that you can archive the ones that never help. ContinualSkillBench found that the smaller library written by the better model was used more.
3. B with A's memories against B with no memory and B with its own memories, on the same tasks. MemCollab and Memory Transfer Learning both found another model's memories can help less than the model's own, or hurt.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Do skill libraries beat keeping the history in context? | Not on average. In ContinualSkillBench, in-context history and feedback scored 0.585 against 0.582 with skills. Skills won on exact-match tasks and lost on open-ended ones. |
| What transfers across tasks: trajectories or insights? | Insights. Pass@3 rose from 0.523 with no memory to 0.534 with raw trajectories and 0.560 with one-line insights, and trajectories hurt where commands no longer applied (Memory Transfer Learning). |
| When should raw records be kept? | Always, as the source of truth. Answer same-conversation questions from them, and distil a fact-preserving or insight layer on top for reuse. |
| Why gate skill promotion on evidence? | Skills distilled from a single run overfit and are invoked in the wrong context. MSCE requires two episodes and a positive gain, and retires skills whose pass rate drops. |
| Should memory go to the planner or the executor? | The planner. In MIA, memory given to the executor cost 0.4 points, and the same memory given to a planner added 3.5. |
| How do you know a memory system is worth its cost? | Compare it against no memory, history in context, and the same tokens spent on retries. ArcMemo's gain shrank as retries grew, and several published memory systems scored below no memory. |

---

## Next

→ [04 — multi-agent design patterns](04-multi-agent-design-patterns.md): reflection, tool use, planning and collaboration built from conversations between agents.
