# Lab: one research agent, built several ways

The pillar's running example. One agent answers "Why do framework agents get stuck in loops, and what stops them?" over a six-document corpus, and it is built with no framework, in LangGraph and in Google ADK. Everything runs offline with no API key, because the model is a deterministic stub (`decide()` in `research_lab.py`) that each framework cannot tell from a real one. The tools are plain Python functions shared by all three builds.

## Run it

From this folder. `uv` installs the dependencies into a throwaway environment.

| Note | Command | Shows |
|---|---|---|
| [01](../../notes/01-react-from-scratch-to-langgraph.md) | `uv run --with langgraph --with langchain-core python demo_01_react.py` | The hand-written loop, then the same agent as a graph |
| [02](../../notes/02-agentic-search-persistence-streaming.md) | `uv run --with langgraph --with langgraph-checkpoint-sqlite python demo_02_agentic.py` | Threads, resume, approval gates, rewind, streaming |
| [03](../../notes/03-long-term-memory-with-langgraph.md) | `uv run --with langgraph --with numpy python demo_03_long.py` | Semantic, episodic and procedural memory in a store |
| [04](../../notes/04-google-adk.md) | `uv run --with 'google-adk[eval]' python demo_04_google.py` | The agent on ADK, with limits, callbacks and evals |
| [05](../../notes/05-langsmith.md) | `uv run --with langgraph --with 'google-adk[eval]' --with langsmith --with wrapt python demo_05_langsmith.py` | LangSmith runs captured in memory, and `evaluate()` offline |
| [06](../../notes/06-framework-selection.md) | `uv run --with langgraph --with 'google-adk[eval]' python demo_06_selection.py` | Cost, stuck-run behaviour and export across the three builds. Takes about a minute, because it runs 5,004 stub model calls on purpose |
| [07](../../notes/07-lcel-composition-in-practice.md) | `uv run --with langchain-core python demo_07_lcel.py` | Chains, capped batches, structured output, plans, map-reduce |

Each `demo_NN` holds the runnable code from that note, in order. Blocks marked `# illustrative` in the notes need a paid service and are left out.

## Files

| File | What it is |
|---|---|
| `research_lab.py` | The corpus, the tools and the scripted brain. No framework imports |
| `agent_scratch.py` | The agent as a text protocol, a regex and a loop |
| `agent_langgraph.py` | A real `StateGraph` with a stub chat model |
| `agent_adk.py` | A real `LlmAgent` and `Runner` with a stub LLM |
| `agent_lcel.py` | A rule-driven chat model for LCEL, with `bind_tools` |
| `trace_capture.py` | A real `langsmith.Client` that keeps runs in memory |
| `compare.py` | Measures cold start, per-run time and lines for the three builds |
| `research_eval/`, `eval/` | The ADK evaluation agent and its eval set, used by note 04 |

## Using a real model

Swap the stub for a real one. This needs an API key:

```python
# illustrative: needs ANTHROPIC_API_KEY and the langchain-anthropic package.
from langchain_anthropic import ChatAnthropic
from agent_langgraph import build_agent

agent = build_agent(ChatAnthropic(model="claude-opus-5-5"))
```
