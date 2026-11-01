---
origin: practice/deep-research-bot (W&B Fully Connected London 2025 workshop clone)
sources:
  - https://github.com/morganmcg1/deep-research-bot (Weights & Biases, "Building Agents from Scratch" workshop, 2025; Apache-2.0)
  - https://github.com/Ayanami0730/deep_research_bench (Du et al., DeepResearch Bench, Apache-2.0 code)
  - https://arxiv.org/abs/2506.11763 (DeepResearch Bench paper, RACE and FACT)
  - https://art.openpipe.ai/fundamentals/ruler (OpenPipe ART, RULER reward)
  - https://www.microsoft.com/en-us/research/wp-content/uploads/2025/06/Code_Researcher-1.pdf (Singh et al., Code Researcher, 2025)
  - https://www.datocms-assets.com/64837/1763496622-dr_tulu_draft.pdf (Shao et al., DR Tulu: RL with Evolving Rubrics, 2025)
  - https://arxiv.org/abs/2506.18096 (Huang et al., Deep Research Agents survey, 2025)
  - https://arxiv.org/abs/2503.20201 (Alzubi et al., Open Deep Search, 2025)
  - https://arxiv.org/abs/2507.16075 (Han et al., TTD-DR, 2025)
  - https://arxiv.org/abs/2408.06292 (Lu et al., The AI Scientist, 2024)
confidence: high
cleaned: 2026-11-01
---
# 2 — A deep research agent from scratch

> No framework: one `while` loop that calls the model with tools, appends the results and stops when the model answers in plain text. Add planning and think tools, compaction once the context passes 80%, a RACE judge for scoring, and optional RL on the same agent.

The search agent in the last note could never surprise you, and that was its limit: three sections, whatever the question. A research question worth an hour of an analyst's time needs more searches when the first ones fail and fewer when they succeed, so here the model takes over the control flow and the code does almost nothing. That raises the questions this note is about. What stops the model when the budget is open-ended? What happens when the transcript no longer fits? And with no test suite and no known answer, how would you know that one report is better than another? We build the loop, run it offline with a stub, score reports against a reference, and then survey how far recent systems have taken the same idea.

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
# illustrative: upstream excerpt from deep_research_bot/agent.py. Needs W&B Inference, Exa and Weave keys.
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

The loop needs no key to run. Here it is with a scripted model: a bad tool call that comes back as a message, a turn counter, and a forced answer if the budget runs out.

```python
import json


def search(query):
    return f"3 sources on {query}"


TOOLS = {"search": search}


def perform_tool_call(call):
    try:
        args = json.loads(call["arguments"])
        return TOOLS[call["name"]](**args)
    except json.JSONDecodeError:
        return f"Error: the JSON for {call['name']} was invalid. Send it again."
    except Exception as err:
        return f"Error executing tool: {err}"


class ScriptedModel:
    """Stands in for call_model. Each entry is one turn: tool calls, or plain text."""

    def __init__(self, turns):
        self.turns = iter(turns)

    def __call__(self, messages):
        return next(self.turns, "(plain text) best answer from what I have")


def run(model, prompt, max_turns=3):
    messages = [{"role": "user", "content": prompt}]
    for step in range(max_turns):
        messages.append({"role": "system", "content": f"You have {max_turns - step - 1} turns left."})
        reply = model(messages)
        if isinstance(reply, str):
            return f"answered at step {step + 1}: {reply}"
        for call in reply:
            result = perform_tool_call(call)
            print(f"  step {step + 1} {call['name']}: {result}")
            messages.append({"role": "tool", "content": result})
    messages.append({"role": "system", "content": "The loop has finished. Answer now."})
    return f"forced at the end: {model(messages)}"


good = {"name": "search", "arguments": '{"query": "EU shipping rules"}'}
bad = {"name": "search", "arguments": '{"query": '}
wrong = {"name": "search", "arguments": '{"topic": "x"}'}
print(run(ScriptedModel([[bad], [good], "(plain text) a cited answer"]), "Shipping rules?"))
print(run(ScriptedModel([[wrong], [good], [good], [good]]), "Keep searching"))
```

