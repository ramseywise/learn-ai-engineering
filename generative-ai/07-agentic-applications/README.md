# 07 — Agentic Applications

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the path: last generative-ai pillar, the payoff. It holds end-to-end applications built with the frameworks and patterns from [03-agentic-foundations](../03-agentic-foundations/README.md) and [04-agentic-frameworks](../04-agentic-frameworks/README.md).

---

## What it is

Agentic applications are what the earlier pillars build toward: a model, tools, a loop and a deployment that complete a real task without step-by-step human direction. This pillar is deliberately small. It holds built or studied projects, not course material:

- **A bounded search agent.** Two LangGraph graphs behind FastAPI: a router that decides whether to search, and a plan → search → draft loop that writes a sectioned report.
- **An open-ended deep-research agent.** A from-scratch tool-calling loop with context compaction, scored on DeepResearch Bench with an LLM judge, then trained with RL.
- **Real-time multimodal agents.** Voice, computer use and robotics, where latency and perception change the architecture.

The pillar's question is the same throughout: how much autonomy does the task need, and what does that cost in calls, latency and failure modes?

---

## Start here

1. Read [01 — Internet search agent](notes/01-internet-search-agent.md). It shows a fixed graph with a bounded cost.
2. Read [02 — Deep research bot](notes/02-deep-research-bot.md), then open [practice/deep-research-bot/notebooks/01_simple_agent.ipynb](practice/deep-research-bot/notebooks/01_simple_agent.ipynb). This is the open loop, and how to evaluate it.
3. Read [03 — Real-time multimodal agents](notes/03-real-time-multimodal-agents.md) for agents whose inputs are audio, screens and sensors.
4. Look up papers and upstream repos in [references.md](references.md).

---

## Layout

```
07-agentic-applications/
├── README.md
├── references.md
├── notes/
│   ├── 01-internet-search-agent.md
│   ├── 02-deep-research-bot.md
│   └── 03-real-time-multimodal-agents.md
├── practice/
│   ├── deep-research-bot/        # W&B workshop agent (Apache-2.0), notebooks 01–03, RACE eval
│   └── deep_research_bench/      # DeepResearch Bench RACE scorer (Apache-2.0), vendored
└── sources/
    ├── images/                   # li-ai-agents-in-depth-fig6-*.svg
    ├── context-engineering-multi-agent-systems/
    └── *.pdf                     # dialogue-systems and human-AI interaction papers (queued)
```

---

## Syllabus

| # | Note | Covers | Source |
|---|---|---|---|
| 01 | [Internet search agent](notes/01-internet-search-agent.md) | Router node vs search tool, structured decisions, the plan → section loop, checkpointers, FastAPI serving, code review | internet-search-agent (MIT) |
| 02 | [Deep research bot](notes/02-deep-research-bot.md) | A minimal agent loop, Exa tools, think/plan tools, context compaction, RACE scoring, RL with ART + RULER, code review | W&B workshop; DeepResearch Bench |
| 03 | [Real-time multimodal agents](notes/03-real-time-multimodal-agents.md) | Cascaded vs omni vs full-duplex voice, fast/slow thinking, computer use, VLA robotics, Sim2Real | Li, *AI Agents in Depth* ch. 6 |

---

## Rules of thumb

| Situation | Do |
|---|---|
| The task has a known shape (search → answer, outline → sections) | Use a fixed graph. Cost is bounded and failures are local |
| The task is open-ended research | Use a loop with a step cap and a token budget, and compact the context before it overflows |
| Deciding whether to search | Let a router node with structured output decide, rather than hoping the model calls the tool |
| Long conversations or reports | Persist state with a checkpointer. Do not rebuild it from chat history |
| Judging a research report | Score it relative to a reference report (RACE-style), with several judge samples, not one |
| Training an agent | Do it only after the eval is stable. RL optimises whatever the reward measures |
| Voice | Stream ASR → LLM → TTS and start speaking before the full answer is ready, or go full-duplex |
| Computer use | Prefer APIs and the DOM to pixels. Use vision for grounding only where there is no structure |
| Third-party search APIs | Wrap them behind one client interface. Bing Search was retired in 2025 and broke agents that called it directly |

