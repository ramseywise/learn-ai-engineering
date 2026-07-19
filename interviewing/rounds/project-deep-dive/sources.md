# Sources — Project Deep-Dive

## Internal Study Guides

### Direct applicability

| Guide | Section | Relevance |
|-------|---------|-----------|
| system-design guide | §6 — Drills: your systems as interview answers | Core method: turning real projects into interview-ready deep-dives. Architecture diagrams, component walk scripts, bottleneck stories. |
| product-business guide | §5 — Three-audience pitch | The three-altitude method (exec → architecture → deep dive) and how to calibrate for audience. Quantification framing. |
| evals-observability guide | Full guide | Measurement story: what to instrument, how to present eval results, incident detection and response. |

### Supplementary — any topic can surface in a deep dive

When an interviewer picks a project that overlaps with a specialized domain, consult the relevant guide before the interview:

- **Coding challenge guide** — if your project had significant algorithmic components
- **System design round guide** — full reference for architecture vocabulary and trade-off framing
- **Technical questions guide** — ML fundamentals, inference, fine-tuning depth if your project was model-centric
- **Customer simulation guide** — for FDE loops where the deep-dive doubles as a communication sample
- **Leadership rounds guide** — for cross-functional and stakeholder management threads in the project story

### Portfolio case studies

The system-design round examples directory contains worked walkthroughs of AI systems (RAG pipelines, agent systems, evaluation harnesses). Use those as templates for your own three-altitude answers.

Path: `interviewing/rounds/system-design-round/examples/`

---

## External Resources

### Staff engineer interview preparation

- **"The Staff Engineer's Path"** (Reilly, O'Reilly 2022) — Chapter 4 on technical vision and decision documentation; the "decision record" format maps directly to what interviewers probe in deep dives
- **StaffEng.com** — Interview stories from staff engineers at major companies; filter by "promotion packet" posts which contain the kind of impact narratives you need to prepare
- **"An Elegant Puzzle"** (Larson, Stripe Press 2019) — Systems and teams framing; useful for the cross-functional and team ownership threads

### Architecture presentation frameworks

- **C4 Model** (c4model.com) — Four-level diagram notation (Context → Container → Component → Code). The Context and Container levels map to the 60-second and 5-minute altitudes respectively. Good for projects with multiple services.
- **Architecture Decision Records (ADRs)** — Lightweight format: context, decision, consequences. The template in the study guide is derived from this; original format at `adr.github.io`.
- **"Designing Distributed Systems"** (Burns, O'Reilly 2018) — Reference for naming patterns (sidecar, ambassador, adapter) you may need to explain in distributed system deep dives

### Incident storytelling

- **Google SRE Book, Chapter 14** (sre.google/sre-book) — Postmortem format that maps to the detection→isolation→root cause→fix→prevention structure in the study guide. Free online.
- **Increment Magazine, "On-Call"** issue — Case studies in incident response that show how senior engineers narrate production failures

### AI tools usage probe (2026)

- **Anthropic's usage policies** — Useful to cite when explaining your verification practices: what responsible AI tool use looks like in professional contexts
- **"AI-Assisted Engineering"** posts on Eugene Yan's blog (eugeneyan.com) — Practitioner accounts of verifying AI output in ML engineering contexts; concrete and interviewable
