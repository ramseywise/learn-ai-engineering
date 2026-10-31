---
origin: course-synthesis
sources:
  - "DeepLearning.AI, AI Agentic Design Patterns with AutoGen (Chi Wang, Qingyun Wu), L1–L6 — https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/ ; snapshot upstream https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen"
  - "DeepLearning.AI, LLMs as Operating Systems: Agent Memory, L6 multi-agent orchestration — https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory"
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 6 P18 Reflection, ch 7 P23 Multiagent Collaboration — ../sources/lakshmanan-hapke-genai-design-patterns-ch07-enabling-agents-to-take-action.pdf"
  - "Cemri et al. 2025, Why Do Multi-Agent LLM Systems Fail? — https://arxiv.org/abs/2503.13657"
  - "Andrew Ng, Agentic Design Patterns (The Batch, 2024) — https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/"
  - https://arxiv.org/abs/2601.12307
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 7"
  - "Nicole Koenigstein, AI Agents: The Definitive Guide (O'Reilly, 2026), ch. 2"
  - "James Phoenix & Mike Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 6"
  - "Salvatore Raieli & Gabriele Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 4, 11"
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 2"
  - "Huang et al. 2024, Understanding the planning of LLM agents: A survey — https://arxiv.org/abs/2402.02716"
  - "Yao et al. 2023, Tree of Thoughts — https://arxiv.org/abs/2305.10601"
confidence: high
cleaned: 2026-10-31
---

# 4 — Multi-agent design patterns

> Andrew Ng's four agentic patterns (reflection, tool use, planning, multi-agent collaboration) can all be built from one primitive: agents that send each other messages until a stop condition fires.

---

## The pattern catalogues

| Source | Patterns |
|---|---|
| Andrew Ng, May 2024 | Reflection, Tool Use, Planning, Multi-agent Collaboration |
| OpenAI adds | LLM-as-Judge, Parallelization, Router, Guardrails |
| Anthropic | *Workflows* (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) vs *agents* (the model directs its own loop) |
| Lakshmanan & Hapke | P17 LLM-as-Judge, P18 Reflection, P21 Tool Calling, P22 Code Execution, P23 Multiagent Collaboration |

The AutoGen course walks through Ng's four patterns with one lesson each, plus two lessons on the conversation primitives underneath. The table below is the whole course; the sections after it pull out the code that matters.

| Lesson | Pattern | Example | Key AutoGen feature |
|---|---|---|---|
| L1 | Two-agent conversation | Two comedians | `ConversableAgent`, `initiate_chat`, termination |
| L2 | Sequential chats | Customer onboarding | `initiate_chats` with summaries carried forward |
| L3 | Reflection | Blog post with reviewers | nested chats |
| L4 | Tool use | Conversational chess | `register_function`, caller/executor split |
| L5 | Coding | Stock price plots | code executor, user-defined functions |
| L6 | Planning | Stock report | `GroupChat` with speaker transitions |

The course is pyautogen 0.2. AutoGen has since been rewritten (0.4 is event-driven) and Microsoft now points new work at the Microsoft Agent Framework; the patterns carry over, the class names do not. See [05 — framework survey](05-framework-survey.md).

---

## L1 — the primitive: a conversation

```python
from autogen import ConversableAgent

cathy = ConversableAgent(
    name="cathy",
    system_message="Your name is Cathy and you are a stand-up comedian.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)
joe = ConversableAgent(
    name="joe",
    system_message="Your name is Joe and you are a stand-up comedian. "
                   "Start the next joke from the punchline of the previous joke.",
    llm_config=llm_config,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "I gotta go" in msg["content"],  # stop condition
)

chat_result = joe.initiate_chat(
    recipient=cathy,
    message="I'm Joe. Cathy, let's keep the jokes rolling.",
    max_turns=2,                                   # hard stop
    summary_method="reflection_with_llm",          # LLM writes the summary
    summary_prompt="Summarize the conversation",
)
chat_result.chat_history, chat_result.cost, chat_result.summary
```

![Two agents in conversation](../sources/images/wang-wu-autogen-patterns-fig1.png)

*Figure: two-agent conversation (AutoGen course, L1).*

Every multi-agent system needs two stop conditions: a turn cap (`max_turns`) and a semantic one (`is_termination_msg`). Without the cap, two polite agents thank each other forever.

---

## L2 — sequential chats: a pipeline of conversations

Onboarding runs three conversations in order. Each one ends with a summary, and the summaries become the context for the next conversation. That is prompt chaining where each link is a dialogue.

