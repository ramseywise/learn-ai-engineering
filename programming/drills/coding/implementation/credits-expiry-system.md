---
title: "Credits expiry system"
track: coding
topic: implementation
difficulty: hard
timebox_min: 40
concepts: [implementation]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Build a credits management system (reported at OpenAI). Customers are granted credits
that expire at a given time. Level 1: add credits (amount, expiry) and charge a cost,
spending soonest-to-expire first. Level 2: expire credits automatically once their
time passes. Level 3: handle events arriving out of order (a charge can arrive before
the grant that funds it). Design so each level builds on the last.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Model each grant as a lot {amount_remaining, expires_at}. A charge spends soonest-to-expire first, and a min-heap keyed by expiry gives you that ordering.

</details>

<details><summary>Hint 2</summary>

Do expiry lazily and driven by the event timestamp: before each charge at time t, drop lots with expires_at <= t. No background timer in an event-driven system.

</details>

<details><summary>Hint 3</summary>

For out-of-order events, make final state a function of timestamps only. Buffer-and-sort-then-replay is the clean version. A re-derive-from-affected-timestamp log is the streaming version.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

OpenAI's progressive coding format: four gates of rising difficulty, pass by clearing two. It's an event-simulation / bookkeeping problem, so the win is a data model that survives the out-of-order events at the end. Represent each grant as a lot: {amount_remaining, expires_at, granted_at}. A charge consumes from lots in expiry order (soonest-expiring first) so credits aren't wasted. A priority queue / heap keyed by expiry is the natural structure. Clarify the rules before coding. Decide whether an unfunded charge should fail, go negative, or wait for a future grant, and what breaks ties. The hard version says events can arrive out of order (unstable network), which means you can't decide a charge's outcome purely on arrival. You must reason by event timestamp, not arrival order. Design Level 1 around timestamps from the start and the out-of-order case becomes a re-processing problem, not a rewrite.

**L1 — add credits + charge (spend soonest-expiring first)** — Keep active lots in a min-heap keyed by expires_at. add(t, amount, expires_at) pushes a lot. charge(t, cost) pops the soonest-to-expire lot, deducts from it, and continues to the next lot until the cost is covered; partially-consumed lots stay on the heap. Spending soonest-expiring-first maximizes credits actually used before they lapse.

**L2 — automatic expiry** — Before servicing any charge at time t, drain the heap of lots whose expires_at <= t (they're dead and can't fund anything). This is lazy expiry driven by the current event's timestamp — no background timer needed since the system is event-driven. Report the current balance as the sum of remaining amounts over unexpired lots.

**L3 — out-of-order events** — Events carry timestamps but may arrive in any order, so a charge can land before the grant that funds it. Two robust strategies. (a) Buffer and replay: collect events, sort by timestamp, then process the ordered stream through the L1/L2 logic — clean and correct if you can batch. (b) Streaming with reconciliation: keep an event log; when a late grant arrives with an earlier timestamp, re-derive state from the affected timestamp forward (or maintain per-timestamp deltas). Either way, the invariant is that final state depends only on event timestamps, never on arrival order — state that Level 1's timestamped model already makes possible.

**Complexity** — time O(log n) per add and per lot consumed via the heap; O(n log n) to sort for a replay pass; space O(n) for the active lots / event log

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is spending soonest-to-expire first the right greedy choice?
- How do you handle a charge that arrives before any funding grant: fail, defer, or go negative?
- Buffer-and-replay vs. incremental reconciliation: when do you pick each?
- How would you answer 'what was the balance at time t' for an arbitrary past t?
- How would you make this idempotent against duplicate/retried events?

Sources:

- [Medium (Exponent) — What It's Actually Like to Interview at OpenAI in 2026](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- [VO Prep — OpenAI Credits: Out-of-Order Credit Grants and Expiration Handling](https://voprep.com/en/openai-vo-quesions-2-credits-out-of-order-credit-grants-and-expiration-handling/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-credits-expiry-system.yaml`.
