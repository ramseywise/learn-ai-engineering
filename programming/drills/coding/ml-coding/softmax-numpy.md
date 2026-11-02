---
title: "Softmax in NumPy"
track: coding
topic: ml-coding
difficulty: easy
timebox_min: 15
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement the softmax function from scratch in NumPy so it is numerically stable
and works row-wise on a 2-D batch of logits.

## Starter

Blank file in `drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The definition is exp(x_i) / sum(exp(x_j)). Try it directly on a logit like 1000 and watch it overflow to nan.

</details>

<details><summary>Hint 2</summary>

Softmax is shift-invariant: subtracting any constant from all logits leaves the output unchanged. Subtract the max so the biggest exponent becomes exp(0) = 1.

</details>

<details><summary>Hint 3</summary>

For a 2-D batch, reduce along axis=-1 with keepdims=True so both the max subtraction and the sum division broadcast per row.

</details>

## Solution

<details><summary>Reference approach</summary>

Softmax turns a vector of logits into a probability distribution: softmax(x)_i = exp(x_i) / sum_j exp(x_j). The naive formula overflows: exp of a large logit (roughly > 710 in float64) returns inf and you get nan. Subtract the row maximum before exponentiating. Because softmax is shift-invariant (subtracting a constant c from every logit multiplies numerator and denominator by exp(-c), which cancels), this changes nothing mathematically. But it keeps the largest exponent at exp(0)=1. For a batch, operate along the last axis with keepdims=True so the max and sum broadcast correctly per row. This is the same routine that sits inside attention and every classification head. Interviewers use it to check you know why the subtraction is there.

```python
def softmax(x, axis=-1):
    # subtract per-row max for numerical stability (shift-invariance)
    z = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=axis, keepdims=True)
```

**Complexity** — time O(n) in the number of logits (one pass for max, one for exp, one for sum); space O(n) for the exponentiated array

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is softmax shift-invariant but not scale-invariant?
- How would you compute log-softmax stably, and why prefer it for cross-entropy?
- How does the temperature parameter change the output distribution?
- Where does this exact function appear inside scaled dot-product attention?

Sources:

- [Delft Stack — NumPy Softmax in Python](https://www.delftstack.com/howto/numpy/numpy-softmax/)
- [Nolan Conaway — A softmax function for numpy](https://nolanbconaway.github.io/blog/2017/softmax-numpy.html)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-softmax-numpy.yaml`.
