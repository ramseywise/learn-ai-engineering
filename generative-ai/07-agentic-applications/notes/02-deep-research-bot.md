---
origin: practice/deep-research-bot (W&B Fully Connected London 2025 workshop clone)
sources:
  - https://github.com/morganmcg1/deep-research-bot (Weights & Biases, "Building Agents from Scratch" workshop, 2025; Apache-2.0)
  - https://github.com/Ayanami0730/deep_research_bench (Du et al., DeepResearch Bench, Apache-2.0 code)
  - https://arxiv.org/abs/2506.11763 (DeepResearch Bench paper, RACE and FACT)
  - https://art.openpipe.ai/fundamentals/ruler (OpenPipe ART, RULER reward)
confidence: high
cleaned: 2026-10-31
---
# 2 — A deep research agent from scratch

> No framework: one `while` loop that calls the model with tools, appends the results and stops when the model answers in plain text. Add planning and think tools, compaction once the context passes 80%, a RACE judge for scoring, and optional RL on the same agent.

---

## Where this sits

[01](01-internet-search-agent.md) fixes the topology in a LangGraph graph. This project goes the other way. The model owns the control flow and the code only runs the loop. It is the "agent = LLM + tools + loop" definition from [03-agentic-foundations 01](../../03-agentic-foundations/notes/01-agent-fundamentals.md), built in about 200 lines, then traced, evaluated and trained. The code is kept in [practice/deep-research-bot/](../practice/deep-research-bot/).

| Notebook / file | Builds |
|---|---|
| `notebooks/01_simple_agent.ipynb` | Raw LLM call → manual tool call → schema from a docstring → agent loop → `SimpleAgent` class → Weave evaluation |
| `notebooks/02_deep_research_agent.ipynb` | Clarification, planning and think tools; the deep research prompt; token counting and compaction; RACE eval |
| `notebooks/03_rl_for_deep_research_agent.ipynb` | Serverless RL with OpenPipe ART: rollouts, RULER rewards, LoRA on Qwen3-14B |
| `deep_research_bot/agent.py`, `tools.py`, `utils.py` | The package version of notebooks 01–02 |
| `deep_research_bot/evaluation/` | RACE scorer as a `weave.Scorer`; judge prompts; config |
| `eval_simple_agent.py` | CLI: run the agent over the 100-query bench and score it |

| Setting | Value |
|---|---|
| Inference | W&B Inference, OpenAI-compatible: `base_url="https://api.inference.wandb.ai/v1"`, key `WANDB_API_KEY` |
| Agent model | `Qwen/Qwen3-235B-A22B-Instruct-2507` (also the compaction and refine model) |
| Judge model | `deepseek-ai/DeepSeek-R1-0528`, `temperature=1.0`, `reasoning_effort="low"` |
| Search | Exa `search_and_contents(type="auto")`, key `EXA_API_KEY` |
| Tracing | `weave.init(f"{entity}/{project}")`, `@weave.op` on every call and tool |

---

## The loop

```python
class AgentState(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)
    step: int = 0
    final_assistant_content: str | None = None    # set when the model answers without tools

    def new(self, **updates):                      # immutable-style update; re-runs validators
        return type(self).model_validate(self.model_dump() | updates)

class SimpleAgent:
    def __init__(self, model_name, system_message, tools, state_class=AgentState):
        self.tools = [function_tool(t) for t in tools]   # attach a JSON schema to each function
        ...

    @weave.op(name="SimpleAgent.step")
    def step(self, state):
        msgs = state.messages
        resp = call_model(self.model_name, msgs, tools=[t.tool_schema for t in self.tools])
        msgs.append(resp.model_dump())
        if resp.tool_calls:                               # model wants tools: run them, loop again
            msgs.extend(perform_tool_calls(self.tools, resp.tool_calls))
            final = None
        else:                                             # plain text = the answer
            final = resp.content
        return state.new(messages=msgs, step=state.step + 1, final_assistant_content=final)

    @weave.op(name="SimpleAgent.run")
    def run(self, user_prompt, max_turns=10, **state_kwargs):
        state = self.state_class(messages=[{"role": "system", "content": self.system_message},
                                           {"role": "user", "content": user_prompt}], **state_kwargs)
        for _ in range(max_turns):
            # Budget awareness: tell the model how many turns it has left
            state.messages.append({"role": "assistant",
                "content": f"You are in step {state.step+1}/{max_turns} of the agent loop. "
                           f"You have {max_turns - state.step - 1} turns left."})
            state = self.step(state)
            if state.final_assistant_content:
                return state
        # Out of turns: force an answer instead of returning nothing
        state.messages.append({"role": "assistant",
            "content": "The agent loop has finished. Produce an answer to the user's question."})
        return self.step(state)
```

Three details carry most of the robustness:

