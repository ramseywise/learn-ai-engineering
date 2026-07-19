# System Design Round — Worked Examples

Each file walks through a full system design using the five-step process from the [study guide](../study-guide.md). Practice by attempting the design yourself first (40-min timer), then compare.

## Real systems (portfolio case studies)

| System | File | Prompt | Key topics |
|--------|------|--------|------------|
| Customer support agent | [support-agent.md](support-agent.md) | "Design a help center agent with citation enforcement and human escalation" | 5-layer guardrails, CRAG, multi-framework comparison, grounding |
| Financial forecasting | [forecasting-agent.md](forecasting-agent.md) | "Design a self-learning cash flow forecasting system" | Classical ML + LLM hybrid, agentic self-learning loop, knowledge graph, dynamic segmentation |
| Meeting intelligence | [meeting-processor.md](meeting-processor.md) | "Design a meeting capture → typed fact extraction → lifecycle state machine" | Event-driven pipeline, sole-writer state machine, multi-tenant, template-rendered architecture |
| Accounting assistant | [accounting-assistant.md](accounting-assistant.md) | "Design a virtual assistant for accounting with regulatory knowledge" | Three knowledge layers (articles + rules + entities), knowledge graph vs RAG, intent routing, uncertainty signaling |

## Design patterns (generic prompts)

| System | File | Prompt | Key topics |
|--------|------|--------|------------|
| RAG system | [rag-system.md](rag-system.md) | "Design a document-QA system for a legal firm" | Hybrid search, CRAG gate, self-hosted models, structure-aware chunking |
| Agent system | [agent-system.md](agent-system.md) | "Design an automated code review agent" | Single agent with structured passes, context budgeting, false positive management |
| Eval & monitoring | [eval-harness.md](eval-harness.md) | "Design an eval pipeline for an LLM product" | Three-tier eval, golden set design, LLM-as-judge calibration, online monitoring |
| Scaling & cost | [scaling.md](scaling.md) | "Scale a RAG system 100x" | Per-component scaling, model routing, caching, cost model |
