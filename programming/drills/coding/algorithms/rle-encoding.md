---
title: "Run-length encoding"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [math-strings]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement run-length encoding (RLE): compress a string by replacing each run of
identical consecutive characters with the character followed by its count (e.g.
"aaabbc" -> "a3b2c1"). Also write the matching decoder.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

In one pass, track the current char and a run count, and emit (char, count) each time the char changes.

</details>

<details><summary>Hint 2</summary>

Don't forget to flush the final run after the loop ends. That's the usual off-by-one bug.

</details>

<details><summary>Hint 3</summary>

Decoding must parse multi-digit counts (a run of 12 is 'a12'), and state your assumption about digits in the input so encode/decode round-trip.

</details>

## Solution

<details><summary>Reference approach</summary>

RLE is a single linear scan. Iterate over the string, tracking the current character and a run counter. When the next character differs (or you reach the end), emit the character and its count, then reset. The only subtlety is flushing the final run after the loop, a classic off-by-one. Decoding is the inverse: read a character, read its count, repeat the character that many times. Watch the ambiguity when the data contains digits (real RLE variants escape counts or use fixed markers). For the interview version, state the assumption (alphabetic input, or counts always emitted even for runs of length 1) so encode/decode round-trip exactly.

```python
def encode(s):
    if not s: return ""
    out, prev, count = [], s[0], 1
    for c in s[1:]:
        if c == prev:
            count += 1
        else:
            out.append(prev + str(count))
            prev, count = c, 1
    out.append(prev + str(count))     # flush the last run
    return "".join(out)

def decode(s):
    out, i = [], 0
    while i < len(s):
        ch = s[i]; i += 1
        num = ""
        while i < len(s) and s[i].isdigit():
            num += s[i]; i += 1
        out.append(ch * int(num))
    return "".join(out)
```

**Complexity** — time O(n) to encode and O(output length) to decode; space O(n) for the output (RLE can expand incompressible input, so it isn't in-place)

</details>

## Notes

Follow-ups an interviewer may push on:

- How do you handle input that already contains digits without breaking the decoder?
- When does RLE make the output larger, and how would you guard against that?
- How would you encode runs of length 1 more compactly?
- How would you adapt RLE to a byte stream / binary image rather than a string?

Sources:

- [Techie Delight — Run Length Encoding (RLE) Data Compression Algorithm](https://www.techiedelight.com/run-length-encoding-rle-data-compression-algorithm/)
- [Michael Dipperstein — Run Length Encoding (RLE) Discussion and Implementation](https://michaeldipperstein.github.io/rle.html)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-rle-encoding.yaml`.
