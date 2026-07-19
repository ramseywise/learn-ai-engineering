# Example: Agentic Financial Forecasting System

## Prompt
"Design an AI system that forecasts cash flows per customer segment for a B2B company. It should learn from its own prediction errors and explain its outputs."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Data sources: invoices, payments, CRM data, external signals?
- Forecast horizon: next month, next quarter, next year?
- Users: finance team (dashboards), executives (summaries), or automated downstream systems?
- Accuracy priority: is a wrong forecast worse than no forecast? (Financial planning = yes)
- Existing models: replacing spreadsheet forecasts? Legacy ML models?
- How often do segments change? (Static customer tiers vs dynamic clustering)

**Assumptions after clarify**:
- Invoice/payment history per customer, CRM metadata (industry, size, contract terms)
- Quarterly horizon, updated monthly
- Finance team via a dashboard, with natural-language explanations
- Wrong forecast on a large customer is high-impact — need confidence intervals + explanations
- Replacing manual spreadsheet forecasts
- Segments discovered dynamically via clustering, not pre-defined

## Step 2: Requirements (2 min)

**Functional**: Per-customer and per-segment cash flow forecasts with confidence intervals, natural-language explanations of forecast drivers, self-learning from prediction errors, dynamic customer segmentation, conversational query interface.

**Non-functional**: Forecast accuracy (MAPE < 15% at segment level), explainability (every forecast accompanied by top-3 drivers), learning cycle (model improves monthly without manual retraining), latency < 5s for conversational queries, < 30 min for full forecast refresh.

## Step 3: Design (15 min)

### Architecture

```
User query → AtlasAgent (Haiku router):
  ├── forecast_tool  → ForecastAgent loop
  ├── segment_tool   → SegmentationAgent
  └── knowledge_tool → Knowledge Graph + LLM explanation

ForecastAgent (LangGraph, self-learning loop):
  Planner → Forecaster → Evaluator → Learner
  │                                      │
  └──── feedback loop: errors → context ──┘

SegmentationAgent:
  HDBSCAN + UMAP clustering → Haiku reads centroids → human-readable segment names

Knowledge Graph (Neo4j):
  Customers ↔ Segments ↔ Metrics ↔ Forecasts
  LLM explains metrics and relationships in plain English

FastAPI backend → Next.js + Tremor dashboard
```

### Key design decisions

**Agentic loop vs static pipeline**: The forecast system is a self-learning agent loop, not a run-once pipeline. Four phases:

| Phase | What it does | Why agentic |
|-------|-------------|-------------|
| **Planner** | Selects features, decides model type, sets hyperparameters based on data characteristics | Adapts strategy per segment (seasonal segments get different treatment than growing ones) |
| **Forecaster** | Runs the statistical/ML model (LightGBM, ARIMA, or ensemble) | Executes the plan |
| **Evaluator** | Scores against held-out data + historical accuracy | Detects when the model is degrading |
| **Learner** | Updates the Planner's context with what worked/failed | Closes the feedback loop — next cycle starts smarter |

The Learner writes structured lessons into the agent's context: "Segment X is seasonal — ARIMA outperformed LightGBM by 12% last quarter." The Planner reads these on the next cycle. This is context engineering applied to ML: the model selection strategy improves without human intervention.

**Classical ML + LLM hybrid**: The forecasting itself uses classical ML (LightGBM for tabular, ARIMA for time series). The LLM layer:
1. Routes user queries to the right tool (forecast/segment/knowledge)
2. Generates natural-language explanations of forecast outputs
3. Manages the self-learning loop (Planner/Learner are LLM-driven)

Trade-off: LLMs are terrible at numerical prediction but excellent at reasoning about what strategy to try. Classical ML is great at prediction but can't explain itself. This hybrid gets both.

**Dynamic segmentation**: HDBSCAN + UMAP over customer features (payment patterns, invoice frequency, contract value, industry). No pre-set number of clusters — HDBSCAN discovers them. The LLM (Haiku) reads cluster centroids and generates human-readable segment names ("Late-paying Enterprise" vs "Cluster 7"). Segments re-compute monthly — customer behavior shifts.

**Knowledge graph for explainability**: Neo4j stores the relationships: Customer → Segment → Metrics → Forecasts. When a user asks "Why is Customer X's forecast declining?", the system:
1. Traverses the graph: Customer X → Segment "Late-paying Enterprise" → Metric "days_to_pay" trending up
2. LLM synthesizes: "Customer X's forecast is declining because their payment delays have increased from 30 to 55 days over the last 3 months, consistent with the Late-paying Enterprise segment trend."

