# System Design Round — Sources

## Internal (this repo + workspace)

| Source | What it covers | Path |
|--------|---------------|------|
| System design study guide | The method: 5-step process, trade-off narration, reference architecture, bottleneck tables | [guides/9-system-design](../../guides/9-system-design/interview-guide.md) |
| RAG study guide | Pipeline components, architecture menu (9 patterns), latency budgets, eval | [guides/3-rag](../../guides/3-rag/interview-guide.md) |
| Agents study guide | Workflow patterns, tool design (ACI), harness engineering, loop engineering, multi-agent | [guides/4-agents](../../guides/4-agents/interview-guide.md) |
| Context & cost study guide | Context engineering, token economics, caching, cost optimization | [guides/5-context-cost](../../guides/5-context-cost/interview-guide.md) |
| Evals & observability study guide | Grader types, trajectory vs outcome, three-tier taxonomy, trace architecture | [guides/6-evals-observability](../../guides/6-evals-observability/interview-guide.md) |
| Security & safety study guide | Threat model, defense stack, source-sink analysis, compliance | [guides/7-security-safety](../../guides/7-security-safety/interview-guide.md) |
| Data eng & MLOps study guide | Pipeline design, feature stores, model serving, CI/CD for ML | [guides/8-data-eng-mlops](../../guides/8-data-eng-mlops/interview-guide.md) |
| Case interview notes | Process framework, trade-off types, bottleneck/failure tables, vantage-point framing | [notes/case-interview.md](../../notes/case-interview.md) |
| Agent harness notes | Harness anatomy, OpenClaw 10 principles, enforcement > documentation | [notes/agent-harness.md](../../../ai-engineering/03-harness/agent-harness.md) |
| Reliable agents notes | PRINCE case study: agentic RAG, error recovery, context engineering, eval | [notes/reliable-agents.md](../../../ai-engineering/03-harness/reliable-agents.md) |
| RAG notes | 9 architecture patterns, production checklist, component trade-offs | [notes/rag.md](../../../generative-ai/02-rag-retrieval/rag.md) |
| Eval harness notes | Golden set design, grader calibration, regression vs capability | [notes/eval-harness.md](../../../ai-engineering/06-eval/eval-harness.md) |

### Librarian wiki (query via `search_wiki`)

**System design drills**

| Page | Design topic |
|------|-------------|
| System Design — Shared Code-Index Service | Centralized indexer + query API, MCP as thin client, single-writer risk, pgvector |
| System Design — Unified Eval Harness | Golden set, two-tier grading, threshold governance, regression vs capability |
| System Design — Serverless Agent Backends | Stateless invocations, session state in Postgres, streaming within platform timeouts |

**Architecture & orchestration**

| Page | Design topic |
|------|-------------|
| Orchestration Architecture Decision | LangGraph vs ADK vs direct API — decision framework |
| RAG Retrieval Strategies | Hybrid search, RRF, reranking, query rewriting |
| Agentic RAG — Advanced Patterns | CRAG, Self-RAG, adaptive RAG, fusion RAG |
| Multi-Agent Orchestration Patterns | Fan-out, delegation, isolation boundaries |
| Semantic Cache Pipeline | Prefix + semantic caching, cache invalidation |
| Prefix Caching | Claude-specific: 90% latency/cost reduction on cached prefixes, 5-min TTL, byte-identical requirement |

**Observability & tracing**

| Page | Design topic |
|------|-------------|
| Langfuse Platform | Trace architecture, LLM-as-judge scoring, cost tracking, prompt management |
| Observability — Langfuse vs Langsmith | Platform comparison: self-hostable vs LangChain-native, data residency, HITL, cost |
| Observability Runtime Patterns | Two-layer tracing (auto + manual decorators), RAG path tagging, retrieval quality scores |
| Langfuse ADK Tracing Patterns | ADK-specific: auto-instrumentation + @observe, session grouping, error marking |
| Observability Glossary | Three pillars (traces/logs/metrics), Datadog vs Langfuse split, tracking ⊃ tracing |
| ADK Observability | ADK-specific tracing patterns, monitoring signals, checkpointer alignment |