```python
chats = [
    {
        "sender": onboarding_personal_information_agent,
        "recipient": customer_proxy_agent,      # human_input_mode="ALWAYS", llm_config=False
        "message": "Hello, I'm here to help you get started. Could you tell me your name and location?",
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Return the customer information as JSON: {'name': '', 'location': ''}"},
        "max_turns": 2,
        "clear_history": True,
    },
    {"sender": onboarding_topic_preference_agent, "recipient": customer_proxy_agent, ...},
    {"sender": customer_proxy_agent, "recipient": customer_engagement_agent, ...},
]
chat_results = initiate_chats(chats)
```

![Sequential chats for onboarding](../sources/images/wang-wu-autogen-patterns-fig2.png)

*Figure: sequential chats (AutoGen course, L2).*

Asking the summary step for JSON turns a free conversation into structured state for the next stage.

---

## L3 — reflection with nested chats

A writer drafts; a critic reviews. The critic does not review alone: each time the writer speaks, the critic runs a set of **nested chats** with specialist reviewers, then returns their combined feedback as its reply.

```python
def reflection_message(recipient, messages, sender, config):
    # pass the writer's latest draft to each reviewer
    return f"Review the following content.\n\n{recipient.chat_messages_for_summary(sender)[-1]['content']}"

review_chats = [
    {"recipient": SEO_reviewer,    "message": reflection_message, "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt": "Return review as JSON: {'Reviewer': '', 'Review': ''}"}, "max_turns": 1},
    {"recipient": legal_reviewer,  "message": reflection_message, ...},
    {"recipient": ethics_reviewer, "message": reflection_message, ...},
    {"recipient": meta_reviewer,   "message": "Aggregate feedback from all reviewers and give final suggestions.",
     "max_turns": 1},
]
critic.register_nested_chats(review_chats, trigger=writer)   # fires when writer speaks

writer.initiate_chat(recipient=critic, message=task, max_turns=2, summary_method="last_msg")
```

![Reflection with nested reviewer chats](../sources/images/wang-wu-autogen-patterns-fig3.png)

*Figure: reflection with nested chats (AutoGen course, L3).*

This is P18 Reflection with the critic split into roles. The book's guidance for reflection applies: a reviewer with a specific rubric beats "please improve this", and one or two rounds capture most of the gain.

**The same loop as a two-node graph.** Oshin and Campos build reflection from a `generate` node and a `reflect` node (*Learning LangChain*, ch. 7). One detail is easy to miss: `reflect` swaps the roles of every message after the first, so AI messages become human messages and the reverse. The critic model then thinks it is grading a user's essay, and its critique goes back to `generate` as a `HumanMessage`, as if the user had sent it. The swap is needed because dialogue-tuned models are trained on alternating human/AI turns. The loop then runs a fixed number of rounds:

```python
def reflect(state: State) -> State:
    swap = {AIMessage: HumanMessage, HumanMessage: AIMessage}
    flipped = [reflection_prompt, state["messages"][0]] + [
        swap[type(m)](content=m.content) for m in state["messages"][1:]
    ]
    critique = model.invoke(flipped)
    return {"messages": [HumanMessage(content=critique.content)]}

def should_continue(state: State):
    return END if len(state["messages"]) > 6 else "reflect"   # 3 rounds, ending on a draft

builder.add_edge(START, "generate")
builder.add_conditional_edges("generate", should_continue)
builder.add_edge("reflect", "generate")
```

