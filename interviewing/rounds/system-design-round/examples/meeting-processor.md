# Example: Meeting Intelligence & Lifecycle Agent

## Prompt
"Design an AI system that captures meeting transcripts, extracts structured decisions and action items, and drives an engagement lifecycle state machine."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Meeting types: internal standups, client discovery calls, all-hands? (Different extraction needs)
- Capture method: live transcription, recording upload, or notetaker integration?
- What "structured output" means: just action items, or decisions, blockers, sentiment, topics?
- Lifecycle: what are the stages? Who defines transitions? Is the agent advisory or authoritative?
- Multi-tenant: multiple teams/orgs using the same system?
- Accuracy bar: what's acceptable for action-item extraction? (70%? 95%?)

**Assumptions after clarify**:
- Nonprofit client engagement meetings (discovery, check-ins, retrospectives)
- Notetaker vendor captures transcript via calendar integration, delivers via webhook
- Extract: action items, decisions, blockers, follow-ups — each with confidence score
- Agent is the **sole writer** of engagement stage transitions (authoritative, not advisory)
- Multi-tenant from day one (multiple nonprofits, RLS on shared Postgres)
- Accuracy bar: 70% action-item capture in v1 (measured against human-graded sample)

## Step 2: Requirements (2 min)

**Functional**: Calendar-triggered meeting capture, transcript ingestion, typed fact extraction (action items, decisions, blockers with confidence), engagement stage transitions, notification emails on stage change, queryable meeting history.

**Non-functional**: Transcript landing < 15 min after meeting end, extraction accuracy > 70% action items, multi-tenant isolation (RLS), audit trail (who/what/when for every stage transition), zero data leakage between tenants.

## Step 3: Design (15 min)

### Architecture

```
Calendar event (tagged "engagement") → Notetaker vendor auto-joins
  → Meeting ends → Vendor webhook delivers transcript
  → Webhook receiver (HMAC-verified, idempotent)
  → Store: meetings + transcript_chunks (with nonprofit_id FK + RLS)

MeetingProcessor (LangGraph pipeline):
  transcript_chunks → Extract facts → Score confidence → Write extracted_facts
  → If stage-relevant facts detected → Evaluate stage transition
  → If transition valid → Write Engagement.stage (sole writer, own credential)
  → Stage write fires comms webhook → templated email to client

Query interface:
  "What were the action items from last week's meeting with Org X?"
  → Platform API → filtered by tenant → LLM synthesizes
```

### Key design decisions

**Sole writer for lifecycle state**: The agent owns `Engagement.stage`. No human, no other system writes this field directly. Why?
1. Single source of truth — no conflicting stage updates
2. Audit trail — every transition is attributable to the agent's own service credential
3. Trigger chain — stage write is the single event that fires downstream actions (emails, dashboard updates, task creation)

Trade-off: if the agent gets a transition wrong, there's no human override in the happy path. Mitigation: transitions require a confidence threshold (> 0.8) AND a matching extracted fact type. Below threshold → flag for human review instead of auto-transitioning.

**Typed fact extraction with confidence**:

```python
class ExtractedFact(BaseModel):
    fact_type: Literal["action_item", "decision", "blocker", "follow_up",
                       "deadline", "risk", "question"]
    text: str
    certainty: int  # 0-100
    assignee: str | None
    due_date: date | None
    source_chunk_id: str  # links back to transcript
```

The `fact_type` enum is intentionally small (7 types, not 20). Each type must be graded — the accuracy harness runs per-type precision/recall. More types = harder to maintain accuracy. Start small, add types when the grading proves they work.

**Multi-tenant from migration one**: Learned from a predecessor system that retrofitted tenancy after 3 migrations — it was painful. Every table has `nonprofit_id` as a FK, RLS policies from the first migration, and the API filters by tenant automatically. The agent's service credential is scoped to the tenant context of the meeting.

**Template-rendered, not greenfield**: The system is rendered from a project template with toggles: `vector_backend=postgres`, `include_calendar_integration`, `include_meeting_intelligence`, `primary_chat_agent=lg_agent`. This gives:
- Postgres + pgvector (shared Supabase instance)
- Calendar integration scaffold
- Meeting capture webhook receiver
- LangGraph agent boilerplate

What the template covers vs. what's custom is documented in a diff doc — this is a key architectural decision that avoids building infrastructure that already exists.

### Integration patterns

