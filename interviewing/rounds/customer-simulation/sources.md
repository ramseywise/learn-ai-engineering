# Customer Simulation — Sources

## Internal guides

### Primary substrate

- **Product & business guide** — `../../guides/10-product-delivery/interview-guide.md`
  The entire guide is this round's substrate. Discovery frameworks, stakeholder communication, ROI framing, and delivery expectations are all treated there. Read before any scenario prep session.

### Supporting by scenario type

- **Security guide** — for incident response and data privacy scenarios (questions 1, 9)
  Data handling, compliance language, incident communication protocols, escalation paths.

- **System design guide §7** — for the IT constraint scenario (question 5)
  On-prem deployment vs. API-based architectures: trade-offs in latency, cost, data residency, and maintenance burden. Use this to fluently discuss VPC deployment, private cloud, and air-gapped options.

- **Agents guide §9** — for trust-building with skeptical stakeholders (questions 7, 12)
  The staged-trust pattern: graduated capability exposure rather than full-system demos. Relevant when onboarding skeptical technical teams or resetting with a hostile new contact.

- **LLM fundamentals §3** — for the fine-tuning question (question 3)
  The adaptation ladder: prompt engineering → few-shot → RAG → fine-tuning → pretraining. Understand when each is appropriate and how to explain the distinction in non-technical terms. The RAG-vs-fine-tuning distinction is the most commonly misunderstood by customers.

## External references

### Customer success methodology

- **MEDDIC / MEDDPICC** — qualification framework; useful for understanding what a champion does and what changes when they leave (question 12). The "Economic Buyer" and "Champion" roles map directly to simulation scenarios.
- **Gainsight resources on QBRs and renewal conversations** — for bad-news scenarios with renewal pressure (questions 4, 10). Practical framing for metrics reviews that aren't going well.
- **CustomerSuccessBox / Totango case studies** — real examples of pilot-to-renewal transitions; useful for internalizing what "metrics look bad" actually means operationally.

### Consultative selling frameworks

- **SPIN Selling (Rackham)** — Situation, Problem, Implication, Need-payoff. The discovery question structure in `study-guide.md` is derived from this. Most relevant for questions 1–6 where you need to surface the real need before proposing.
- **Challenger Sale (Dixon & Adamson)** — teaches insight-led conversations rather than relationship-led ones. Useful when the customer doesn't yet know what they want (board presentation, new contact scenarios).
- **"Discovering Questions Get You Connected" (Bates)** — shorter read; good for calibrating question types (open/probing/confirming) in a simulation context.

### Difficult conversations

- **"Difficult Conversations" (Stone, Patton, Heen / Harvard Negotiation Project)** — the "third story" framework (describe the situation from neither your perspective nor theirs, but a neutral observer's) is directly applicable to bad-news delivery and scope-creep scenarios.
- **"Crucial Conversations" (Patterson et al.)** — STATE model (Share facts, Tell story, Ask for others' paths, Talk tentatively, Encourage testing) for high-stakes conversations under pressure.
- **Nonviolent Communication (Rosenberg)** — for the emotional intelligence layer: observation → feeling → need → request. Particularly useful for hostile-new-contact and incident scenarios where the customer is activated.

### Technical communication

- **"Made to Stick" (Heath & Heath)** — for analogy construction and altitude matching. The SUCCES framework (Simple, Unexpected, Concrete, Credible, Emotional, Story) is a useful lens for checking whether your technical explanation will land.
- **HBR: "The Art of Giving a 5-Minute Presentation"** — directly applicable to the board presentation scenario (question 8).