There are two variants: let `reflect` decide when the draft is good enough, or add reflection as the last node of a tool-calling agent, at the price of more latency. The authors "strongly recommend" grounding the critique wherever possible. For code, run a linter or compiler before `reflect` and pass it the errors. That matches the P22 rule of sending execution errors back to the model ([02](02-tool-use-and-react.md#code-execution-instead-of-a-tool-list)).

---

## L4 — tool use inside a conversation

Two player agents play chess through a board proxy that owns the `python-chess` board. Each player has the tools `get_legal_moves()` and `make_move(move)`, registered with the player as caller and the board proxy as executor (see [02 — caller and executor](02-tool-use-and-react.md#caller-and-executor-are-different-agents)).

```python
board_proxy = ConversableAgent(
    name="Board Proxy",
    llm_config=False,                      # no LLM: it only executes tools
    is_termination_msg=check_made_move,    # nested chat ends once a legal move is made
    default_auto_reply="Please make a move.",
    human_input_mode="NEVER",
)

player_white.register_nested_chats(
    trigger=player_black,
    chat_queue=[{"sender": board_proxy, "recipient": player_white, "summary_method": "last_msg"}],
)
```

![Chess: players and a board proxy](../sources/images/wang-wu-autogen-patterns-fig4.png)

*Figure: conversational chess (AutoGen course, L4).*

The structure is worth copying: the outer chat is the social layer (players talk), the nested chat is the work layer (a player and the board negotiate a legal move). A variant adds chit-chat to the outer layer and marks the nested chats `"silent": True` so the tool traffic stays out of the outer transcript.

---

## L5 — coding agents

Covered in [02 — code execution](02-tool-use-and-react.md#code-execution-instead-of-a-tool-list). The multi-agent point: the code writer and the code executor are separate agents, and the executor runs with `human_input_mode="ALWAYS"` so a person approves each run.

![Coding agent with executor](../sources/images/wang-wu-autogen-patterns-fig5.png)

*Figure: code writer and executor (AutoGen course, L5).*

---

## L6 — planning with a group chat

Five agents share one conversation, and a manager picks who speaks next.

| Agent | Role | LLM? |
|---|---|---|
| Admin | the human; approves the plan and the report | no (`human_input_mode="ALWAYS"`) |
| Planner | breaks the task into steps that need information Python can get | yes |
| Engineer | writes code for the steps | yes |
| Executor | runs the code (`last_n_messages=3`, `use_docker=False`) | no |
| Writer | writes the blog post in Markdown | yes |

```python
groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, writer, executor, planner],
    messages=[],
    max_round=10,
    allowed_or_disallowed_speaker_transitions={
        user_proxy: [engineer, writer, executor, planner],
        engineer:   [user_proxy, executor],
        writer:     [user_proxy, planner],
        executor:   [user_proxy, engineer, planner],
        planner:    [user_proxy, engineer, writer],
    },
    speaker_transitions_type="allowed",
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
```

![Planning with a group chat](../sources/images/wang-wu-autogen-patterns-fig6.png)

*Figure: the financial-report group chat (AutoGen course, L6).*

Without the transition table, the manager LLM picks the next speaker from each agent's `description` alone, and it often picks badly (the writer starts before any data exists). The table turns free-for-all into a state machine with LLM choice only among legal moves. LangGraph makes that state machine the primary abstraction; see [04-agentic-frameworks](../../04-agentic-frameworks/README.md).

---

## Planning strategies

The Planner in L6 is one way to plan. Huang et al.'s survey of LLM-agent planning ([arXiv:2402.02716](https://arxiv.org/abs/2402.02716)), as summarized by Raieli and Iuculano, sorts the options by where each one fails (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 4):

| Strategy | How it works | Fails when |
|---|---|---|
| Decomposition first | Plan every subgoal up front, then execute ("Let's first devise a plan" / "Let's carry out the plan") | A step goes wrong mid-run: the plan can't be corrected |
| Interleaved | Decompose one subtask, solve it, decompose the next (ReAct is this) | The problem is hard: chains grow long and costly without reaching an answer |
| Multi-plan selection | Sample several plans and pick one by majority vote, tree search or RL | The budget is tight: generating many paths costs compute and time, and the stochastic choice is inconsistent |
| External planner | A symbolic or small neural planner finds the path; the LLM fixes the mistakes | You can't afford the engineering: complex to build |
| Reflection and refinement | Generate a plan, critique it (self or a separate evaluator), refine | No guarantee of convergence; it can loop |
| Memory-augmented | Store and recall past observations and outcomes in external memory to get past the context limit | The book names no failure mode; it inherits the weaknesses of retrieval |

**Plan-and-execute** separates planning from execution, with each handled by its own LLM call that sees the objective, the current task and the completed tasks. BabyAGI is the classic example. In a loop, an execution agent does the next task and stores the result in a vector database. A task-creation agent derives new tasks from the objective and that result. A prioritization agent reorders the task list against the objective (*Prompt Engineering for Generative AI*, ch. 6). The structure is also an injection defense: Plan-Then-Execute in [02](02-tool-use-and-react.md#prompt-injection-six-defenses) fixes the plan before untrusted data is read. BabyAGI regenerates tasks every cycle, so it gets the flexibility and loses that protection.

**Tree of Thoughts** (ToT, [arXiv:2305.10601](https://arxiv.org/abs/2305.10601)) is multi-plan selection with backtracking. On the Game of 24, GPT-4 with chain-of-thought solved 4% of problems; ToT solved 74% (*Prompt Engineering for Generative AI*, ch. 6). Koenigstein's cheap version uses two models: a small model proposes three options as structured output, and a stronger judge picks one. Clamp the judge's index in code, because structured output guarantees the type, not the range (*AI Agents: The Definitive Guide*, ch. 2):

```python
choice = judge_llm.with_structured_output(ChoicePayload).invoke(eval_prompt)
idx = max(0, min(choice.choice_index, len(opts) - 1))
```

She notes that this propose-and-judge pair can sometimes replace a full multi-agent design, with fewer calls to the large model.

---

## Letta: agents as services with shared memory

The Letta course (L6) takes a different approach. Each agent is a persistent service behind a REST API, with its own memory. Agents coordinate in two ways:

| Mechanism | How |
|---|---|
| Messaging | a tool `send_message_to_agent_and_wait_for_reply` |
| Shared state | the same memory block attached to both agents (`block_ids=[company_block.id]`) |
| Groups | `client.groups.create(agent_ids=[...])`: round-robin turn-taking |

```python
company_block = client.blocks.create(label="company", value="The company is called AgentOS ...", limit=10000)

eval_agent = client.agents.create(
    name="eval_agent",
    memory_blocks=[{"label": "persona", "value": eval_persona}],
    model="openai/gpt-4o-mini-2024-07-18",
    embedding="openai/text-embedding-ada-002",
    tool_ids=[reject_tool.id],
    tools=["send_message_to_agent_and_wait_for_reply"],
    include_base_tools=False,
    block_ids=[company_block.id],                         # shared with the outreach agent
    tool_rules=[{"type": "exit_loop",                     # stop after handing off
                 "tool_name": "send_message_to_agent_and_wait_for_reply"}],
)
```

![Multi-agent recruiting with a shared memory block](../sources/images/packer-wooders-agent-memory-fig8.png)

*Figure: evaluator and outreach agents sharing a company block (Letta course, L6).*

When the outreach agent is told "the company has rebranded to Letta", it edits the shared block, and the evaluator sees the new name on its next step. Shared memory replaces a whole round of messages. The memory mechanics are in [03](03-memory-as-an-operating-system.md#shared-memory-across-agents).

---

## Architectures (P23)

| Architecture | Shape | Use when |
|---|---|---|
| Hierarchical | an executive delegates to workers; prompt chaining is the simplest form | the task decomposes cleanly |
| Peer-to-peer | agents debate to consensus | you want diverse views on a judgement call |
| Market-based | agents bid for tasks (sealed-bid or English auction) | heterogeneous agents with different costs |
| Human-in-the-loop | a proxy agent routes conflicts to a person | high stakes, ambiguous decisions |

The LangGraph view of the same space names topologies by who decides what runs next (*Learning LangChain*, ch. 7):

![Multi-agent topologies: single agent, network, supervisor, supervisor with agents as tools, hierarchical, custom](../sources/images/learning-langchain-fig7-3.png)
*Image Source: Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025), Fig. 7-3*

| Topology | Who picks the next agent |
|---|---|
| Network | Any agent can call any other |
| Supervisor | One supervisor agent. A special case makes the subagents its tools. |
| Hierarchical | Supervisors of supervisors |
| Custom | Parts of the flow are fixed edges; only some agents choose |

The supervisor is a structured-output call: `next: Literal["researcher", "coder", "FINISH"]`, read by a conditional edge. The router sees only the agents' names unless you add descriptions, so `agent_1` and `agent_2` give it nothing to decide with. Two design choices follow. The first is whether subagents share one `messages` list, so each sees the others' work, or are subgraphs that keep their own state and return only a summary. The second is whether each subagent returns to the supervisor or decides for itself to answer the user. The authors' own caveat: reflection and multi-agent "shouldn't be the first thing you reach for". Start with the single agent of [02](02-tool-use-and-react.md). (Their Python listing has bugs. `AgentState` declares only `next`, yet the nodes return `messages`, and `"FINISH"` is never mapped to `END`. The JavaScript version maps it.)

Koenigstein builds three of these in LangGraph and compares them (*AI Agents: The Definitive Guide*, ch. 2):

| Architecture | Use when | Benefits | Trade-offs |
|---|---|---|---|
| Supervisor | Small teams with clear task boundaries | Simple; strong control; avoids deadlocks | Central bottleneck; single point of failure |
| Hierarchical | Multi-team workflows that must scale | Modular; mirrors an org chart | Harder to debug; needs careful design |
| Swarm | Peers handing work back and forth (researcher ↔ writer) | Flexible, natural back-and-forth | Less predictable; needs robust handoff design |

Her runs show the cost profile, but on different tasks. The hierarchical team wrote a whitepaper in about two minutes with `recursion_limit=150`. The swarm produced three cited bullet points in about 30 seconds. Don't read that as swarm being faster. Swarm handoffs use `create_handoff_tool`, which by default passes the **full message history** to the next agent. Filter it, or every handoff grows the context.

Raieli and Iuculano's single- vs multi-agent comparison (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 11; the book's caption for this table is wrong):

| | Single agent | Multi-agent |
|---|---|---|
| Cost | Lower: fewer inference steps | Higher: more agents, LLM calls and tool use |
| Latency | Lower | Higher: inter-agent communication |
| Fault tolerance | One failure breaks the system | Failures can be contained in one agent |
| Modularity | Monolithic | Agents added or replaced independently |
| Scalability | One agent handles all logic | Parallel agents |
| Communication overhead | None | Significant: explicit messaging |
| Interpretability | One decision chain | Distributed reasoning is harder to follow |

Albada adds the cost driver: agents spend tokens sharing context and coordinating, so a multi-agent system often uses more tokens for the same task (*Building Applications with AI Agents*, ch. 2).

Use cases from the book, roughly from least to most complex: parallel breadth-first work (the most common), multistep pipelines, collaborative content, complex reasoning, adversarial verification (red team / blue team), domain integration, self-improving systems.

---

## Why multi-agent systems fail

Cemri et al. (2025) found 40–80% of tasks fail in the multi-agent systems they studied, and sorted 14 failure modes into three groups:

| Category | Examples |
|---|---|
| Specification issues | ignoring the role or task spec, repeating steps, losing context, not recognising completion |
| Inter-agent misalignment | conversation resets, not asking for clarification, derailment, withholding information, ignoring other agents, reasoning that does not match action |
| Task verification | missing or weak checks, premature termination |

The taxonomy comes from expert annotation of about 150 conversation traces, each averaging over 15,000 lines. No single cause dominates: failures spread across all three categories, and they are correlated. A bad architecture, for example, causes inefficient communication downstream, so fixing one mode rarely fixes the system (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 11).

The book adds that coordination overhead grows faster than the number of agents, consistency across agents is hard, and errors compound along a chain. Its advice: if UX design, a human in the loop or adjusted expectations let a single agent do the job, use a single agent. The production view (subagents as context firewalls, when not to go multi-agent) is in [harness 07 — orchestration](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md) and [context 10 — tools and multi-agent](../../../ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent.md).

| Rule | Why |
|---|---|
| Always set a turn cap and a semantic stop | Agents rarely stop on their own |
| Restrict who can speak after whom | Free speaker selection derails |
| Summarize between stages, as JSON when possible | Keeps the next stage's context small and parseable |
| Give reviewers a rubric | Generic critique adds little |
| Prefer shared state to chatter for facts | One block edit beats N messages |
| Start with one agent | Most failures are coordination failures |

"Start with one agent" holds even for a workflow you have already designed as multi-agent, provided every role runs on the same model. Xu et al. ([arXiv:2601.12307](https://arxiv.org/abs/2601.12307), 2026-01) executed such homogeneous workflows as one agent role-playing each step over successive turns, so the shared prefix stays in the KV cache. With GPT-4o-mini as executor, accuracy held (HumanEval 92.1% vs. 91.6% multi-agent; MBPP 81.4% vs. 81.1%) and cost fell (an AFlow workflow on HotpotQA: $0.53 vs. $1.44), though HotpotQA accuracy did drop, 68.4% vs. 72.1%. The closed-model savings are a simulated KV-cache cost, not a billed one, and the trick can't reproduce a workflow that mixes models; in their tests a GPT-4o-mini + Haiku mix was largely bounded by the best single-model workflow anyway.

---

## Interview questions

| Question | Short answer |
|---|---|
| Name Ng's four agentic patterns | Reflection, tool use, planning, multi-agent collaboration |
| What is a nested chat for? | Running a sub-conversation (reviewers, a tool executor) behind one agent's reply |
| How do you stop a group chat from derailing? | Speaker-transition rules, turn caps, a human approver |
| Why do multi-agent systems fail? | Bad specs, misaligned agents, weak verification (Cemri 2025) |
| Messages vs shared memory? | Messages for requests; shared blocks for facts every agent needs |
| Why does a reflection node swap human and AI roles? | Dialogue-tuned models expect alternating turns; the critic must see the draft as user input, and the generator must see the critique as user feedback |
| Supervisor, hierarchical or swarm? | Supervisor for small teams (bottleneck, but no deadlocks); hierarchical for many teams (harder to debug); swarm for peer back-and-forth (needs careful handoffs) |
| Decomposition-first vs interleaved planning? | Up-front plans can't correct mid-run errors; interleaved plans adapt but can run long and costly on hard problems |

→ Next: [05 — framework survey](05-framework-survey.md) — the same patterns in AutoGen, CrewAI, LangGraph, ADK, the OpenAI Agents SDK, smolagents and Letta, plus MCP and A2A.
