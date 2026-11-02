---
title: "Key-value store"
track: coding
topic: implementation
difficulty: medium
timebox_min: 25
concepts: [implementation]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Build an in-memory key-value store. Level 1: SET, GET, DELETE. Level 2: add TTL so
keys expire. Level 3: add persistence so state survives a restart. Each level builds
on your previous code — design so you don't have to rewrite it.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Clarify first (single-threaded? durability?), then build Level 1 as a thin dict wrapper, but store each value as a {value, expires_at} record, not a bare value.

</details>

<details><summary>Hint 2</summary>

For TTL, prefer lazy expiration: check-and-evict on get so expired keys are never returned. Then mention an active background sweep as the memory-vs-work trade-off.

</details>

<details><summary>Hint 3</summary>

For persistence, contrast a write-ahead log (append every mutation, replay on restart) with periodic snapshots (fast recovery, may lose recent writes). Real systems combine both.

</details>

## Solution

<details><summary>Reference approach</summary>

A progressive implementation round reveals a single problem in levels, where the grade is mostly about whether your Level 1 design absorbs Levels 2 and 3 without a rewrite. Start deliberately small but with clean seams. Level 1 is just a dict wrapped in a class: set(k, v), get(k) -> value or None, delete(k). Resist adding anything else yet, but keep the store behind a small interface so you can change the stored value type later. The design decision that pays off: store each value as a record (value + metadata) rather than the bare value. Level 2 needs an expiry timestamp, and Level 3 needs it too. Talk through the trade-offs out loud (lazy vs. active expiry, log vs. snapshot persistence). Interviewers weight reasoning over feature count. Clarify requirements before coding (whether it's single-threaded or concurrent, and what durability guarantees are needed) since jumping straight to code is the most-cited failure mode.

**L1 — SET / GET / DELETE** — A hash map (dict) gives O(1) set/get/delete. Wrap it so values are stored as a small record, not a raw value — e.g. {value, expires_at=None}. get returns the value (or None); delete is idempotent. This record shape is what lets the next two levels slot in without touching the API.

**L2 — TTL / expiry** — set(k, v, ttl) stores expires_at = now + ttl. Use lazy expiration: on get, if now >= expires_at, delete the key and return None — so expired data never leaks out even if you never actively clean it. Mention the trade-off: lazy expiry leaves dead keys occupying memory until touched, so add an optional background sweep (active expiration) that periodically scans and evicts, or sample-and-evict like Redis. A min-heap or sorted structure keyed by expiry makes the sweep O(log n) per eviction instead of a full scan.

**L3 — persistence** — Two standard options. Append-only log (write-ahead log): append every mutation to a file before applying it; on restart, replay the log to rebuild state. Simple and durable but the log grows unbounded, so compact it periodically. Snapshot: periodically dump the whole map to disk; fast recovery but you lose writes since the last snapshot. Production systems combine them (snapshot + WAL replay of writes after the snapshot). Persist the expiry timestamps too, and on load drop keys that already expired while the process was down.

**Complexity** — time O(1) average for set/get/delete; expiry sweep O(log n) per eviction with a heap; space O(n) for n live keys, plus the on-disk log/snapshot

</details>

## Notes

Follow-ups an interviewer may push on:

- How would you make this thread-safe, and where exactly do the locks go?
- How would you add atomic multi-key transactions (BEGIN / COMMIT / ROLLBACK)?
- How does your persistence choice trade durability against write latency?
- How would you shard this across multiple nodes, and how do TTLs behave then?
- When would you switch the underlying structure from a hash map to an LSM tree or B-tree?

Sources:

- [System Design Handbook — Design a Key-Value Store](https://www.systemdesignhandbook.com/guides/design-a-key-value-store/)
- [Taro — Implement a key-value store with expiration (Google interview question)](https://www.jointaro.com/interview-insights/google/implement-a-key-value-store-with-an-expiration-feature-using-setkey-value-ttl-and-getkey-functions-discuss-your-data-structure-choice-time-complexity-and-expiration-strategy-explain-how-the-implementation-would-handle-concurrent-access-optional-show-example-usage-of-the-store-with-keys-expiring-after-a-specified-time-to-live-ttl-for-example-storesetfoo-bar-5-where-foo-expires-in-5-seconds/)
- [linkjob — Anthropic Software Engineer Interview](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-key-value-store.yaml`.
