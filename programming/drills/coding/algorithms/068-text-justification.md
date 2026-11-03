---
title: "LC 68 — Text Justification"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [math-strings]
source: https://leetcode.com/problems/text-justification/
---
## Prompt

Given an array of `words` and an integer `maxWidth`, format the text so each line is
exactly `maxWidth` characters and fully (left and right) justified. Greedily pack as many
words per line as fit with at least one space between them, then distribute extra spaces
as evenly as possible, giving earlier gaps the surplus. The last line, and any line with
a single word, is left-justified with trailing spaces. Return the list of lines.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Split the problem into two separate steps: first decide which words belong on each line, then decide how to space the words on each line.

</details>

<details><summary>Hint 2</summary>

Greedily pack as many words as fit within max_width (counting single spaces) to form each line, then distribute leftover spaces as evenly as possible across the gaps for non-last lines, giving earlier gaps any extra space. The last line and single-word lines are left-justified with trailing padding.

</details>

<details><summary>Hint 3</summary>

This two-phase greedy packing plus careful gap arithmetic processes the text in O(total characters) time and space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

A greedy line-packing problem followed by careful spacing. First greedily group words: keep adding the next word to the current line while it still fits in max_width (counting one space between words). When it doesn't fit, close the line and start a new group. Then render each group: for a normal (non-last) line with multiple words, distribute the leftover spaces as evenly as possible across the gaps, giving the earlier gaps the extra space when it doesn't divide evenly. A single-word line (and the last line) is left-justified and padded with trailing spaces to max_width.

```python
# group
groups = greedily pack words so each fits in max_width (with single spaces)
# render
for each group except the last:
    if one word: left-justify + pad trailing spaces
    else:
        gaps = words - 1
        base, extra = divmod(max_width - total_word_len, gaps)
        give each gap `base` spaces, first `extra` gaps one more
last line: join with single spaces, pad trailing to max_width
```

**Complexity** — time O(total characters); space O(total characters)

Full Python solution: `LeetCodeCheat/text-justification.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Text Justification](https://leetcode.com/problems/text-justification/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/068-text-justification.yaml`.