This is more reliable than asking the LLM to explain a number — the graph provides the factual basis, the LLM provides the narration.

### Eval harness

```
Forecast evaluation (monthly):
  - Segment-level MAPE against actuals (target: < 15%)
  - Per-customer accuracy distribution (flag outliers)
  - Confidence interval calibration (do 90% intervals contain 90% of actuals?)
  - Learning effectiveness: is this month's MAPE < last month's?

Explanation evaluation (golden set):
  - 30 forecast+explanation pairs graded by finance team
  - LLM-as-judge: faithfulness (explanation matches graph data?)
  - Completeness: are the top-3 drivers mentioned?

Segmentation evaluation:
  - Silhouette score (cluster quality)
  - Business validity: do segment names match human intuition?
  - Stability: did 80%+ of customers stay in the same segment month-over-month?
```

### Data pipeline

```
Sources:
  Invoice/payment data (ERP sync, daily batch)
  CRM data (API pull, daily)
  External signals (industry indices, optional)

Pipeline:
  1. Ingest: idempotent upserts (content hash per record)
  2. Feature engineering: rolling aggregates (30/60/90-day payment patterns),
     seasonal decomposition, segment membership
  3. Training data: expanding window (all history) with temporal validation split
  4. Model training: per-segment models, monthly retrain
  5. Forecast generation: per-customer predictions + confidence intervals
  6. Knowledge graph update: new metrics, forecast nodes, segment relationships
  7. Dashboard refresh
```

### Deployment

- **Backend**: FastAPI on Cloud Run, stateless API serving forecasts from Postgres
- **Training**: Cloud Run Jobs (monthly scheduled), ~30 min per full retrain
- **Graph**: Neo4j (managed or self-hosted container), updated after each training cycle
- **Frontend**: Next.js + Tremor charts on Vercel
- **Observability**: Langfuse for agent traces, structlog for pipeline metrics, forecast accuracy dashboard

### Trade-off narrated

**Pre-built vs custom forecasting**: Could use a managed forecasting service (AWS Forecast, Google Vertex Forecast). Trade-off: managed = faster to ship, less control over feature engineering and segment-specific strategies. Custom = more work, but the self-learning loop and segment-aware strategy selection is the differentiator. At < 10K customers, the compute cost is trivial either way — the value is in the adaptive strategy, not raw scale.

**Single model vs per-segment models**: Per-segment. Payment patterns differ fundamentally between "Net-30 Enterprise" and "Prepaid Startup." A single model would need to learn these modes implicitly; per-segment models let each segment have its own feature set and hyperparameters. Trade-off: more models to manage (N segments × model artifacts), but the self-learning loop handles selection automatically.

## Step 4: Shortcomings (3 min)

- **Cold-start customers**: New customers with < 3 months of payment history can't be reliably forecasted. Mitigation: segment-level forecast as a proxy until individual history accumulates.
- **Regime changes**: Economic downturns, M&A, contract renegotiations invalidate historical patterns. The Learner detects degraded accuracy but can't predict regime changes. Mitigation: anomaly detection on forecast errors → alert finance team for manual review.
- **Knowledge graph staleness**: If the graph update fails after training, the LLM explains based on stale data. Mitigation: graph update is part of the training pipeline (same transaction), with rollback on failure.
- **Segment instability**: If HDBSCAN finds different clusters each month, segment-level trends become meaningless. Mitigation: stability constraint (penalize solutions that reassign > 20% of customers).

## Step 5: Close with measurement (2 min)

**Metrics**: Segment-level MAPE < 15%, confidence interval calibration within 5%, learning effectiveness (month-over-month MAPE improvement), explanation faithfulness > 0.9, dashboard query p95 < 5s.

**Cost model**: LLM costs are minimal (routing + explanation, ~$5/day). Compute costs dominated by monthly training (~$10/run on Cloud Run). Neo4j hosting (~$50/month). Total: < $100/month — the value is in replacing manual spreadsheet forecasting, not in raw compute.

**Future**: Real-time payment event processing (stream instead of batch), multi-entity forecasting (subsidiary-level roll-ups), what-if scenarios ("what if Customer X pays 30 days late?"), automated report generation for board presentations.

---

**Study refs**: [data eng & MLOps guide §1-2](../../../guides/8-data-eng-mlops/interview-guide.md) for pipeline design and MLOps maturity; [agents guide §1-4](../../../guides/4-agents/interview-guide.md) for agent loop design; [evals guide §2-4](../../../guides/6-evals-observability/interview-guide.md) for eval harness; librarian wiki: Orchestration Architecture Decision, Production Hardening Patterns.
