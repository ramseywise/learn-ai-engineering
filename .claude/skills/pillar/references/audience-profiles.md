# Audience profiles

Who reads each subject. Prerequisites come from each subject's README ("Before you begin"), and the
README wins if the two disagree. `audience-editor` and `/write-chapter` load this file, so keep it short.

Every subject has the same adult reader: learning alone, technically serious, short of time, often
preparing for a job or an interview. Write to a capable colleague. Never condescend, never pad.

The test for a term: if the prerequisites do not teach it and this note does not define it, the note
has a gap. A term the prerequisites teach needs no definition, and defining it again is padding.

| Subject | Reader | Assumed | Not assumed | Maths and code |
|---|---|---|---|---|
| **Programming** | Someone learning to program, or moving to a new language | A terminal, and nothing more at the start. Each track assumes what its README says comes first | Any language feature not yet taught, any CS vocabulary | No maths beyond arithmetic. Code is the main text, and runs as written |
| **Data analytics** | An aspiring or working analyst who answers questions for decision-makers | Python modules 01 to 03: variables, functions, collections, files | pandas, statistics, SQL depth | Algebra. Introduce a formula in words first, then compute it in code |
| **Data engineering** | An engineer who moves and stores data for others to trust | Python 01 to 03, SQL to its capstone. Docker helps | Distributed systems, cloud services, operating system internals | Little maths, plus back-of-envelope sizing. Code and config, run locally |
| **Data science** | An analyst moving on to predictive modelling | Probability, estimation, hypothesis tests, regression, pandas, NumPy | Machine learning, deep learning, and calculus beyond the chain rule | Linear algebra and the chain rule where stated. Derive what the reader must debug, not everything |
| **Generative AI** | A builder who wants useful LLM applications | Comfort with Python helps. No machine learning is required for Unit 01 | Neural network internals, statistics, any provider's API | Light maths, explained when used. No GPU or API key unless the README says so |
| **AI engineering** | An engineer making LLM systems reliable in production | Generative AI Unit 01, and practical Python or TypeScript | Production agent harnesses, distributed tracing, security engineering | Light maths: cost and token arithmetic. Labs in both TypeScript and Python |

## Register

The same for every subject, and it comes from `pillar-layout.md`:

- State the claim plainly, then give the evidence. Every number carries the setup it holds under.
- Prefer a worked example to an abstract explanation.
- Say what goes wrong, and what the symptom looks like, not only what to do.

## Slides versus chapters

A chapter is read alone, so it carries its own context. A slide supports someone talking, so it carries
the claim and the number and leaves the explanation for the speaker notes. See `deck-spec.md`.