| Detail | Where | Why it matters |
|---|---|---|
| Bad tool JSON comes back to the model as a `tool` message ("Error: The JSON format for X was invalid…") | `perform_tool_calls` | The model repairs its own call next turn instead of crashing the run |
| Tool exceptions become `"Error executing tool: …"` | same | One failed search doesn't end the research |
| A turn counter in the transcript and a forced final turn | `run` | The model paces itself and always returns something |

**Tool schemas from docstrings.** `function_tool` reads the signature and type hints (`str`→`string`, `list[str]`→array, `Enum`→`enum`) and parses an `Args:` block for parameter descriptions. It is the hand-built version of what the OpenAI Agents SDK and Claude's tool runner do for you ([03-harness 03 — tool design](../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md)).

---

## Tools for deep research

| Tool | Returns | Purpose |
|---|---|---|
| `exa_search(query, num_results=12)` | title, first 1,000 chars, URL | Cheap breadth |
| `exa_search_and_refine(query, num_results=5)` | title, **LLM-extracted relevant text**, URL | Each page is condensed by a second model call before the agent sees it. This is context isolation per result |
| `async_exa_search_and_refine` | same, 5 concurrent refines via `weave.flow.util.async_foreach` | Same, faster |
| `planning_tool(plan)` | `None` | The plan exists only as the tool-call argument in the transcript |
| `think_tool(reflection)` | `None` | Same trick: a structured pause after each search |
| `clarification_tool(questions)` | the user's typed answer (`input()`) | Ask up to 3 questions before researching |

`planning_tool` and `think_tool` do nothing. Their value is that the model has to *write* a plan or reflection into a field with a described structure, and that text stays in context. This is the "think tool" pattern Anthropic described in 2025. The default deep tool set is `[planning_tool, think_tool, exa_search_and_refine]`. `clarification_tool` is left out because `input()` blocks any non-interactive run.

The prompt's stopping rules are what keep the cost down:

```text
**Stop Immediately When**:
- You can answer the user's question comprehensively
- You have 3+ relevant examples/sources for the question
- Your last 2 searches returned similar information
```

---

## Context engineering: compaction at 80%

```python
class AgentStateCompaction(AgentState):
    max_tokens: int = 5000              # the CLI passes 128_000
    compaction_count: int = 0
    compact_model_name: str = MODEL_SMALL
    _threshold: float = PrivateAttr(default=0.8)

    def model_post_init(self, _):       # runs on every state.new(...) → checked every step
        self._estimated_tokens = estimate_token_count(self.messages)   # len(json)/4 × 1.1
        if self._estimated_tokens > self.max_tokens * self._threshold:
            self.messages = self.compact_conversation()

    @weave.op(name="compact")
    def compact_conversation(self):
        system_msg, request_msg = self.messages[0], self.messages[1]   # always kept verbatim
        summary = call_model(self.compact_model_name, [
            {"role": "system", "content": "You are compacting a deep research agent's conversation history. ... Preserve: "
                                          "key findings (with source URLs), facts and statistics, research decisions, gaps"},
            {"role": "user", "content": f"Conversation to summarize:\n{json.dumps(self.messages[1:], indent=2)}"}])
        return [system_msg, request_msg,
                {"role": "assistant", "content": f"# Compacted conversation summary: \n\n{summary.content}"}]
```

The hook lives in the state class, so compaction is invisible to the loop. The trade-offs are the ones in [02-context engineering](../../../ai-engineering/02-context-engineering/README.md): a character-count estimate instead of a tokenizer, and a summary that replaces *everything* after the request. The last tool result goes too, though the comment says "system + summary + recent messages".

---

## Evaluation: RACE against a reference report

