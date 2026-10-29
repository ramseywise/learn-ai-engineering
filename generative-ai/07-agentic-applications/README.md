# 07 — Agentic Applications

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position: seventh pillar — specific projects built with agentic frameworks.
> Presumes: [03-agentic-foundations](../03-agentic-foundations/README.md).

---

## What it is

Agentic applications are the payoff: end-to-end projects that apply the frameworks and
patterns from the earlier pillars to real tasks. This pillar is intentionally small —
it holds only genuinely built things, not course material.

---

## Resource map

### Projects

- **[`internet-search-agent-main/`](internet-search-agent-main/)** —
  a web-search agent built with LangGraph: tool calling for search, result parsing, and
  iterative query refinement. Has its own `README.md`, `pyproject.toml`, and test suite.

- **[`chatbot/deep-research-bot/`](chatbot/deep-research-bot/)** —
  a 2025 agent-building workshop clone with real post-clone activity: eval scripts
  (`eval_simple_agent.py`) and notebooks edited after the initial clone date. Has its own
  `CLAUDE.md` and `AGENTS.md`. The most actively maintained project in the repo.

- **[`chatbot/deep_research_bench/`](chatbot/deep_research_bench/)** —
  deep research benchmark dataset. Untouched reference data.

### Notes

- **[`real-time-multimodal-agents.md`](real-time-multimodal-agents.md)** —
  voice (cascaded / Omni / full-duplex, streaming perception, fast/slow thinking,
  control-token TTS), Computer Use (action space, visual grounding, efficiency) and
  robotics (planning + VLA, action chunking, Sim2Real). From *AI Agents in Depth* ch. 9,
  with upstream lab links.

Other application-shaped labs from the book live upstream: web-search and search+codegen
agents ([ch. 1](https://github.com/bojieli/ai-agent-book/tree/main/chapter1)) and
paper→slides→video, log diagnosis and text-to-SQL
([ch. 5](https://github.com/bojieli/ai-agent-book/tree/main/chapter5)).

---

## Cross-links

- [03-agentic-foundations/](../03-agentic-foundations/README.md) — the course material
  that taught the frameworks these projects use.
- [04-agentic-frameworks/](../04-agentic-frameworks/README.md) — framework reference
  material: LangGraph and ADK docs used during implementation.
- [06-observability/](../06-observability/README.md) — LangFuse integration for tracing
  and evaluation of deployed agents.
- [ai-engineering/03-harness-engineering/](../../ai-engineering/03-harness-engineering/README.md) — harness
  architecture notes applicable to both projects here.
