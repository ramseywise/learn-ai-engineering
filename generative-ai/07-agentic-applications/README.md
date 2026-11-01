# 07 — Agentic Applications

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the path: last generative-ai pillar, the payoff. It holds end-to-end applications built with the frameworks and patterns from [03-agentic-foundations](../03-agentic-foundations/README.md) and [04-agentic-frameworks](../04-agentic-frameworks/README.md).

---

## What it is

Agentic applications are what the earlier pillars build toward: a model, tools, a loop and a deployment that complete a real task without step-by-step human direction. This pillar holds built and studied projects, not framework reference:

- **A bounded search agent.** Two LangGraph graphs behind FastAPI: a router that decides whether to search, and a plan → search → draft loop that writes a sectioned report.
- **An open-ended deep-research agent.** A from-scratch tool-calling loop with context compaction, scored on DeepResearch Bench with an LLM judge, then trained with RL.
- **Real-time multimodal agents.** Voice, computer use and robotics, where latency and perception change the architecture.
- **A coding agent.** A read, edit, test loop in a sandbox with limits, built here and run end to end against a toy repo.
- **A data-analysis agent.** Read-only SQL and pandas tools over real datasets, a validator that recomputes each claim, and charts, also built here.
- **Application patterns.** Where the agent sits in the user's work (chatbot, collaborative editor, ambient background agent), and one engine re-tasked to a new domain by changing only its corpus.

## Why it matters

Models get swapped out every few months, and the application decisions stay: how much autonomy to grant, what limits to enforce, what counts as done and who checks it. Most production incidents with agents are failures in those decisions. They are not model failures, and you can only learn to spot them by building and breaking a few agents.

## The story in one paragraph

Start with an agent whose cost is bounded because the graph is fixed. Open the loop to get a research agent that handles open-ended work, and learn the price: context fills up, runs wander, and a report needs a judge that is itself fallible. Add a clock with voice and screens, where every stage eats into a budget people can feel. Then take two applications with a stricter judge. A coding agent has tests, but tests can be gamed, so hold some back. A data agent has numbers that can be recomputed, but a correct number can answer the wrong question, so agree the metric first. Across all of them the question is the same: **what would prove this answer wrong, and who checks?** Finally, place the agent next to a person, because a confirmation they cannot evaluate protects nothing.

---

## Reading order

| # | Note | Covers | Source |
|---|---|---|---|
| 01 | [Internet search agent](notes/01-internet-search-agent.md) | Router node vs search tool, structured decisions, the plan → section loop, checkpointers, FastAPI serving, code review, a stubbed graph you can run | internet-search-agent (MIT) |
| 02 | [Deep research bot](notes/02-deep-research-bot.md) | A minimal agent loop, Exa tools, think/plan tools, context compaction, RACE scoring, RL with ART + RULER, how the design has spread into research and science agents | W&B workshop; DeepResearch Bench; 15 papers |
| 03 | [Real-time multimodal agents](notes/03-real-time-multimodal-agents.md) | Cascaded vs omni vs full-duplex voice, the latency budget, fast/slow thinking, computer use, the GUI-agent literature, VLA robotics, Sim2Real | Li, *AI Agents in Depth* ch. 6; GUI-agent papers |
| 04 | [A coding agent](notes/04-coding-agent.md) | Reproduce, localize, patch, verify; the agent-computer interface; edits that fail safely; what each sandbox layer stops; held-out tests; supervision | SWE-agent; OpenDev; Shen & Tamkin; [practice/coding-agent](practice/coding-agent/) |
| 05 | [A data-analysis agent](notes/05-data-analysis-agent.md) | Profiling, read-only access below the level of the text, agreeing the metric, a validator that recomputes, charts, guards | Biswal et al.; Liu et al.; [practice/data-analysis-agent](practice/data-analysis-agent/) |
| 06 | [Application patterns](notes/06-application-patterns.md) | Chatbot, collaborative editing (merge levels, CRDT/OT, concurrency, undo) and ambient agents (triggers, memory, reflection); NLU routers; explanations and trust; one engine re-tasked to marketing, and its grounding failure | Oshin & Campos, *Learning LangChain* ch. 11; Rothman ch. 9; dialogue and HAI papers |

