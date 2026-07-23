# Why We Extract Claims Before the AI Answers

> Applies to RAG-grounded agents (`hc_adk`, `hc_lg`, `hc_rag`) — any agent where the answer
> should come from retrieved passages, not model training memory.
> The grounding tiers that enforce this are in `invocation-flow.md` (Tier 2–3).

---

## The Yellow Highlighter Metaphor

When we ask an AI assistant to answer questions using company documents, we want the answer
to come from the documents — not from the model's general memory, assumptions, or guesses.

This is especially important in accounting and support domains where a fluent but
unsupported answer can be worse than no answer at all.

That is why we use **claims**.

A **claim** is a specific fact the AI extracts from retrieved documents *before* it writes
the final answer — in practice, copying the exact sentence or passage from the source
material that supports the answer.

Think of it like asking a human assistant to answer a question from a large manual:

1. **Find the relevant pages** — RAG search retrieves document chunks.
2. **Highlight the exact supporting sentences** — the AI marks these as `claims`.
3. **Write the answer from the highlights** — only after the evidence is marked.

Claims are a **yellow highlighter for AI**: they force the system to identify which facts
it is using before it explains them.

---

## Why This Matters

### 1. Claims anchor the AI to facts

Without claims, an AI may generate an answer that sounds confident but is only loosely
connected to the source documents. With claims, the answer is designed to be grounded
in specific retrieved evidence.

This does not make hallucinations impossible, but it reduces the risk and makes mistakes
easier to detect. Qi et al. show that self-generated citations can be unreliable —
referring to non-existent sources or failing to reflect the context actually used [1].

### 2. Claims create a verifiable paper trail

Claims make it possible to inspect the exact evidence behind an AI answer without asking
users to read long paragraphs. Chen et al. argue that citations should be concise and
sufficient, proposing sub-sentence citations to reduce the verification burden [2].

### 3. Claims separate facts from presentation

The source document may use formal, technical, or legal wording. The final answer may
need to be shorter, friendlier, or translated. Claims let us verify the factual basis is
correct independently of how the answer is expressed.

### 4. Claims make debugging much easier

If the AI gives a bad answer, the claim immediately identifies the failure type:

- **Wrong document retrieved?** → retrieval problem
- **AI highlighted the wrong sentence?** → extraction problem
- **Right claim, wrong explanation?** → generation problem

---

## Simple Example

User asks: *"Can I change the bank account used for vendor payments?"*

Source document contains:
> *The payment account can be changed under Settings > Payments > Vendor payment account.*

The AI extracts this sentence as a `claim`, then writes:
> *Yes. You can change the bank account for vendor payments under Settings → Payments → Vendor payment account.*

The answer is user-friendly, but anchored to a verified quote.

---

## Connection to Grounding Tiers

| Tier | What it enforces |
|---|---|
| Tier 1 | Top-level `citations[]` — IDs must come from the retrieved set |
| Tier 2 | Per-claim `citations` — every claim-level ID must be declared at top level. Closes the defeat case: a model that lists valid IDs at response level but references undeclared passages per-claim. |
| Tier 3 | `supportingQuote` — the verbatim excerpt must appear in the cited passage. Zero token overlap = fabricated. |

---

## Important Limitation

Claims are not magic. The system can still fail if:
- the wrong documents are retrieved
- the extracted claim is not actually relevant
- the final answer adds unsupported details
- source documents are outdated or incomplete

But claims make the system much safer and easier to evaluate because they expose the
evidence behind the answer. Citation quality itself must also be evaluated — the ALCE
benchmark shows even strong systems can lack complete citation support [3].

---

## References

[1] Qi et al. (2024). *Model Internals-based Answer Attribution for Trustworthy RAG.* EMNLP 2024.

[2] Chen et al. (2025). *Concise and Sufficient Sub-Sentence Citations for RAG.* arXiv:2509.20859.

[3] Gao et al. (2023). *Enabling Large Language Models to Generate Text with Citations.* EMNLP 2023.
