---
origin: notion-export
confidence: medium
sources:
  - https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google
cleaned: 2026-07-17
---

https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google

https://notebooklm.google.com/notebook/25cb1710-ae04-4a99-9c1a-b6c2a4fdbb11

### Schedule:

- **Day 1: Introduction to Agents & Vibe Coding** Level up from AI chatbots and text completion to autonomous agents. Master vibe coding workflows where natural language is the primary programming interface.
- **Day 2: Agent Tools & Interoperability** Explore unlimited capabilities by integrating external APIs, code execution, and agent to agent communication.
- **Day 3: Agent Skills** Build personalized agents with long-term memory and state. Master strategies for long context and optimal token use and building skills with agents to integrate into agentic frameworks.
- **Day 4: Vibe Coding Agent Security and Evaluation** Develop reliable agents by implementing rigorous testing, guardrails, and quality evaluations. Secure agents against new threat vectors.
- **Day 5: Spec-Driven Production Grade Development in the Age of Vibe Coding** Graduate your local agents into a governed, scalable, and observable production-ready fleet. Master cloud deployment, debugging, and observability.

# Day 1 Introduction to Agents & Vibe Coding

1. Complete Unit 1 – "Introduction to Agents & Vibe Coding"
    - Listen to the summary podcast (https://www.youtube.com/watch?v=cbzmr7vt4XA) episode for this unit.
    - To complement the podcast, read "The New SDLC with Vibe Coding” whitepaper (https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding).
    - Complete these codelabs on Kaggle:
        - Get started with Antigravity 2.0 and IDE (https://codelabs.developers.google.com/getting-started-google-antigravity#0)
        - Build a Web Application in AI Studio and Deploy to Cloud Run (https://codelabs.developers.google.com/deploy-from-aistudio-to-run?hl=en#0)

![Vibe-coding stakes spectrum — prototype vs production](../images/adk-vibe-coding-stakes-spectrum.png)

The right position on this spectrum depends on the stakes. A weekend prototype
can be pure vibe coding. A production API handling financial transactions demands
agentic engineering. Most real work falls somewhere in between, and the skill is
knowing where to draw the line for each task.

**in agentic engineering: how to eval code:** 
a. Tests verify the deterministic parts of the system: a function given this input produces that output. 

b. Evaluations, or evals, verify the parts that are not deterministic: did the agent take the right trajectory of steps, choose the right tools, and produce a final response that meets the quality bar.

Context engineering: providing AI agents with rich, structured information about your codebase, architecture, conventions, and intent. 

six primary types of context:
• Instructions: The agent's core role, goals, and operational boundaries.
• Knowledge: Retrieved documents, architectural diagrams, and domain-specific data.
• Memory: Short-term session logs (what just happened) and long-term persistent state
(what the project is).
• Examples: Few-shot behavioral demonstrations and codebase reference patterns.
• Tools: The precise definitions of the APIs, scripts, and external services the agent
can invoke.
• Guardrails: Hard constraints, formatting rules, and safety validations.

**2 contexts:** 

![Static vs dynamic context](../images/adk-static-vs-dynamic-context.png)

managing dynamic context: skills

### The new software development life cycle -**SDLC Phase Transformations**

![SDLC phase transformations with agents](../images/adk-sdlc-phase-transformations.png)

**What will remain constant is human judgment, taste, and the skill to verify AI
output as the machines take on more of the implementation.**

- **Requirements and Planning**: Traditionally a manual process, this phase now involves interactive AI conversations that simultaneously generate user stories, API schemas, and working prototypes, dramatically collapsing feedback loops.
- **Design and Architecture**: While humans still make critical trade-off decisions, AI is used to scaffold entire applications and ensure new modules conform to established conventions once the structural path is set.
- **Implementation**: This phase moves from a "writing" task to a "reviewing and guiding" task. Agents can generate multi-file features, but developers must spend significant time verifying and debugging the output.
- **Testing and Quality Assurance**: Testing becomes the primary way to communicate intent to an agent. Evaluation shifts to include both **Output Evaluation** (final code correctness) and **Trajectory Evaluation** (the reasoning steps the agent took).**56**
- **Code Review and Deployment**: AI acts as a first-pass reviewer for security and style, while deployment pipelines become "AI-aware," using agents to monitor health and predict risks or perform automatic rollbacks.
- **Maintenance and Evolution**: AI makes legacy codebases accessible by understanding impenetrable patterns and automating tedious tasks like framework migrations or updating deprecated APIs.

![New SDLC lifecycle stages](../images/adk-sdlc-lifecycle-stages.png)

### **Tips for Navigating the New SDLC**

- **Define Specs Early**: Treat specifications as your contract with the AI; a well-defined eval suite communicates intent more precisely than natural language prompts.
- **Monitor the "Trajectory"**: Don't just check if the final code works; verify *how* the agent got there to ensure it didn't skip critical verification steps or use insecure methods.
- **Design the "Factory," Not the Code**: Move from being an implementor to a "factory manager" by designing the systems (guardrails, tests, and context) that produce the code.
- **Beware the "80% Problem"**: AI can rapidly generate 80% of a feature, but the remaining 20% (edge cases and complex logic) requires deep human expertise.
- **Use "Agent Skills"**: To save on costs and avoid "context rot," use portable "skills" that load specific instructions only when a task requires them.
- **Invest in the "Harness"**: Recognize that most agent failures are configuration failures; focus on improving your tools, prompts, and guardrails (the harness) rather than just blaming the model. → next section ⬇️

### Harness: Agent = model + harness

![Agent = model + harness](../images/adk-agent-model-plus-harness.png)

it includes: 

*(missing diagram — `Screenshot 2026-06-15 at 22.29.31.png` not exported from Notion)*

Harness in SDLC: 

1. Requirements, Planning, & Architecture (Configuring
the Harness)
    1. Harness Configuration: Providing the Instructions and Rule Files (e.g., creating the
    AGENTS.md and defining architectural constraints)
    2. developer’s work:
        1. set up the agent's environment
        2. defines the tools the agent will have access to (like specific
        APIs or database schemas) and sets the fundamental rules the agent cannot break.
2. Implementation (Running the Harness)
    1. Harness Components Used: Sandboxes(code generation/excution environment), Execution Environments, and Tools(e.g. agent reads files/ search on the web).
3. Testing & QA (The Feedback Loop)
    1. harness Orchestration Logic and Guardrails.
    2. 'think -> act -> observe' loop.”: execute code — error captured — loop back to model — try again 
4. Code Review, Deployment, & Maintenance (Observing the Harness)
    1. harness hooks and observability 
    2. runs deterministic hooks 
    3. observability layer tracks token costs, latency, and agent drift, allowing human engineers to audit exactly why an agent made a specific deployment decision.

The developer's evolving role: conductors and orchestrators

*(missing diagram — `Screenshot 2026-06-15 at 22.37.44.png` not exported from Notion)*

The conductor: hands-on, real-time direction 

when working on complex logic, debugging tricky issues, or working in unfamiliar codebases where the developer needs to understand each change as it's made.

The orchestrator: async, multi-agent delegation

for well-defined tasks like bug fixes, feature implementations against established patterns, codebase migrations, and test generation.

requires a different skill set:

Specification: Defining tasks precisely enough that an agent can execute them without ambiguity
Decomposition: Breaking large tasks into appropriately sized units for agent execution
Evaluation: Quickly assessing whether agent output meets quality standards
System design: Designing the constraints, tests, and feedback loops that keep
agents productive

### The 80% problem:

AI agents can rapidly generate approximately 80% of the code for a feature, but the remaining 20%: **the edge cases, error handling, integration points, and subtle correctness requirements** - demands deep contextual knowledge that current models often lack

### The Economics of AI Development — why agentic engineering is important

the critical metric is the Total Cost of Ownership (TCO).

operational burdens between Capital Expenditure (CapEx)— the upfront investment to build something—and Operational Expenditure (OpEx)—the ongoing cost to run, fix, and maintain it.

*(missing diagram — `Screenshot 2026-06-15 at 22.50.05.png` not exported from Notion)*

# Day 2 Agent Tools & Interoperability

- Listen to the summary podcast (https://www.youtube.com/watch?v=GjjKXqxFTOY) episode for this unit.
- To complement the podcast, read "Agent Tools & Interoperability” whitepaper (https://www.kaggle.com/whitepaper-agent-tools-and-interoperability)
- Complete these codelabs on Kaggle:
- Get started with Antigravity CLI (https://codelabs.developers.google.com/antigravity-cli-hands-on#0)
- Explore Google Developer Knowledge MCP server in Google Antigravity (https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity)

What You’ll Learn
Today's whitepaper talks about standardizing the plug-and-play AI ecosystem using open protocols to eliminate the complex technical debt of custom tool integrations. It details how the Model Context Protocol (MCP) connects models to data sources, outlines Agent2Agent (A2A) collaboration, showcases Agent-to-User Interface (A2UI) for generative UI, and introduces Agent Payments Protocol (AP2) and Universal Commerce Protocol (UCP) for secure machine-to-machine commerce.
In today's codelabs, you'll learn how to add MCP servers to Antigravity, giving it access to the canonical, machine-readable source of Google's public developer documentation. You'll then extend your familiarity with Antigravity by using it via the terminal with Antigravity CLI.

Software's next evolution isn't written: it's orchestrated by interoperable agents.

MCP, A2A, A2UI, AP2, and UCP are the Industry Standards—the uniform nuts and bolts and screw sizes, data formats, and communication channels—that allow your machinery to safely interact with the rest of the world.

*(missing diagram — `Screenshot 2026-06-16 at 16.00.44.png` not exported from Notion)*

MCP tips: 

Discovery: always consider security as a first priority,

public community servers do not pass credentials, consider using services like Model Armor to avoid security issues.

config: 
Check for pre-requisites
Identify scope, access criterias
Include the specifications in the coding agent
Authentication

# Day 3 Agent Skills

Complete Unit 3 - “Agent Skills”:

- Listen to the summary podcast (https://www.youtube.com/watch?v=uYURYHhpmKc) episode for this unit.
- To complement the podcast, read the “Agent Skills” whitepaper: https://www.kaggle.com/whitepaper-agent-skills
- Complete these codelabs:
- Explore how Skills work in Antigravity: https://codelabs.developers.google.com/getting-started-with-antigravity-skills?hl=en#4
- Build agents in Antigravity with Agents CLI and ADK: https://codelabs.developers.google.com/agents-cli-adk-lifecycle

What You’ll Learn
Today's whitepaper talks about managing dynamic context and avoiding "context rot" by equipping agents with portable "Agent Skills", directories structured around a central SKILL.md file. It explains how this framework uses progressive disclosure to keep system prompts lightweight, loading execution details and tools only on demand so that single agents can flex into hundreds of specialist roles efficiently.
In the codelabs, you will familiarize yourself with skills in Antigravity. Then, using Antigravity, you will install and use Agents CLI skills to create agents, lint your code, and test your agent, all by using natural language prompts.

Claude Code skill course notes: ‣ 

too much context —> attention dilution

The challenge is not giving the model more information. The challenge is giving it the right information at the right time. 

need —> progressive disclosure —> skills 

Skill compontents:
Must: `skill.md` : name, description, activation criteria, instructions , usage guidance

Optional: some folders: 

1. Scripts Folder: executable code/ deterministic logic 
2. References Folder: Large domain knowledge stays outside the prompt until needed. → PDFs, manuals, tax rules, compliance documentation
3. Assets Folder: JSON schemas, templates, email formats, structured resources

Skills vs MCP vs agent.md：

MCP gets data/ API/ platforms 

Skills tell the agent what to do.

agent.md: Global instructions. always loaded 

Why Multi-Agent Systems Are Losing Favor:

Previous: Large orchestration complexity.

Now: One general-purpose agent can dynamically load skills. — deployment/ memory stores / routing complexity / maintenance
