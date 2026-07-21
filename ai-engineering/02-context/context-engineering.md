---
origin: notion-export
confidence: medium
sources:
  - https://medium.com/ai-in-plain-english/10-context-engineering-techniques-every-ai-engineer-should-know-b54b486a6921
cleaned: 2026-07-17
---

https://medium.com/ai-in-plain-english/10-context-engineering-techniques-every-ai-engineer-should-know-b54b486a6921

*(missing diagram — not exported from Notion)*

←approaches

←context engineering’s goals

Context Engineering is the process of selecting, organizing, compressing, and delivering the right information to an LLM before it generates a response.

1. **Context Compression — compress documents into only the information relevant to the current question.**
2. **Context Ranking  -reranking - Only send the highest-ranked results. — also for RAG**
3. **Dynamic Context Windows: adjusts context size based on task complexity:**
    1. simple one (Simple FAQ)— less chunks
    2. complex one (Product comparison)— more chunks 
4. **Metadata Filtering First — also used in RAG** 
5. **Context Deduplication — but, need to detect deduplicated chunks after re-retrieval, cuz they might be the most relevant chunks, — a good parameters for reranking** 
6. **Conversation Memory Management — Memory management + Context Management** 
7. **Hierarchical Retrieval —?**
8. **Context Caching — hot questions caching** 
9. **Structured Context Formatting - Avoid dumping raw text.**
10. **Context Validation - avoid poor context — hallucination** 
    1. Remove outdated documents
    2. Validate permissions
    3. Detect conflicting information
    4. Check freshness
    5. Verify citations

pipeline:

```markdown
User Query
      ↓
Metadata Filtering
      ↓
Vector Search
      ↓
Context Ranking
      ↓
Deduplication
      ↓
Compression
      ↓
Memory Injection
      ↓
Structured Formatting
      ↓
LLM
      ↓
Response

```

*(missing diagram — not exported from Notion)*

## Salvaged from table_of_contents.md (Notion): skills design tips (OpenAI)


### skills tips from https://developers.openai.com/blog/skills-shell-tips  — add in ‣

**1) Write skill descriptions like routing logic** 

- When should I use this?
- When should I not use this?
- What are the outputs and success criteria?
    
    2 points: skill description tokens and precision 
    
    ```markdown
    # bad skill description（约 45 tokens）
    description: |
      This skill handles the complete deployment process to production.
      It covers environment checks, rollback procedures, and post-deploy
      verification. Use this before deploying any code to production.
    
    # good（约 9 tokens）
    description: Use when deploying to production or rolling back.
    ```
    

**2) Add negative examples and edge cases to reduce misfires**

```markdown
“Don’t call this skill when…” cases (and what to do instead).
```

*(missing diagram — not exported from Notion)*

**3) Put templates and examples inside the skill (they’re basically free when unused)**

This is especially effective for knowledge work outputs, like:

- Structured reports.
- Escalation triage summaries.
- Account plans.
- Data analysis writeups.

**4) Design for long runs early with container reuse and compaction**

**5) When you need determinism, explicitly tell the model to use the skill**

```markdown
“Use the <skill name> skill.”
```

### **6) Treat skills plus networking as a high-risk combo (design for containment)**

This is the security tip that’s easy to gloss over now and hard to fix later.

**Combining skills with open network access creates a high-risk path for data exfiltration.** If you use networking, keep network allowlists strict, assume tool output is untrusted, and avoid open internet plus powerful procedures in consumer-facing flows where users expect strong confirmation controls.

A strong default posture:

- Skills: **allowed**
- Shell: **allowed**
- Network: **enabled only with a minimal allowlist**, per request, for narrowly scoped tasks