```
Inbound:
  - Notetaker vendor webhook → HMAC-verified receiver → idempotent handler
    (event may be delivered more than once → deduplicate by meeting_id + timestamp)
  - Calendar API → tagged events trigger notetaker join

Outbound:
  - Platform API (shared Supabase) → stage writes, fact queries
  - Comms module → stage change webhook → templated email
  - Dashboard → reads from Platform API (never direct DB)

Service credentials:
  - Agent has its OWN credential (not service-role key)
  - Stage writes are attributable to "PM-AI" in audit log
  - Principle: if the system is the sole writer, its writes must be distinguishable
```

### Eval harness

```
Accuracy harness (graded sample):
  1. Collect ≥ 3 real meeting transcripts
  2. Human labels: what are the actual action items, decisions, blockers?
  3. Run MeetingProcessor on same transcripts
  4. Grade: per-type precision + recall
  5. Bar: 70% action-item recall (v1 — raise to 85% in v2)

Metrics:
  - Extraction accuracy per fact_type
  - Confidence calibration: do certainty=90 facts have 90% accuracy?
  - Stage transition accuracy: correct transition / total transitions
  - Latency: transcript → extracted_facts (target: < 2 min)
  - Escalation rate: what % of transitions need human review?
```

### Deployment

- **Compute**: Cloud Run (webhook receiver + extraction pipeline) — stateless, scales to zero between meetings
- **Database**: Shared Supabase (Postgres), same instance as other platform services — tenancy via RLS
- **Pipeline**: Webhook-triggered (event-driven), not scheduled — meetings happen when they happen
- **Orchestration**: LangGraph for extraction (multi-step: parse → extract → score → validate), flat dispatch for everything else
- **Monitoring**: structlog for pipeline metrics, Langfuse for LLM traces

### Trade-off narrated

**Notetaker vendor vs manual upload**: Vendor (Fireflies-class) for auto-capture — zero friction, meetings are captured without human action. Manual upload as fallback if budget is $0. Trade-off: vendor adds a recurring cost and a dependency (webhook shape unknown until chosen, API changes), but the alternative (asking busy volunteers to upload recordings) has near-zero adoption. The vendor dependency is worth it.

**Graphs for genuinely multi-step flows only**: The extraction pipeline is a genuine graph (parse → extract → score → validate, with conditional branching on confidence). But the webhook receiver, the stage writer, and the query interface are flat dispatch — not everything needs to be a graph. LangGraph is used where the flow has real branching logic, not as a default.

## Step 4: Shortcomings (3 min)

- **Extraction accuracy ceiling**: LLM extraction from noisy transcripts (interruptions, tangents, incomplete sentences) may plateau below the 85% bar. Mitigation: prompt iteration with real transcripts, consider fine-tuning on domain-specific meeting patterns.
- **Meeting scope ambiguity**: A meeting may span two engagement stages. Which stage does the fact belong to? Mitigation: each fact links to the meeting's engagement; stage transitions use the most recent meeting's facts as evidence.
- **Vendor lock-in**: The webhook shape is vendor-specific. Changing vendors means rebuilding the receiver. Mitigation: adapter pattern — vendor-specific webhook parsing → common `TranscriptEvent` schema → rest of pipeline is vendor-agnostic.
- **Offline/manual meetings**: Not all engagement interactions are scheduled meetings. Phone calls, hallway conversations, emails contain decisions too. v1 accepts this gap — only structured meetings are captured.

## Step 5: Close with measurement (2 min)

**Metrics**: Action-item recall > 70% (v1), stage transition accuracy > 90%, transcript landing < 15 min, extraction latency < 2 min, zero cross-tenant data leakage.

**Cost**: LLM extraction ~$0.10/meeting (one Sonnet call per transcript). Notetaker vendor ~$20-50/month. Infrastructure near-zero (Cloud Run scales to zero, shared Supabase). Total: < $75/month for a system that replaces manual note-taking and follow-up tracking for an entire nonprofit engagement team.

**Future**: Action-item auto-assignment based on historical patterns, meeting summary emails (auto-generated, sent within 1 hour), cross-meeting trend analysis ("this client's blockers are recurring"), integration with task management (extracted action items → Linear/Asana issues).

---

**Study refs**: [agents guide §1-4](../../../guides/4-agents/interview-guide.md) for workflow patterns and when to use graphs; [data eng guide §1](../../../guides/8-data-eng-mlops/interview-guide.md) for event-driven pipelines and idempotency; [security guide §2-3](../../../guides/7-security-safety/interview-guide.md) for multi-tenant isolation and credential scoping; [evals guide §2-4](../../../guides/6-evals-observability/interview-guide.md) for accuracy harness design; librarian wiki: System Design — Serverless Agent Backends, Cloud Run + Cloud SQL Pattern.