---

## Resource map

### Related notes

- [03-agentic-foundations/notes/01-agent-fundamentals.md](../03-agentic-foundations/notes/01-agent-fundamentals.md) and [02-tool-use-and-react.md](../03-agentic-foundations/notes/02-tool-use-and-react.md): the loop and tool calling these projects use.
- [04-agentic-frameworks](../04-agentic-frameworks/README.md): LangGraph and ADK reference.
- [06-observability](../06-observability/README.md): tracing and evaluating deployed agents (Weave in 02, LangFuse elsewhere).
- [05-RL/notes/05-post-training-for-agents.md](../05-RL/notes/05-post-training-for-agents.md): the theory behind notebook 03's RL.
- [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/README.md): tool design ([03](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md)), long-horizon execution ([06](../../ai-engineering/03-harness-engineering/notes/06-long-horizon-execution.md)), failure modes ([08](../../ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes.md)).
- [02-rag-retrieval](../02-rag-retrieval/README.md): agentic RAG, the retrieval half of a research agent.

### Books and courses

- W&B *Building Agents from Scratch* workshop → 02. Li, *AI Agents in Depth* ch. 6 → 03. Details and upstream links are in [references.md](references.md#books-and-courses).

### Coursework

Not executed during consolidation. Labels describe what each needs.

| Item | Label | Needs |
|---|---|---|
| [practice/deep-research-bot/notebooks/01_simple_agent.ipynb](practice/deep-research-bot/notebooks/01_simple_agent.ipynb), [02_deep_research_agent.ipynb](practice/deep-research-bot/notebooks/02_deep_research_agent.ipynb) | needs API key | W&B (Inference + Weave) and Exa keys; Python ≥ 3.12, `uv sync` |
| [practice/deep-research-bot/notebooks/03_rl_for_deep_research_agent.ipynb](practice/deep-research-bot/notebooks/03_rl_for_deep_research_agent.ipynb) | needs service | W&B Serverless RL (OpenPipe ART); upstream `add_rl` branch |
| [practice/deep-research-bot/eval_simple_agent.py](practice/deep-research-bot/eval_simple_agent.py) | needs API key | W&B + Exa keys; the judge model runs on W&B Inference |
| `practice/deep-research-bot/tests/test_eval.ipynb` | needs API key | Eval smoke test over the `fixture_*.jsonl` files; calls the judge model |
| [practice/deep_research_bench/](practice/deep_research_bench/) | needs API key | Gemini + Jina keys; the benchmark data (from the upstream repo / Hugging Face; `data/` is gitignored) |
| [internet-search-agent](https://github.com/omidreza-amrollahi/internet-search-agent) (upstream, not copied) | legacy | Azure OpenAI + Bing Search (retired 2025); optional crawl4ai on :11235. Unit tests run offline with mocks |
| Li ch. 6 labs ([upstream](https://github.com/bojieli/ai-agent-book)) | needs API key / GPU | Voice labs need ASR/TTS keys; robotics labs need a simulator and GPU |
| Li ch. 1 and ch. 5 application labs ([ch. 1](https://github.com/bojieli/ai-agent-book/tree/main/chapter1), [ch. 5](https://github.com/bojieli/ai-agent-book/tree/main/chapter5)) | needs API key | LLM and search keys |

### Readings

- Queued PDFs in [sources/](sources/): dialogue systems (DIET, Dialogue Transformers, joint intent/slot BERT, slot-filling survey, conversational AI survey) and human-AI interaction design (Amershi guidelines, Bansal, Yang). They are listed in [references.md](references.md#papers) and not yet folded into a note.

### Interview guide

- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md): compressed summary for interview prep.

### Layers

- Previous: [06-observability](../06-observability/README.md).
- Next: [ai-engineering](../../ai-engineering/README.md), the engineering layer under these applications (context, harness, loop and graph engineering).
