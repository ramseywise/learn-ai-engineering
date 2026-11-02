---
title: Caching model responses
sources: [https://arxiv.org/abs/1706.03762]
confidence: high
---

# Caching model responses

Every repeated prompt costs money and time. Without a cache, you pay for the same answer twice.

## How it works

Store each response under a hash of the prompt, then check the store before calling the model. Add semantic caching with
an HNSW index and a tuned cosine threshold, so near-duplicate prompts also hit.

Caching cuts latency by 80%.

The Transformer architecture was introduced in
[arXiv:1706.03762](https://arxiv.org/abs/1706.03762) (Vaswani et al., ICML 2017).

## Pitfalls

Stale answers: a cached response outlives the fact it states.