**Production & deployment**

| Page | Design topic |
|------|-------------|
| Production Hardening Patterns | Embedder warmup, retries, fallbacks, state persistence, circuit breakers, model pinning |
| Cloud Run + Cloud SQL Pattern | Single-worker constraint, memory/CPU sizing, min-instances, concurrency ceiling |

### Workspace references (design decision frameworks)

| Source | What it covers | Path |
|--------|---------------|------|
| Archetype selection | 4 project archetypes (information retrieval, doc gen, workflow automation, conversational), complexity tiers | `ai-project-template` reference |
| Deployment topology | 5 topologies (local → serverless), cost/ops trade-offs, decision criteria | `ai-project-template` reference |
| Integration patterns | 5 patterns (MCP, Composio, Direct API, Webhooks, n8n), when to use each | `ai-project-template` reference |
| Data pipeline patterns | 4 patterns (batch, event-driven, streaming, hybrid), freshness vs complexity | `ai-project-template` reference |
| Support agents architecture | 5-layer guardrails, 3-framework comparison, grounding methodology, invocation flow | `playground/docs/support-agents/` |
| Atlas agents | Forecast (self-learning loop), Segmentation (HDBSCAN + LLM naming), Knowledge (Neo4j + explanation) | `atlas/` |
| PM-AI scoping | Meeting capture, typed fact extraction, lifecycle state machine, sole-writer pattern | `dssg/.claude/docs/scoping/project-mgmt-ai.md` |

### Images

- [Case interview evaluation dimensions](../../images/case-interview-evaluation-dimensions.png)
- [9 RAG architectures](../../images/9-rag-architectures.png)

## External

### Interview prep

| Source | Focus | Link |
|--------|-------|------|
| Complete Agentic AI System Design Interview Guide 2026 | Agent architecture, orchestrator, tool layer, memory, guardrails | [Medium/TechEon](https://atul4u.medium.com/the-complete-agentic-ai-system-design-interview-guide-2026-f95d0cfeb7cf) |
| GenAI System Design Interview Guide 2026 | RAG pipeline design, trade-off reasoning, end-to-end flow | [systemdesignhandbook.com](https://www.systemdesignhandbook.com/guides/generative-ai-system-design-interview/) |
| Evaluating AI Engineers for Multi-Agent Systems | What interviewers look for at senior/staff level, failure modes, war stories | [PromptLayer blog](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/) |
| ML System Design Interview — Exponent | 6-step framework, common mistakes, example walkthrough | [tryexponent.com](https://www.tryexponent.com/blog/machine-learning-system-design-interview-guide) |
| IGotAnOffer — ML System Design | Process, examples, common pitfalls | [igotanoffer.com](https://igotanoffer.com/en/advice/machine-learning-system-design-interview) |
| AI Engineering Field Guide — System Design | Open-source question bank with answer structures | [GitHub](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/04-ai-system-design.md) |

### Deep dives

| Source | Topic | Link |
|--------|-------|------|
| PRINCE case study (Fowler blog) | Production agentic RAG: context engineering, harness engineering, eval, recovery | [martinfowler.com](https://martinfowler.com/articles/reliable-llm-bayer.html) |
| Anthropic — Building Effective Agents | 5 workflow patterns, when to add agency, tool design | [anthropic.com](https://anthropic.com/engineering/building-effective-agents) |
| OpenAI — Harness Engineering | Progressive disclosure, enforcement > documentation, plans as artifacts | [openai.com](https://openai.com/index/harness-engineering) |
| Google eng-practices | General code/system design review standards | [google.github.io](https://google.github.io/eng-practices/) |

## Practice material

- **Three drill systems** in the librarian wiki (shared indexer, eval harness, serverless agents) — rehearse as full spoken 45-min answers
- **Classic prompts**: support chatbot for a bank, document-QA at 10K→1M docs, code-assistant for private enterprise code, feed/notification ranking
- **Portfolio systems**: review your own deployed projects — designs you've actually built beat memorized generic ones
