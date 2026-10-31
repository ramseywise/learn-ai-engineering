---
origin: curated
sources:
  - https://github.com/walkinglabs/learn-harness-engineering (MIT; English docs, lectures 01–13, projects 01–07, harness-creator skill)
confidence: high
cleaned: 2026-10-31
---
# Harness Engineering — Primary Sources and Upstream Course

> The primary sources behind notes [09](notes/09-repo-as-system-of-record.md)–[10](notes/10-scope-and-done.md) and the 2026-10 additions to [notes/](notes/), plus what was kept from the *learn-harness-engineering* course and what was dropped. The full source list for notes 01–08 is in the [README](README.md#external-sources).

---

## Books

| | Source | Notes |
|---|---|---|
| ★ | Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDFs in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Folded in as: ch. 3 → [05](notes/05-verification-loops.md); ch. 4 → [03](notes/03-tool-design.md), [05](notes/05-verification-loops.md); ch. 5 → [03](notes/03-tool-design.md), [07](notes/07-orchestration.md); ch. 12 → [04](notes/04-execution-boundaries.md), [08](notes/08-maturity-and-failure-modes.md). Ch. 11 and 13 are in [loop engineering](../04-loop-engineering/references.md#books). Ch. 4's MCP transport and security claims are dated. Notes cite it as `(*Building Applications with AI Agents*, ch. N)` | 03, 04, 05, 07, 08 |
| ★ | Denis Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025). Chapter PDFs in [sources/context-engineering-multi-agent-systems/](sources/context-engineering-multi-agent-systems/). Folded in as: ch. 4 → [07](notes/07-orchestration.md); ch. 5 → [05](notes/05-verification-loops.md), [07](notes/07-orchestration.md), [08](notes/08-maturity-and-failure-modes.md); ch. 8 → [04](notes/04-execution-boundaries.md), [07](notes/07-orchestration.md). The book's "MCP" is its own message envelope, not the Model Context Protocol. Notes cite it as `(*Context Engineering for Multi-Agent Systems*, ch. N)` | 04, 05, 07, 08 |
| | Mayo Oshin and Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/learning-langchain/](../../generative-ai/01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 8 → [07](notes/07-orchestration.md#double-texting-the-same-problem-in-a-chat-app). Ch. 8's human-control material is in [loop engineering](../04-loop-engineering/references.md#books). Notes cite it as `(*Learning LangChain*, ch. N)` | 07 |

## Primary sources

| Source | Why read it | Maps to |
|---|---|---|
| ★ OpenAI, [*Harness engineering: leveraging Codex in an agent-first world*](https://openai.com/index/harness-engineering/) | The repo as system of record, `AGENTS.md` as a map rather than a manual, layered architecture enforced by checks, golden rules and background cleanup agents | [09](notes/09-repo-as-system-of-record.md) · [06](notes/06-long-horizon-execution.md#entropy-management-two-cleanup-modes) · [05](notes/05-verification-loops.md#agent-oriented-error-messages) |
| ★ Anthropic, [*Effective harnesses for long-running agents*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer agent, feature list as JSON, one feature per session, progress file + git as continuity, end-to-end testing before marking done | [06](notes/06-long-horizon-execution.md#the-session-lifecycle) · [10](notes/10-scope-and-done.md) |
| Anthropic, [*Harness design for long-running apps*](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Planner/generator/evaluator, sprint contracts, evaluator calibration, cost breakdown of a full build | [05](notes/05-verification-loops.md) · [08](notes/08-maturity-and-failure-modes.md#iterative-simplification) |
| Liu et al., [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172) (2023) | Recall drops for information in the middle of long inputs, which is why the entry file stays short and puts critical rules at the edges | [09](notes/09-repo-as-system-of-record.md#the-entry-file-is-a-router) |
| HumanLayer, [*Skill issue: harness engineering for coding agents*](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) | Failures are configuration, not model limits | [01](notes/01-what-a-harness-is.md#the-skill-issue-reframe) |
| Bojie Li, *AI Agents in Depth*, [ch. 1](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter1.md), [ch. 4 Tools](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter4.md), [ch. 5 Coding Agent](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter5.md) | Harness as "reins on the horse"; tool design principles; proposer–reviewer; moving policy from prompt to code. Labs: MCP tool servers (4-1–4-3), codified rules for small models (5-3), a pure-Python coding agent (5-12). Synthesised into the notes at right; each links its labs upstream. | [01](notes/01-what-a-harness-is.md) · [03](notes/03-tool-design.md) · [05](notes/05-verification-loops.md) · [07](notes/07-orchestration.md) |
| ★ Faldor, Singh, Raileanu, *A team of Gemini 4 Argon agents beats Minecraft*, arXiv 2610.22319 (2026) · [PDF](sources/faldor-2026-team-gemini-4-argon-agents.pdf) | Four agents, 27 h 14 min, no human help: one harness read through the five subsystems, sandboxed programs, honest reporting and an Observer, emergent coordination, full cost and run statistics | [02](notes/02-harness-anatomy.md#one-harness-read-through-the-five-subsystems) · [04](notes/04-execution-boundaries.md#shell-vs-interpreter) · [05](notes/05-verification-loops.md#an-observer-that-checks-claims-against-the-record) · [06](notes/06-long-horizon-execution.md#what-a-27-hour-run-looks-like) · [07](notes/07-orchestration.md#coordination-without-a-coordinator-four-agents-in-minecraft) |
| Li G. et al., *Object-Oriented Harness*, arXiv 2610.28380 (2026, Google Cloud) · [PDF](sources/li-2026-object-oriented-harness.pdf) | A hierarchy of specialized harnesses plus a router, up to +15.79 points; added components can hurt other task classes; injected nudges | [05](notes/05-verification-loops.md#nudges-the-harness-injects) · [08](notes/08-maturity-and-failure-modes.md#an-early-step-a-family-of-harnesses-and-a-router) |
| Agashe et al., *Evolving Agent Interfaces* (Agent S4), arXiv 2610.28601 (2026) · [PDF](sources/agashe-2026-evolving-agent-interfaces.pdf) | Harness-only changes take a 27B open model from 5.6% to 21.3%, ahead of frontier models at a fraction of the cost | [01](notes/01-what-a-harness-is.md) |
| Kulkarni, [*Building reliable agentic AI systems*](https://martinfowler.com/articles/reliable-llm-bayer.html) (martinfowler.com, 2026), Bayer PRINCE | Three kinds of reflection, two-level retry, resume from failure, provider fallback; the retrieval stack moved to [genai/02 agent-rag-patterns](../../generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince.md) | [05](notes/05-verification-loops.md#three-kinds-of-reflection) · [08](notes/08-maturity-and-failure-modes.md#production-reliability-primitives) |
| LangChain, [Deep Agents docs](https://docs.langchain.com/oss/python/deepagents/overview) | Capability groups, pluggable filesystem backends, permissions, tool allowlists and harness profiles, `execute` vs. `eval` | [02](notes/02-harness-anatomy.md) · [04](notes/04-execution-boundaries.md) · [06](notes/06-long-horizon-execution.md#shallow-vs-deep-agents) |
| Karpathy, AISN 2026 talk (secondary: YouTube breakdown, no primary transcript) | Spec / verifier / environment layers; rules vs. requests; robot librarian | [01](notes/01-what-a-harness-is.md) · [04](notes/04-execution-boundaries.md#prompts-vs-hooks) · [05](notes/05-verification-loops.md#asymmetric-qa) · [09](notes/09-repo-as-system-of-record.md#karpathys-environment-layer) · [10](notes/10-scope-and-done.md#before-the-list-the-spec) |

## AI Papers of the Week

| Source | Why read it | Maps to |
|---|---|---|
| ★ Mak et al., *Is Bash All You Need? An Empirical Study of Tool Interfaces for Enterprise Digital Worker Agents*, arXiv [2609.11999](https://arxiv.org/abs/2609.11999) (2026, Microsoft) · [PDF](sources/mak-2026-bash-all-you-need.pdf) | Five tool interfaces on TheAgentCompany and APEX-Agents with Opus-4.8 and GPT-5.5: bash alone beats typed tools by up to 24.5 pp with 19–72% fewer tokens, typed tools on top of bash add nothing, PTC when a fixed catalog is required; shell agents declare done without verifying and read evaluator scripts | [03](notes/03-tool-design.md#capability-form-and-granularity) · [05](notes/05-verification-loops.md#the-core-failure) |
| Bansal et al., *Challenges in Human-Agent Communication* (2024, Microsoft Research) · [PDF](sources/challenges-human-agent-communication-2024.pdf) | Twelve communication challenges set on a before/during/after timeline: what the agent can do, is about to do, is doing, changed, and achieved; what the user wants, prefers and would correct. Over-notification buries the one alert that matters. Position paper, no user study | [04](notes/04-execution-boundaries.md#permission-gates-and-hitl) |
| Fang et al., *LLM Agents can Autonomously Hack Websites*, arXiv [2402.06664](https://arxiv.org/abs/2402.06664) (2024, UIUC) · [PDF](sources/fang-2024-llm-agents-can-autonomously-hack.pdf) | GPT-4 with a browser, terminal, Python and six hacking docs exploits 11 of 15 sandboxed vulnerabilities (73.3% pass@5, 42.7% pass@1) at about $9.81 per site, with no hint of which bug; GPT-3.5 6.7%, open models 0%. Author-built sites, prompt withheld | [04](notes/04-execution-boundaries.md#coding-agent-specifics) |
| Yang et al., *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*, arXiv [2405.15793](https://arxiv.org/abs/2405.15793) (NeurIPS 2024) · [PDF](sources/yang-2024-swe-agent.pdf) | Origin of the ACI term: GPT-4 Turbo 18.0% vs. 11.0% on SWE-bench Lite with a designed interface vs. a plain shell; ablations of search, file window, lint-on-edit and history | [03](notes/03-tool-design.md#aci-not-api) · [03](notes/03-tool-design.md#output-discipline) |

## About the upstream course

[walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) (MIT) is a 13-lecture, 7-project course built around an Electron knowledge-base app. Its English material was folded into this module on 2026-10-28 and the vendored snapshot was deleted.

| Upstream | Became |
|---|---|
| L01–L02 (why agents fail, what a harness is) | [01](notes/01-what-a-harness-is.md#five-ways-a-capable-model-fails-without-a-harness) failure table and diagnostic loop · [02](notes/02-harness-anatomy.md#the-five-subsystems) five subsystems |
| L03–L04 (repo as system of record, split instructions) | [09](notes/09-repo-as-system-of-record.md) |
| L05–L06, L12 (continuity, initialization, clean state) | [06](notes/06-long-horizon-execution.md#the-session-lifecycle) |
| L07–L08 (scope, feature lists) | [10](notes/10-scope-and-done.md) |
| L09–L10 (premature done, end-to-end testing) | [05](notes/05-verification-loops.md#the-three-layer-termination-check) |
| L11 (observability) | [08](notes/08-maturity-and-failure-modes.md#runtime-vs-process-observability) |
| Projects 01–06 | Dropped (the exercises built on them were removed 2026-10-31) |
| Resource templates + harness-creator skill templates | Trimmed excerpts inline in [06](notes/06-long-horizon-execution.md#the-session-lifecycle), [05](notes/05-verification-loops.md#grading-criteria-beat-vibes), [08](notes/08-maturity-and-failure-modes.md#the-quality-document), [10](notes/10-scope-and-done.md#the-triple). The full copy-ready set lived in `templates/` until 2026-10-31; it is in git history at commit `6ee939f` |
| OpenAI advanced repo template | Layout described in [09](notes/09-repo-as-system-of-record.md#encoding-knowledge-the-agent-cant-see); files in git history at `6ee939f` (`templates/openai-repo-template/`) |
| harness-creator skill (gotchas, pattern references) | [08](notes/08-maturity-and-failure-modes.md#builder-gotchas) · [07](notes/07-orchestration.md#handoff-design) |

## Deliberately not kept

- **The Electron app projects and TypeScript demos.** The starter and solution code taught the app more than the harness. The labs now run on your own repo.
- **Translations** (zh, ja, ko, es, fr, vi, pt, de) and the VitePress website tooling.
- **The rest of the harness-creator skill.** The gotchas and patterns were folded into the notes. The skill's own instructions duplicated the course.
- **L13 and project 07 (loop engineering).** These became [04-loop-engineering/notes/](../04-loop-engineering/notes/).
- **Unsourced statistics and "a team found…" anecdotes.** Only numbers traceable to a cited source were kept.
- **The duplicate `CLAUDE.md` template.** `CLAUDE.md` can be a pointer or symlink to `AGENTS.md`.

To read the originals, use the upstream repo.
