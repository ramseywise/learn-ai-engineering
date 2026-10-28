---
origin: curated
sources:
  - https://github.com/walkinglabs/learn-harness-engineering (MIT; English docs, lectures 01–13, projects 01–07, harness-creator skill)
confidence: high
cleaned: 2026-10-28
---
# Harness Engineering — Primary Sources and Upstream Course

> The primary sources behind the [practice track](notes/practice/) and the 2026-10-28 additions to [notes/](notes/), plus what was kept from the *learn-harness-engineering* course and what was dropped. The full source list for notes 01–08 is in the [README](README.md#external-sources).

---

## Primary sources

| Source | Why read it | Maps to |
|---|---|---|
| ★ OpenAI, [*Harness engineering: leveraging Codex in an agent-first world*](https://openai.com/index/harness-engineering/) | The repo as system of record, `AGENTS.md` as a map rather than a manual, layered architecture enforced by checks, golden rules and background cleanup agents | [P1](notes/practice/01-repo-as-system-of-record.md) · [P2](notes/practice/02-session-lifecycle.md#entropy-management-two-cleanup-modes) · [05](notes/05-verification-loops.md#agent-oriented-error-messages) · [templates/openai-repo-template/](templates/openai-repo-template/) |
| ★ Anthropic, [*Effective harnesses for long-running agents*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer agent, feature list as JSON, one feature per session, progress file + git as continuity, end-to-end testing before marking done | [P2](notes/practice/02-session-lifecycle.md) · [P3](notes/practice/03-scope-and-done.md) |
| Anthropic, [*Harness design for long-running apps*](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Planner/generator/evaluator, sprint contracts, evaluator calibration, cost breakdown of a full build | [05](notes/05-verification-loops.md) · [08](notes/08-maturity-and-failure-modes.md#iterative-simplification) |
| Liu et al., [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172) (2023) | Recall drops for information in the middle of long inputs, which is why the entry file stays short and puts critical rules at the edges | [P1](notes/practice/01-repo-as-system-of-record.md) |
| HumanLayer, [*Skill issue: harness engineering for coding agents*](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) | Failures are configuration, not model limits | [01](notes/01-what-a-harness-is.md#the-skill-issue-reframe) |

## About the upstream course

[walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) (MIT) is a 13-lecture, 7-project course built around an Electron knowledge-base app. Its English material was folded into this module on 2026-10-28 and the vendored snapshot was deleted.

| Upstream | Became |
|---|---|
| L01–L02 (why agents fail, what a harness is) | [01](notes/01-what-a-harness-is.md#five-ways-a-capable-model-fails-without-a-harness) failure table and diagnostic loop · [02](notes/02-harness-anatomy.md#the-five-subsystems) five subsystems |
| L03–L04 (repo as system of record, split instructions) | [P1](notes/practice/01-repo-as-system-of-record.md) |
| L05–L06, L12 (continuity, initialization, clean state) | [P2](notes/practice/02-session-lifecycle.md) |
| L07–L08 (scope, feature lists) | [P3](notes/practice/03-scope-and-done.md) |
| L09–L10 (premature done, end-to-end testing) | [05](notes/05-verification-loops.md#the-three-layer-termination-check) |
| L11 (observability) | [08](notes/08-maturity-and-failure-modes.md#runtime-vs-process-observability) |
| Projects 01–06 | [P4 labs](notes/practice/04-exercises.md), rewritten to work on any repo |
| Resource templates + harness-creator skill templates | [templates/](templates/), merged into one set |
| OpenAI advanced repo template | [templates/openai-repo-template/](templates/openai-repo-template/) |
| harness-creator skill (gotchas, pattern references) | [08](notes/08-maturity-and-failure-modes.md#builder-gotchas) · [07](notes/07-orchestration.md#handoff-design) |

## Deliberately not kept

- **The Electron app projects and TypeScript demos.** The starter and solution code taught the app more than the harness. The labs now run on your own repo.
- **Translations** (zh, ja, ko, es, fr, vi, pt, de) and the VitePress website tooling.
- **The rest of the harness-creator skill.** The gotchas and patterns were folded into the notes. The skill's own instructions duplicated the course.
- **L13 and project 07 (loop engineering).** These became [04-loop-engineering/notes/](../04-loop-engineering/notes/) and the [loop labs](../04-loop-engineering/practice/01-exercises.md).
- **Unsourced statistics and "a team found…" anecdotes.** Only numbers traceable to a cited source were kept.
- **The duplicate `CLAUDE.md` template.** [templates/AGENTS.md](templates/AGENTS.md) notes that `CLAUDE.md` can be a pointer or symlink to it.

To read the originals, use the upstream repo.
