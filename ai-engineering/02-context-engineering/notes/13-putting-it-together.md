---
origin: synthesis
sources:
  - https://github.com/davidkimai/Context-Engineering (00_foundations/01–07, 00_COURSE/10_orchestration_capstone, 40_reference/patterns.md, cognitive-tools/cognitive-architectures/{solver,tutor,research,reconstruction-memory}-architecture.md, 00_foundations/06_advanced_applications.md — snapshot 2026-08-14)
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
confidence: medium
cleaned: 2026-10-28
---
# 13 — Putting It Together

> The previous chapters each cover one lever. This one covers how they combine: a maturity ladder for context systems, the recurring design patterns, and four reference architectures.

---

## The maturity ladder

The upstream course is built on a biological metaphor. Read as a maturity ladder, it's a useful way to tell how much machinery a problem actually needs:

| Level | Upstream name | What's in the window | Chapter |
|---|---|---|---|
| 1 | **Atom** | One instruction: task + constraints + output format | [02](02-context-anatomy.md) |
| 2 | **Molecule** | Instruction + examples (few-shot) | [02](02-context-anatomy.md), [03](03-budgeting-the-window.md) |
| 3 | **Cell** | + memory: state carried across turns | [05](05-compression-compaction.md), [06](06-memory.md) |
| 4 | **Organ** | Several specialised contexts coordinated by an orchestrator | [10](10-tools-and-multi-agent.md) |
| 5 | **Cognitive system** | + reasoning tools, schemas, verification loops | [07](07-structured-context.md), [08](08-cognitive-tools.md) |

**Climb only when the level below fails measurably.** Most production failures at level 4 are level-2 problems: the examples or instructions were never right. Each rung multiplies cost and failure modes ([11](11-failure-modes.md)).

---

## Recurring design patterns

Across the upstream applications and the reference `patterns.md`, the same seven patterns recur:

| Pattern | What it does | Lever |
|---|---|---|
| **Structured state** | A small, overwritten state block (goal, decisions, next step) instead of raw history | Write / Compress |
| **Progressive context** | Start minimal; add context only when a step needs it (identifiers first, contents on demand) | Select |
| **Verification loop** | Generate → check → revise, bounded, with a machine-readable verdict | (reasoning) |
| **Structured schemas** | Fixed input, state and output shapes | (all) |
| **Template programs** | Parameterised, reusable prompt procedures | (all) |
| **Personalisation** | A user model kept outside the window, selectively injected | Write / Select |
| **Phased processing** | Split a long task into phases with a compaction point between them | Compress / Isolate |

---

## Four reference architectures

### 1. Long-form document generation

```
outline (schema) → for each section: retrieve → draft → verify against outline → store summary
                                     ↑                                       │
                                     └──── running summary of prior sections ┘
```

- The **outline** is the persistent state. Each section is written with the outline, a summary of prior sections and its own evidence. It never sees the full prior text.
- Levers: structured state + phased processing. The window stays constant-size however long the document gets.

### 2. Problem solver with memory

```
understand_question → recall_related (memory of solved problems) → solve
      → examine_answer ─┬─ ok → store (problem, method, outcome) → done
                        └─ error → backtrack → solve
```

- This is the IBM cognitive-tool loop ([08](08-cognitive-tools.md)) with a memory write at the end, so solved problems become future `recall_related` hits.
- Levers: cognitive tools in isolated calls + a write-to-memory step.

### 3. Research assistant

```
plan (questions, scope) → orchestrator
     ├─ sub-agent per question: search → read → extract findings (own context)
     └─ collect condensed findings → synthesise → cite → verify claims against sources
```

- Each sub-agent burns tokens exploring and returns only a condensed result. The orchestrator holds the plan and the synthesis ([10](10-tools-and-multi-agent.md)).
- Levers: isolate + compress at the hand-off. This is the shape of Anthropic's multi-agent research system.

### 4. Adaptive tutor

```
learner model (stored) → select next concept → explain at learner's level → check understanding
      ↑                                                                          │
      └──────────────── update mastery estimates, misconceptions ────────────────┘
```

- The learner model (mastery per concept, known misconceptions, preferences) is a structured memory ([06](06-memory.md), [07](07-structured-context.md)), injected as a short summary each turn.
- Levers: write + select. The model never sees the full interaction history, only the current estimate of the learner.

### A note on "reconstructive memory"

The upstream architecture of the same name stores **fragments** (facts, episodes, procedures) and reassembles a context-specific memory at retrieval time, rather than replaying stored transcripts. Stripped of the field-theory framing, that's retrieval over atomised memories plus model-written synthesis. It's a sound pattern, with a real risk: the synthesis step can confabulate connections between fragments. Keep source pointers on every fragment so a reconstructed memory can be checked.

---

## Designing a context system: the order of questions

1. **What does success look like, and how will you measure it?** Build the eval set first ([12](12-evaluating-context.md)).
2. **What's the smallest window that could work?** Start at level 1 or 2 of the ladder.
3. **What does the model lack?** Facts → retrieval ([04](04-retrieval.md)). Continuity → memory ([06](06-memory.md)). Method → cognitive tools ([08](08-cognitive-tools.md)).
4. **What grows?** Give every growing component a ceiling and a compaction rule ([03](03-budgeting-the-window.md), [05](05-compression-compaction.md)).
5. **What can live outside the window?** Write before you select. Select before you compress. Isolate last.
6. **What can go wrong?** Walk the failure modes ([11](11-failure-modes.md)) against your design before shipping.

---

## Capstone exercise

Take an agent you've built, or the research-assistant shape above, and produce:

- [ ] A per-component token budget with ceilings, measured on real traffic
- [ ] An ablation table: each component's Δ quality and Δ tokens
- [ ] A compaction rule, with a fact-retention score
- [ ] One failure mode from [11](11-failure-modes.md) reproduced, fixed and added to the eval set
- [ ] A one-page design doc stating which lever each component serves

When the loop that assembles this context becomes stateful and conditional, you've crossed into the harness layer → [03-harness](../../03-harness-engineering/README.md).
