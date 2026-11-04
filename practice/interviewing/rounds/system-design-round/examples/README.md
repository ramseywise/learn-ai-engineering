# System Design Round — Worked Examples

Each file walks through a full system design using the five-step process from the [study guide](../study-guide.md). Practice by attempting the design yourself first (40-min timer), then compare.

## Design patterns (generic prompts)

| System | File | Prompt | Key topics |
|--------|------|--------|------------|
| RAG system | [rag-system.md](rag-system.md) | "Design a document-QA system for a legal firm" | Hybrid search, CRAG gate, self-hosted models, structure-aware chunking |
| Agent system | [agent-system.md](agent-system.md) | "Design an automated code review agent" | Single agent with structured passes, context budgeting, false positive management |
| Eval & monitoring | [eval-harness.md](eval-harness.md) | "Design an eval pipeline for an LLM product" | Three-tier eval, golden set design, LLM-as-judge calibration, online monitoring |
| Part matching | [part-matching.md](part-matching.md) | "Find interchangeable parts in industrial catalogues" | Retrieval ceiling, attributes vs similarity, cost-priced routing, closure, document reading |
| Scaling & cost | [scaling.md](scaling.md) | "Scale a RAG system 100x" | Per-component scaling, model routing, caching, cost model |
| Voice agent | [voice-agent.md](voice-agent.md) | "Design a voice agent that conducts thousands of structured phone conversations a day and scores each one" | Cascade vs speech-to-speech, endpointing, barge-in with tools, per-vertical config, calibrated scoring |