Note 06 is the synthesis, so read it last, or read it first if you are designing the UI around one of these agents. Papers and upstream repos are in [references.md](references.md).

## Run the labs

Both of the labs built for this pillar run offline, with a scripted stub model in place of an API. Neither needs a key.

```bash
cd generative-ai/07-agentic-applications/practice/coding-agent
uv run python run.py                 # all scenarios: fix, overfit, guards, timeout, loop, budget, giveup, escape
uv run python -m unittest test_agent

cd ../data-analysis-agent
uv run --with pandas --with matplotlib python run.py
uv run --with pandas --with matplotlib python -m unittest test_agent
```

Details are in the [coding-agent](practice/coding-agent/README.md) and [data-analysis-agent](practice/data-analysis-agent/README.md) READMEs. To drive either with Claude, see its `claude_model.py`, which needs `ANTHROPIC_API_KEY` and is marked illustrative.

## The deck

[slides/agentic-applications.pptx](slides/agentic-applications.pptx), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=generative-ai/07-agentic-applications`. It follows the same order as the notes.

---

## Layout

```
07-agentic-applications/
├── README.md
├── references.md
├── notes/
│   ├── 01-internet-search-agent.md
│   ├── 02-deep-research-bot.md
│   ├── 03-real-time-multimodal-agents.md
│   ├── 04-coding-agent.md
│   ├── 05-data-analysis-agent.md
│   └── 06-application-patterns.md
├── practice/
│   ├── coding-agent/             # built here: read/edit/test agent, toy repo, stub model, offline
│   ├── data-analysis-agent/      # built here: SQL + pandas agent over tips and Titanic, offline
│   ├── deep-research-bot/        # W&B workshop agent (Apache-2.0), notebooks 01–03, RACE eval
│   └── deep_research_bench/      # DeepResearch Bench RACE scorer (Apache-2.0), vendored
├── slides/                       # deck.yaml, agentic-applications.pptx
└── sources/
    ├── images/                   # li-ai-agents-in-depth-fig6-*.svg, context-engineering-multi-agent-systems-fig9-1.png, lab chart
    ├── context-engineering-multi-agent-systems/   # ch. 9 PDF
    └── *.pdf                     # research-agent, GUI-agent, dialogue and human-AI interaction papers
```

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
| The agent edits an artifact the user is also editing | Decide the merge level (branch + diff, or real-time CRDT/OT) before building the agent; emit targeted edits, never whole rewrites |
| A run takes tens of seconds | Make it ambient or batch and deliver a summary; don't put it behind a chat turn |
| The goal asks for something the corpus doesn't contain | Say so, and label inferred claims separately from cited ones |
| A coding agent says it is done | Believe the test run and not the sentence. Keep some tests out of its sight, and enforce limits in the tools, since a prompt is only advice |
| Sandbox limits | Say what each layer stops and what it does not. A path check does not contain a subprocess that can write anywhere |
| A data agent reports a number | Recompute it from the query, separately from the model's sentence. Agree the metric before the query runs |
| Data access for an agent | Enforce read-only at the connection and not by inspecting the SQL text |
| A person must approve an action | Show evidence they can check, such as the diff or the recomputed number. Explanations also persuade when the AI is wrong |
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

- W&B *Building Agents from Scratch* workshop → 02. Li, *AI Agents in Depth* ch. 6 → 03. Oshin & Campos, *Learning LangChain* ch. 11 → 06. Rothman, *Context Engineering for Multi-Agent Systems* ch. 9 → 06. Details and upstream links are in [references.md](references.md#books), and courses are in [Courses and videos](references.md#courses-and-videos).

### Coursework

The two labs built here run offline and are covered above. The items below were not executed for these notes, and the labels describe what each one needs.

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

### Datasets used by the data-analysis lab

Read in place and not copied: [tips.csv](../../data-analytics/01-python-for-data-analysis/practice/data/tips.csv) and [titanic/train.csv](../../data-analytics/01-python-for-data-analysis/practice/mckinney/datasets/titanic/train.csv).

### Interview guide

- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md): compressed summary for interview prep.

### Layers

- Previous: [06-observability](../06-observability/README.md).
- Next: [ai-engineering](../../ai-engineering/README.md), the engineering layer under these applications (context, harness, loop and graph engineering).
