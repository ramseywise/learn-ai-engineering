---
origin: notion-export
confidence: medium
sources:
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://openai.com/index/harness-engineering/
  - https://interloom.com/en/blog/harness-engineering-matching-agents-to-work/
cleaned: 2026-07-17
---

Harness comprises at least four parts: acceptance baseline, execution boundary, feedback signals, and rollback mechanisms.

Agent = Model + Harness. 

https://www.langchain.com/blog/the-anatomy-of-an-agent-harness

https://openai.com/index/harness-engineering/

https://interloom.com/en/blog/harness-engineering-matching-agents-to-work/

#### tips/ summaries:

- **Break down complex objectives:** Planning tools let agents decompose tasks, track progress, and adapt as they learn
- **Delegate work in parallel:** Spawn subagents for independent subtasks, each with isolated context
- A well-configured environment, the right tools, durable state, and verification loops make any model more efficient regardless of its base intelligence.
- **The model contains the intelligence and the harness is the system that makes that intelligence useful.**

Concretely, **a harness includes things like:**

- System Prompts/ context policies
- Tools, Skills, MCPs + and their descriptions
- Bundled Infrastructure (filesystem, sandbox, browser)
- Orchestration Logic (subagent spawning, handoffs, model routing, feedback loops(HITL))
- Hooks/Middleware for deterministic execution (compaction, continuation, lint checks)
- Recovery path ‣
    
    *(missing diagram — not exported from Notion)*
    

need for harness:  things that is out of the box of models, like: Maintain durable state across interactions, Execute code, Access realtime knowledge, Setup environments and install packages to complete work

**Behavior we want (or want to fix) → Harness Design to help the model achieve this.**

*(missing diagram — not exported from Notion)*

It's a **configuration problem**.

1. **Filesystems for Durable Storage and Context Management: agents to have durable storage to interface with real data, offload information that doesn't fit in context, and persist work across sessions.**
    
    **Harnesses ship with filesystem abstractions and tools for fs-ops.**
    
2. **Bash + Code as a General Purpose Tool**
    
    **We want agents to autonomously solve problems without humans needing to pre-design every tool. Harnesses ship with a bash tool so models can solve problems autonomously by writing & executing code.**
    
3. **Sandboxes and Tools to Execute & Verify Work**
    
    Sandboxes give agents safe operating environments to safely act, observe results, and make progress.
    
    Tools like browsers, logs, screenshots, and test runners give agents a way to observe and analyze their work. This helps them create **self-verification loops where** they can **write application code,** run tests, inspect logs, and fix errors.
    
    Deciding where the agent runs, what tools are available, what it can access, and how it verifies its work are all harness-level design decisions.
    
4. **Memory & Search for Continual Learning**
    
    **Agents should remember what they've seen and access information that didn't exist when they were trained(context injection). —> see infor from other pages** 
    
    RAG/ AGENT.md/ MCP / Web Search / skills(?)
    
5. maintaining performance over long context — context/ memory management —> for more infor, see other pages 
    
    
    **Compaction** addresses what to do when the context window is close to filling up.  So compaction intelligently offloads and summarizes the existing context window so the agent can continue working.
    
    **Tool call offloading** helps reduce the impact of large tool outputs that can noisily clutter the context window without providing useful information. The harness keeps the head and tail tokens of tool outputs above a threshold number of tokens and offloads the full output to the filesystem so the model can access it if needed.
    
    **progressive disclosure — Skills** address the issue of too many tools or MCP servers loaded into context on agent start which degrades performance before the agent can start working. 
    
6. **Long Horizon Autonomous Execution - loop engineering…** https://www.langchain.com/blog/the-art-of-loop-engineering & Loop Engineering  
    
    **agents to complete complex work, autonomously, correctly, over long time horizons.**
    
    Long-horizon work requires durable state, planning, observation, and verification to keep working across multiple context windows.
    
    **Planning and self-verification to stay on track.**  Planning is when a model decomposes a goal into a series of steps.  Harnesses support this via good prompting and injecting reminders how to use a plan file in the filesystem.  After completing each step, agents benefit from the checking correctness of their work via **self-verification.**  Hooks in harnesses can run a pre-defined test suite and loop back to the model on failure with the error message or models can be prompted to self-evaluate their code independently.  Verification grounds solution in tests and creates a feedback signal for self-improvement.
    
    *(missing diagram — not exported from Notion)*
    

some Qs need to be explored: 

- orchestrating hundreds of agents working in parallel on a shared codebase
- agents that analyze their own traces to identify and fix harness-level failure modes
- harnesses that dynamically assemble the right tools and context just-in-time for a given task instead of being pre-configured

**A decent model with a great harness beats a great model with a bad harness.**

*Harness engineering treats that scaffolding as a real artifact, and it tightens every time the agent slips.*

Roughly: anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again.

*(missing diagram — not exported from Notion)*

some components to achieve harness engineering: 

**hooks** for automated integration and deterministic control flow

**skills** for progressive disclosure of knowledge. (Dex likes to refer to them as "Instruction Modules" - more on this in another post.)

