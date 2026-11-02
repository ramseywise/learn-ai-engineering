# Practice: the Tallybook retrieval kit

Everything here runs offline with no API key. The code blocks in the notes import from this folder, so you can change something and see the numbers move.

| File | What it is |
|---|---|
| `ragkit.py` | The Tallybook help-centre corpus (18 pages, including the stale 2024 refund page and an internal runbook), 20 labelled queries, BM25, a small dense embedder, RRF, a `Retriever` with sparse, dense and hybrid search, and the eval metrics. It needs only NumPy |
| `ablation.py` | Compares four local embedders, BM25 and their fusion on the Tallybook queries, with paired bootstrap intervals. Note 11 quotes its output. First run downloads about 2.5 GB of ONNX weights |
| `check_blocks.py` | Runs every Python block in `../notes/` and compares its output with the `text` block printed underneath it |

## Run the scoreboard

```bash
cd generative-ai/02-rag-retrieval/practice
uv run --with numpy python ragkit.py
```

This prints recall@3 and MRR for BM25, dense and hybrid search, overall and per query kind. The chapters use these numbers, starting with [03](../notes/03-keyword-semantic-and-hybrid-search.md).

Start exercising with one change at a time: add a page to `DOCS`, label a query you care about in `QUERIES`, or delete `kb-05` and see what happens to the refund questions.

## Check the notes

```bash
uv run --with numpy python check_blocks.py 03        # one note, by prefix
uv run --with numpy --with scikit-learn --with faiss-cpu --with duckdb --with pydantic \
    --with chromadb --with sentence-transformers --with bm25s --with tiktoken \
    --with langchain-text-splitters --with opentelemetry-sdk --with fastembed \
    --with boto3 python check_blocks.py              # every note
```

Blocks marked `# illustrative` in their first lines are skipped, because they need a paid API or infrastructure and say which. Timings in the output differ from run to run, so a diff that only touches a timing line isn't a failure. Add `--write` to replace the printed output in the notes with what the blocks print now.

## Labs elsewhere

The DeepLearning.AI labs and the book labs are linked upstream from each note's `## Labs` table and from the [pillar README](../README.md#coursework-and-labs).