Output:

```text
  step 1 search: Error: the JSON for search was invalid. Send it again.
  step 2 search: 3 sources on EU shipping rules
answered at step 3: (plain text) a cited answer
  step 1 search: Error executing tool: search() got an unexpected keyword argument 'topic'
  step 2 search: 3 sources on EU shipping rules
  step 3 search: 3 sources on EU shipping rules
forced at the end: [{'name': 'search', 'arguments': '{"query": "EU shipping rules"}'}]
```

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
# illustrative: upstream excerpt. `call_model` needs a W&B Inference key.
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

Both behaviours are easy to see with a stub summarizer. Note how the last tool result vanishes, which is the review item below, and what happens to the threshold check when the summary is short.

```python
import json

MAX_TOKENS, THRESHOLD = 300, 0.8


def estimate_tokens(messages):
    return int(len(json.dumps(messages)) / 4 * 1.1)  # the upstream estimate: characters, not a tokenizer


def summarize(messages):  # stands in for the compaction model
    return f"# Compacted summary of {len(messages)} messages, keeping key findings and URLs"


def maybe_compact(messages):
    if estimate_tokens(messages) <= MAX_TOKENS * THRESHOLD:
        return messages, False
    system, request = messages[:2]
    return [system, request, {"role": "assistant", "content": summarize(messages[2:])}], True


messages = [{"role": "system", "content": "You research."}, {"role": "user", "content": "Shipping rules?"}]
for step in range(1, 9):
    messages.append({"role": "tool", "content": f"result {step}: " + "evidence " * 25})
    messages, compacted = maybe_compact(messages)
    print(f"step {step}: {len(messages)} messages, about {estimate_tokens(messages)} tokens"
          + ("  <- compacted, latest result gone" if compacted else ""))
```

Output:

```text
step 1: 3 messages, about 100 tokens
step 2: 4 messages, about 173 tokens
step 3: 3 messages, about 54 tokens  <- compacted, latest result gone
step 4: 4 messages, about 128 tokens
step 5: 5 messages, about 201 tokens
step 6: 3 messages, about 54 tokens  <- compacted, latest result gone
step 7: 4 messages, about 128 tokens
step 8: 5 messages, about 201 tokens
```

Code Researcher ([Microsoft Research, 2025-06](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/06/Code_Researcher-1.pdf) (Singh et al., 2025-06)) uses the same research-then-write split on Linux kernel crashes, with a different way of managing context. Its Analysis phase searches definitions, code patterns and past commit messages and diffs (`search_commits(regex)`). Each (action, result) pair goes into a structured memory instead of a running summary. Before writing a patch, the Synthesis phase filters out the pairs that turned out to be irrelevant. On 200 kBenchSyz crashes, with GPT-4o, 15 LLM calls, a 50K-token context limit and best of 5 tries, it resolved 48% against 31.5% for SWE-agent. It explored 10 files per trajectory against 1.33. Using o1 for the patch-writing step raised that to 58%, above o1 handed the ground-truth buggy files (51%). Dropping commit search cut the resolution rate from 48% to 38%. That ablation was run on only the 96 bugs it had already solved, so the two percentages don't share a denominator. "Resolved" means the reproducer no longer crashes, and the authors note that some of those patches only block the crash path without fixing the cause.

---

## Evaluation: RACE against a reference report

