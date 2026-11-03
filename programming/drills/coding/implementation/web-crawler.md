---
title: "Web crawler"
track: coding
topic: implementation
difficulty: hard
timebox_min: 40
concepts: [implementation]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement a web crawler. Level 1: single-threaded — fetch a page, extract links,
follow them, don't revisit. Level 2: add per-host rate limiting / politeness.
Level 3: make it concurrent. Design each level so the next builds on it.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Model it as frontier queue + visited set + a fetch/parse/enqueue loop. Normalize URLs (strip fragments, resolve relative links) before dedup, or the visited set is useless.

</details>

<details><summary>Hint 2</summary>

Rate limiting is per-host, not global: track last-fetch time per domain and defer URLs whose host was hit too recently. Honor Retry-After and back off with jitter.

</details>

<details><summary>Hint 3</summary>

For concurrency, share a thread-safe frontier across N workers. The visited set and per-host timers now need locking too, so track in-flight work to know when the crawl finishes.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

A progressive round (reported at Anthropic): you start with a correct single-threaded crawler and evolve it under new requirements, so the seams matter more than the first version. Model it as a work queue (frontier of URLs to visit) + a visited set for dedup + a fetch/parse/enqueue loop. The most important early decision is URL normalization: strip fragments, resolve relative links against the base, lowercase the host, drop default ports, so the visited set actually dedups. Keep fetch, parse, and the frontier as separate components. That separation is what lets you swap the frontier for a rate-limited one (L2) and the loop for a thread pool (L3) without a rewrite. Clarify scope up front (same-domain only, a max depth, whether to respect robots.txt). Handle errors and timeouts gracefully with backoff. Real pages fail.

**L1 — single-threaded crawl** — BFS/DFS over a frontier queue. Loop: pop a URL, skip if in visited, fetch it, add to visited, extract and normalize links, enqueue unseen ones. Bound it by max depth or max pages. Normalize URLs before checking the visited set so `example.com/a` and `example.com/a#top` aren't crawled twice. Wrap fetch in try/except with a per-request timeout.

**L2 — rate limiting / politeness** — Be polite per host: at most 1 request per host per interval (configurable), and honor Retry-After on 429/503. Track last-fetch time per domain; if a URL's host was hit too recently, defer it (re-enqueue with a ready-at time, or hold a per-host queue). Add exponential backoff with jitter on failures so retries don't synchronize. The key insight: rate limiting is per-host, not global — you can still be fast overall by interleaving many hosts.

**L3 — concurrency** — Run N workers (thread pool for I/O-bound fetching, or asyncio) pulling from a shared, thread-safe frontier. The visited set and per-host timers now need synchronization (a lock, or a concurrent structure) to avoid double-crawling and to keep the per-host limit correct under parallelism. Producers (link extractors) and consumers (fetchers) share the queue; use a sentinel or an in-flight counter to know when the crawl is truly done. Per-host caps + a global worker pool give high aggregate throughput while any single site sees at most 1 req/interval.

**Complexity** — time O(V + E) in pages and links visited; wall-clock bounded by rate limits and worker count; space O(V) for the visited set and frontier

</details>

## Notes

Follow-ups an interviewer may push on:

- How do you respect robots.txt and crawl-delay?
- How would you detect and avoid crawler traps (infinite calendars, session-id URLs)?
- How do you scale the visited set past memory (bloom filter, sharded store)?
- How would you distribute this across many machines, and how is the frontier partitioned?
- Thread pool vs. asyncio here: which fits an I/O-bound crawler and why?

Sources:

- [Hello Interview — Design a Web Crawler](https://www.hellointerview.com/learn/system-design/problem-breakdowns/web-crawler)
- [AlgoMaster — Design Multithreaded Web Crawler (concurrency interview)](https://algomaster.io/learn/concurrency-interview/design-multithreaded-web-crawler)
- [linkjob — Anthropic Software Engineer Interview](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-web-crawler.yaml`.