DeepResearch Bench ([Du et al., 2025](https://arxiv.org/abs/2506.11763)) has 100 PhD-level tasks (50 Chinese, 50 English), each with a reference report and **task-specific weighted criteria**. RACE asks a judge to score the target and the reference side by side, per criterion, 0–10.

```python
class CriterionScore(BaseModel):
    criterion: str
    analysis: str
    article_1_score: int     # target
    article_2_score: int     # reference

class JudgeOutput(BaseModel):          # judge must fill all four dimensions
    comprehensiveness: list[CriterionScore]
    insight: list[CriterionScore]
    instruction_following: list[CriterionScore]
    readability: list[CriterionScore]

# Per dimension d: weighted average over its criteria, for target T and reference R
#   T_d = Σ w_c · s_c^T / Σ w_c
# Overall: weight each dimension by the task's dimension_weight (e.g. insight 0.36, comprehensiveness 0.30)
#   T = Σ_d W_d · T_d
# Report relative quality, so a judge's harshness cancels out:
def normalize_dimension(target, reference):
    return target / (target + reference) if target + reference > 0 else 0.0   # 0.5 = as good as the reference
```

| Choice | Effect |
|---|---|
| Pairwise against a reference, then `T/(T+R)` | Score is relative. 0.5 means "matches the reference". Judge drift affects both articles |
| Per-task criteria and weights (in `criteria.jsonl`) | "Insight" means something specific for each task |
| Fuzzy criterion matching, fallback to the mean weight | The judge paraphrasing a criterion doesn't drop it |
| `weave.Evaluation` with `trials=2`, `limit=20` by default | Each run is a traced, comparable experiment in W&B |

```bash
# Simple agent, 20 English prompts, 2 trials
uv run eval_simple_agent.py --wandb_entity <you> --limit 20 --trials 2
# Deep agent: planning + think + refine tools, compaction on
uv run eval_simple_agent.py --wandb_entity <you> --deep True
```

The upstream bench (kept in [practice/deep_research_bench/](../practice/deep_research_bench/)) also has **FACT**: it extracts each cited statement–URL pair, fetches the page with Jina Reader and checks support. That gives citation accuracy and effective citations per task. The workshop port implements RACE only.

---

## RL on the same agent (notebook 03)

| Piece | Value |
|---|---|
| Framework | OpenPipe ART, `ServerlessBackend` (training runs on W&B GPUs) |
| Base model | `OpenPipe/Qwen3-14B-Instruct`, LoRA |
| Reward | RULER: an LLM judge (DeepSeek-V3.1) ranks the trajectories in a group against a rubric (ART default + "thorough, balanced, objective; information dense") |
| Loop | `groups_per_step=2` questions × `rollouts_per_group=2`, `learning_rate=1e-5`, `max_turns=2` |
| Demo twist | The system prompt asks for "comically wicked" answers, so you can *see* the policy shift after 1 vs. 27 steps |

The grouping is GRPO-style: rewards are relative within a group, so RULER only needs to rank, not to score absolutely. Theory: [05-RL 05 — post-training for agents](../../05-RL/notes/05-post-training-for-agents.md).

---

## Review: what to fix before reusing it

| Issue | Where | Fix |
|---|---|---|
| `--deep` builds `DEEP_RESEARCH_AGENT_PROMPT` but passes the simple prompt to `SimpleAgent` | `eval_simple_agent.py` | Pass `system_message` |
| Docstring parser splits on the literal string `"\\n"`, so parameter descriptions are never parsed | `utils._generate_tool_schema` | `split("\n")` |
| Compaction drops the most recent tool results | `compact_conversation` | Keep the last k messages after the summary |
| `execute_tool` uses `asyncio.run` per async tool | `utils.py` | Breaks inside notebooks or servers with a running loop; make the loop async |
| `clarification_tool` calls `input()` | `tools.py` | Make it an interrupt (see [05-graph 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md)) |
| Notebook 03 installs the `add_rl` branch, which has helpers missing from the local package (`_to_plain`, `WANDB_BASE_URL`) | notebook 03 | Run it in Colab from upstream |
| A single judge (DeepSeek-R1) with `temperature=1.0` | `eval_config.py` | Run ≥2 trials and report variance, or use two judges |

---

## Rules of thumb

| Rule | Why |
|---|---|
| Write the bare loop once before reaching for a framework | You'll know what the framework is hiding |
| Return tool errors and bad JSON to the model as tool messages | It self-corrects; the run survives |
| Put the turn budget in the transcript and force a final answer | The model paces itself; no empty runs |
| Refine each search result with a cheap model before the agent sees it | Keeps the main context small and on-topic |
| Give the model no-op `plan` and `think` tools | Structured reflection, kept in context |
| Compact at a threshold inside the state, not the loop | The loop stays simple; the policy is in one place |
| Score research reports pairwise against a reference, normalised | Absolute LLM-judge scores drift; ratios hold up better |

---

## Labs

| Project | Label |
|---|---|
| [practice/deep-research-bot/](../practice/deep-research-bot/) notebooks 01–02, `eval_simple_agent.py` | needs API key (W&B Inference `WANDB_API_KEY`, Exa `EXA_API_KEY`); Python ≥3.12, `uv sync`; `uv run pytest -vv` for `tests/` |
| notebook 03 (RL) | needs W&B Serverless RL (W&B Training) + API key; installs upstream `add_rl` branch |
| [practice/deep_research_bench/](../practice/deep_research_bench/) | needs API key (`GEMINI_API_KEY` for RACE, `JINA_API_KEY` for FACT) + the dataset from [Hugging Face](https://huggingface.co/datasets/muset-ai/DeepResearch-Bench-Dataset) (its `data/` is gitignored) |

→ Next: [03-real-time-multimodal-agents.md](03-real-time-multimodal-agents.md) — the same loop under a hard time budget: voice, computer use and robots.