DeepResearch Bench ([Du et al., 2025](https://arxiv.org/abs/2506.11763)) has 100 PhD-level tasks (50 Chinese, 50 English), each with a reference report and **task-specific weighted criteria**. RACE asks a judge to score the target and the reference side by side, per criterion, 0–10.

```python
# illustrative: upstream excerpt. The judge that fills these fields needs an API key.
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

The arithmetic runs on its own. Note the judge that is harsh on both reports: its raw scores fall, and the normalized score barely moves.

```python
WEIGHTS = {"comprehensiveness": 0.30, "insight": 0.36, "instruction_following": 0.20, "readability": 0.14}


def weighted(scores, weights):
    return sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)


def normalize_dimension(target, reference):
    return target / (target + reference) if target + reference > 0 else 0.0


def race(judged):
    total_target = total_reference = 0.0
    for dimension, weight in WEIGHTS.items():
        criteria = judged[dimension]
        criterion_weights = [c[0] for c in criteria]
        total_target += weight * weighted([c[1] for c in criteria], criterion_weights)
        total_reference += weight * weighted([c[2] for c in criteria], criterion_weights)
    return total_target, total_reference, normalize_dimension(total_target, total_reference)


# each criterion: (weight, score for the target report, score for the reference report)
fair = {"comprehensiveness": [(0.6, 7, 8), (0.4, 6, 7)], "insight": [(1.0, 5, 8)],
        "instruction_following": [(1.0, 9, 9)], "readability": [(1.0, 8, 7)]}
harsh = {name: [(w, max(t - 2, 0), max(r - 2, 0)) for w, t, r in rows] for name, rows in fair.items()}
for label, judged in [("fair judge", fair), ("harsh judge", harsh)]:
    target, reference, score = race(judged)
    print(f"{label:<12} target {target:.2f}  reference {reference:.2f}  normalized {score:.3f}")
```

Output:

```text
fair judge   target 6.70  reference 7.94  normalized 0.458
harsh judge  target 4.70  reference 5.94  normalized 0.442
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

RULER's rubric is fixed. DR Tulu ([DR Tulu](https://www.datocms-assets.com/64837/1763496622-dr_tulu_draft.pdf) (Shao et al., 2025-11)) makes it move, and calls the method RLER. Training starts from Qwen3-8B fine-tuned on 16K GPT-5 research trajectories. The judge, GPT-4.1-mini, scores every rollout against two sets of rubrics:
- **Persistent rubrics**, written once per question from search results.
- **Evolving rubrics**, regenerated each step by comparing the current rollouts. Positive ones reward new knowledge the policy found. Negative ones penalize hacks the judge noticed, such as copying retrieved text verbatim to farm citation precision.

Rubrics with zero reward variance across a group are dropped, because they can't rank anything. In the ablation, generic rubrics lowered the four-benchmark average by 1.1 points. Search-grounded rubrics raised it by 1.7, and adding evolving rubrics on a second SFT base gave +4.0 against +3.1. After RL, the 8B model averaged 60.7 against 53.9 for SFT alone. It beat OpenAI Deep Research on AstaBench ScholarQA-CSv2, 86.7 to 79.6, at about $0.00008 a query in API fees (hosting excluded) against $1.80. Several caveats apply:
- Many of the proprietary-system scores are copied from the benchmarks' authors, not rerun.
- Search results drift between runs.
- The run with the highest training reward did worse downstream. The authors blame the gap between the in-loop judge and the different judges used for evaluation.

---

## How far the design has spread

Once you know the loop, a recent paper can be read by asking which part it changed. Huang et al.'s survey offers a useful map: static versus dynamic workflows, single versus multi-agent planning, API versus browser retrieval, and tuning by prompt, fine-tuning or RL (Huang et al., [Deep Research Agents](https://arxiv.org/abs/2506.18096), 2025, preprint). Notes 01 and 02 are its two ends: static with a fixed path, dynamic with a free one.

| Part changed | System | The idea, and what was measured |
|---|---|---|
| Retrieval | Open Deep Search ([Alzubi et al.](https://arxiv.org/abs/2503.20201), 2025) | An open search tool plus a reasoning agent. With DeepSeek-R1, 82.4% on SimpleQA and 30.1% on FRAMES at the base setting, and the authors report a 9.7% FRAMES gain on GPT-4o Search Preview for the best configuration (75.3%) |
| Plan shape | TTD-DR ([Han et al.](https://arxiv.org/abs/2507.16075), 2025) | Starts from a draft and revises it with retrieval, like denoising. 69.1% and 74.5% win rates against OpenAI Deep Research in side-by-side comparisons on two long-form tasks; the judging setup is the authors' own |
| Interleaving | WebThinker ([Li et al.](https://arxiv.org/abs/2504.21776), NeurIPS 2025) | Think, search and draft are interleaved instead of fixed phases, with online DPO to tune tool use |
| Who owns the plan | Universal Deep Research ([Belcak et al.](https://arxiv.org/abs/2509.00244), 2025) | Users write the strategy in natural language. The authors report that devising strategies was tedious even for those who value the control |
| Training | SFR-DeepResearch ([Nguyen et al.](https://arxiv.org/abs/2509.06283), 2025) | A single autonomous agent trained by RL on synthetic data. The 20B model reached up to 28.7% on Humanity's Last Exam |
| Training data | DeepDive ([Lu et al.](https://arxiv.org/abs/2509.10446), 2025) | Knowledge-graph questions and multi-turn RL with a penalty on redundant queries. 15.3% on BrowseComp |
| Capabilities and eval | Step-DeepResearch ([Hu et al.](https://arxiv.org/abs/2512.20491), 2025) | Trains atomic capabilities on a 32B model, and argues that ground-truth benchmarks such as BrowseComp miss open-ended work, proposing ADR-Bench with expert judges |
| Enterprise | Enterprise Deep Research ([Prabhakar et al.](https://arxiv.org/abs/2510.17797), 2025) | A planner over specialized search agents, NL2SQL and visualization, with human steering during reflection. See [note 05](05-data-analysis-agent.md) for the SQL half |

All are preprints except where a venue is shown, and these numbers come from different tasks and judges, so do not compare across rows. The recurring disagreement matters most: are short ground-truth questions or long judged reports the right measure? Both are partial, which is why this note's RACE score is only one instrument.

The same loop has also been pointed at research itself. Here the check gets harder, because a result is supposed to be new, and the most useful thing in these papers is how they handle that.

- **The AI Scientist** runs ideation, experiment, write-up and a simulated review, for under $15 a paper ([Lu et al.](https://arxiv.org/abs/2408.06292), 2024, preprint). **Agent Laboratory** covers the same span with human oversight, at $2.33 for its full process ([Schmidgall et al.](https://arxiv.org/abs/2501.04227), 2025, preprint). Costs for different pipelines are not like for like.
- **The AI Scientist-v2** adds agentic tree search and vision-model feedback on figures, and reports the first fully AI-generated paper accepted by peer review at a workshop ([Yamada et al.](https://pub.sakana.ai/ai-scientist-v2/paper/paper.pdf), 2025).
- **CodeScientist** gives the most sobering figures: across hundreds of automatically run experiments it returned 19 candidate discoveries, of which 6 were judged at least minimally sound and incrementally novel. Those judgments went beyond reading the paper, to code review and replication ([Jansen et al.](https://arxiv.org/abs/2503.22708), Findings of ACL 2025).
- **Agentic Scientist** builds on headless coding agents, with sandboxed experiments and a meta-controller that enforces rubric verification at each stage ([Lange et al.](https://arxiv.org/abs/2610.18933), 2026-10, preprint). **AI Co-Mathematician** borrows its orchestration from software engineering to support the messy, iterative process of doing mathematics ([Zheng et al.](https://arxiv.org/abs/2605.06651), 2026-05, preprint).

Note the direction of travel: the later papers spend their design on verification. That is the question note [04](04-coding-agent.md) and note [05](05-data-analysis-agent.md) take up.

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

## Pitfalls

- **No stopping rule.** A model with open-ended tools will keep searching. Put explicit stop conditions in the prompt and a hard turn budget in the code.
- **Compaction that loses the latest evidence.** Summarizing everything after the request drops the result the model has just asked for. Keep the last few messages.
- **Compaction that loses citations.** If the summary drops URLs, later claims can no longer be sourced. Name them in the compaction prompt, and test for it.
- **Trusting a single judge.** One high-temperature LLM judge is noisy. Run several trials and report the spread.
- **Comparing absolute judge scores across runs.** Harshness drifts. Score relative to a reference.
- **Citations nobody checks.** RACE judges reports and does not fetch the pages. Without FACT or an equivalent, a confident invented link can score well.
- **Optimizing the in-loop judge.** DR Tulu's highest-reward run did worse downstream. A rubric you train against becomes a target.
- **Blocking tools in unattended runs.** `input()` in a tool hangs batch evaluation. Use an interrupt or a queue.

## Try it

The blocks above run as written. The full lab needs keys, as listed under Labs below, and was not run for this note.

1. **Keep the recent messages.** Change `maybe_compact` so that the last two messages survive. What does the printout show, and what can go wrong?

   <details><summary>Answer</summary>

   Return `[system, request, summary, *messages[-2:]]`, and summarize `messages[2:-2]`. The latest result stays available. The catch is that with long tool results, two messages may already be close to the threshold, so compaction fires every step. Compact to a target well below the trigger, or truncate the kept messages.
   </details>

2. **Find the judge's blind spot.** In the RACE block, give the target a 10 on everything and the reference a 10 on everything. What is the normalized score, and what does it mean if every system you test comes close to this?

   <details><summary>Answer</summary>

   0.5, by construction. If all systems cluster there, the judge has stopped discriminating, or the criteria are too easy, and the score no longer separates them. Look at the per-criterion spread and at the disagreement between trials.
   </details>

3. **Add a search budget.** Add a counter so that the tool returns an error after three searches. Should the agent see a tool error, or should the loop stop?

   <details><summary>Answer</summary>

   Prefer the tool message, such as "Search budget used. Answer from what you have", since it lets the model finish with what it knows. Keep the hard turn limit as the backstop for when it ignores the message. The turn counter works the same way in the loop above.
   </details>

## Interview checklist

| Question | Strong answer |
|---|---|
| What makes something a deep research agent? | A model-controlled loop of search and reading that decides its own depth, with a long structured report as the output. |
| Why return tool errors as messages? | The model can repair the call on the next turn, and the run survives one bad search. |
| What is a no-op think tool for? | It makes the model write down a plan or reflection in a described field, and the text stays in context. |
| How does compaction work here, and what does it risk? | At 80% of a token estimate, everything after the request becomes a summary. It risks losing recent tool results and URLs, so keep the last k and name what must be preserved. |
| What is RACE? | A judge scores the target and a reference report per criterion and per weighted dimension, and the report is `T/(T+R)`, so 0.5 means matches the reference and judge harshness largely cancels. |
| What does FACT add? | It checks citations by fetching the pages. RACE judges quality and does not verify sources. |
| What did Code Researcher change? | Structured memory of (action, result) pairs filtered before synthesis, and commit search. 48% against 31.5% for SWE-agent on 200 kBenchSyz crashes, under its stated budget. |
| How does RLER differ from RULER? | RULER's rubric is fixed. RLER adds rubrics regenerated per step, including negative ones that penalize discovered hacks. Its best-reward run did worse downstream, a warning about judge gaps. |
| How would you evaluate a research agent with no ground truth? | Reference-relative judged scores, plus citation verification, plus short-answer benchmarks for retrieval, with several trials. CodeScientist shows the last resort for claims: review the code and replicate. |

## Labs

| Project | Label |
|---|---|
| [practice/deep-research-bot/](../practice/deep-research-bot/) notebooks 01–02, `eval_simple_agent.py` | needs API key (W&B Inference `WANDB_API_KEY`, Exa `EXA_API_KEY`); Python ≥3.12, `uv sync`; `uv run pytest -vv` for `tests/` |
| notebook 03 (RL) | needs W&B Serverless RL (W&B Training) + API key; installs upstream `add_rl` branch |
| [practice/deep_research_bench/](../practice/deep_research_bench/) | needs API key (`GEMINI_API_KEY` for RACE, `JINA_API_KEY` for FACT) + the dataset from [Hugging Face](https://huggingface.co/datasets/muset-ai/DeepResearch-Bench-Dataset) (its `data/` is gitignored) |

## Next

[Real-time and multimodal agents](03-real-time-multimodal-agents.md) run the same loop under a hard time budget: voice, computer use and robots.