subagent: When working on hard problems that require many, many context windows to solve, **sub-agents are the key to maintaining coherency across many sessions**. Sub-agents **function as a "context firewall"** that ensures discrete tasks can run in isolated context windows so none of the intermediate noise accumulates in your parent thread which is responsible for orchestration, and you can maintain coherency for much, much longer.

*(missing diagram — not exported from Notion)*

### https://openai.com/index/harness-engineering/

1. **progressive disclosure**
    1. Content invisible to the Agent is essentially non-existent: Knowledge must reside within the codebase itself. External documentation is invisible to running Agents. `AGENTS.md` retains only about 100 lines as an index, with details broken down into various `docs` directories for on-demand referencing.
        1. no one big `AGENTS.md`⁠(opens in a new window)” approach. Treat AGENTS.md as **the table/ map of contents**.
        
        ```markdown
        AGENTS.md
        ARCHITECTURE.md
        docs/
        ├── design-docs/
        │   ├── index.md
        │   ├── core-beliefs.md
        │   └── ...
        ├── exec-plans/
        │   ├── active/
        │   ├── completed/
        │   └── tech-debt-tracker.md
        ├── generated/
        │   └── db-schema.md
        ├── product-specs/
        │   ├── index.md
        │   ├── new-user-onboarding.md
        │   └── ...
        ├── references/
        │   ├── design-system-reference-llms.txt
        │   ├── nixpacks-llms.txt
        │   ├── uv-llms.txt
        │   └── ...
        ├── DESIGN.md
        ├── FRONTEND.md
        ├── PLANS.md
        ├── PRODUCT_SENSE.md
        ├── QUALITY_SCORE.md
        ├── RELIABILITY.md
        └── SECURITY.md
        ```
        
        b. Plans are treated as first-class artifacts. Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans⁠(opens in a new window) with progress and decision logs that are checked into the repository. Active plans, completed plans, and known technical debt are all versioned and co-located, allowing agents to operate without relying on external context.
        
2. **Enforcing architecture and taste:** 
    1. Constraints are encoded, not documented: Specifications written in documentation are easily overlooked. Constraints encoded into Linters, type systems, or CI rules are enforceable. Architectural layering is mechanically enforced by custom Linters, not by manual review.
    2. **By enforcing invariants, not micromanaging implementations, we let agents ship fast without undermining the foundation.** 
3. Agents autonomously complete tasks end-to-end: From verifying the current state, reproducing bugs, implementing fixes, driving application verification, to opening PRs, handling review feedback, and autonomous merging, the entire chain requires no human intervention. Checking logs, metrics, and traces are all proactively handled by the Agent.
4. Minimizing merge resistance: Occasional test failures are handled by rerunning instead of blocking progress. In high-throughput environments, the cost of waiting for manual review is often higher than the cost of fixing small errors. The discipline of writing code hasn't disappeared; it's just that it's transformed from manual review to machine-executed constraints—written once, effective everywhere.

## Salvaged from table_of_contents.md (Notion): OpenClaw harness tips (10 principles)


tips: 

1. The core of an agent is a stable loop of perception, decision-making, action, and feedback. The control flow remains largely unchanged; new capabilities are primarily achieved through tool extensions, adjustments to the prompt structure, and externalization of state.
2. Harness, encompassing acceptance baselines, execution boundaries, feedback signals, and rollback mechanisms, often determines system convergence more significantly than the model itself. High-quality automated verification and clear objectives are indispensable.
3. Context engineering focuses on preventing Context Rot. This is achieved through layered management of persistent information, on-demand knowledge, runtime information, and memory, coupled with sliding windows, LLM summarization, tool result replacement, and skill lazy loading to stabilize signal quality.
4. Tool design follows ACI principles: it should be agent-oriented, not API-oriented, with clear boundaries, error-proof parameters, and direct examples in the definition. During debugging, prioritize checking the tool description rather than questioning the model's capabilities.
5. Memory can be categorized into working memory, procedural memory, contextual memory, and semantic memory. MEMORY.md, on-demand retrieval, and rollbackable integration are crucial for maintaining consistency across sessions.
6. Stable operation of long-running tasks relies on state externalization. The Initializer Agent transforms the task into a file system state, the Coding Agent is reentrant in a loop, and progress is passed via files, independent of context windows.
7. For multiple agents, a task graph and isolation boundaries must be established before introducing parallelism. Protocols precede collaboration, and sub-agents only return summaries, keeping search and debugging details within their own contexts.
8. In evaluation, Pass@k verifies capability boundaries, and Pass^k ensures deployment quality. If the evaluation system has issues, fix the evaluation system first before affecting the agents; do not adjust direction based on distortion signals.
9. For observability, traces are a prerequisite for troubleshooting. Event streams form the foundation for single-distribution multi-consumption, with manual annotation and calibration followed by automatic LLM scoring; both layers should be used together.
10. OpenClaw incorporates these principles into a workable system. The real key to agent stability lies not in more complex loops, but in engineering details such as message decoupling, state externalization, layered hints, memory integration, and security boundaries.

