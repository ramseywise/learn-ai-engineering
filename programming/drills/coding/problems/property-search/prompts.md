# property-search — env1 drill (60 min)

Semantic search over 50 real-estate listings: FastAPI + sentence-transformers
(`all-MiniLM-L6-v2`) + a FAISS inner-product index. Cheaper listings are supposed to be
boosted up the ranking. **It runs and returns results without errors.**

```bash
cd programming/drills/coding/scratch && cp -r ../problems/property-search/src property-search && cd property-search
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sentence-transformers faiss-cpu numpy pydantic
uvicorn main:app --reload        # then open http://localhost:8000
```

First run downloads the embedding model (~90 MB). `requirements.txt` also lists `openai`,
which the code never imports — skip it. Work in `programming/drills/coding/scratch/`; don't edit `src/`.

Answer as if an interviewer is reading. Name the actual functions, variables and lines.
Trace execution in order. Explain *why*, not just *what*.

---

## Phase 1 — comprehension (8 min)

**1a.** Walk `POST /search` from request to response for the query `"condo"`. What
happens at each step, and what is the shape of the data between steps?

**1b.** Why does `load_properties` call `faiss.normalize_L2` before building an
`IndexFlatIP`? What would change if it didn't?

---

## Phase 2 — bug hunt (30 min)

Search for **"condo"**. You should get five condos with similar names, and the cheaper
ones should rank higher.

**2a.** The ranking is wrong. Find every defect that makes it wrong. For each one: cite
the line, show a concrete input → wrong output, and give the smallest fix.

**2b.** Count what comes back. Is it what `max_results` promised? If not, why not?

**2c.** For each fix, write the test that would have caught it, as an `assert` you
could add without starting the server.

---

## Phase 3 — feature design (20 min, spoken)

Product wants two new filters:

1. **Size** — square footage, a new field on every listing.
2. **Features in natural language** — "I want a pool and parking".

**3a.** Where does `size_sqft` live — in the embedded text, or as a structured filter?
Pre-filter or post-filter relative to the FAISS search? Defend it.

**3b.** Compare a traditional NLP approach with an LLM approach for feature matching:
latency, cost, determinism, failure modes, maintenance.

**3c.** Give three concrete queries where the NLP approach returns a false positive.

**3d.** How would you make the LLM approach deterministic enough to ship?
