# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Note 14: use code checks and critiques as evidence about a judge.

Run from this folder with: uv run judge_checks_and_critiques.py

The judges come from GA 06's support_agent package. They are deterministic rules and the
"human" labels are the planted failures, so this tests the procedure and measures no real
model. Part 4 of the note needs a real model: see the ONLINE section at the bottom.
"""
import argparse
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True  # leave GA 06's package folder as it is
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "06-observability" / "practice"))

from support_agent import generate_traces  # noqa: E402
from support_agent.judges import _numbers, fast_hallucination, raw_export, to_conversation  # noqa: E402

SEED = 14
PROVABLE = {"hallucinated_citation", "distorted_claim"}


# %% load
class Row:
    def __init__(self, trace):
        self.trace = trace
        self.conv = to_conversation(raw_export(trace))
        self.human_pass = trace.seeded_failure not in PROVABLE  # stand-in for a person's label


rows = [Row(t) for t in generate_traces()]
order = list(range(len(rows)))
random.Random(SEED).shuffle(order)
train = [rows[i] for i in order[:280]]  # few-shot pool: a rule judge has no use for it
dev = [rows[i] for i in order[280:840]]
test = [rows[i] for i in order[840:]]
for name, part in [("train", train), ("dev", dev), ("test", test)]:
    print(f"{name:5} {len(part):4} rows  human PASS {sum(r.human_pass for r in part):4}  FAIL {sum(not r.human_pass for r in part):2}")


# %% checks and judges
def check_citation(conv):
    """Code check A: every cited URL was retrieved."""
    retrieved = {d["url"] for d in conv.documents}
    return all(url in retrieved for url in conv.sources)


def check_numbers(conv):
    """Code check B: every number in the answer appears in a document the answer cites."""
    cited = [d for d in conv.documents if d["url"] in conv.sources]
    if not cited:
        return True  # nothing to compare against: check A reports this row
    return not _numbers(conv.answer) - set().union(*(_numbers(d["text"]) for d in cited))


def code_passes(conv):
    return check_citation(conv) and check_numbers(conv)


def lenient(conv):
    """v0: GA 06's lenient judge. Its evidence list plays the part of a critique."""
    return fast_hallucination(conv, "lenient")


def strict(conv):
    """v1: GA 06's strict judge, which is v0 without the low-overlap rule."""
    return fast_hallucination(conv, "strict")


def scoped(conv):
    """v2, written here: v1 with numbers compared against the cited documents only."""
    retrieved = {d["url"] for d in conv.documents}
    evidence = [{"claim": url} for url in conv.sources if url not in retrieved]
    cited = [d for d in conv.documents if d["url"] in conv.sources]
    if cited:
        allowed = set().union(*(_numbers(d["text"]) for d in cited))
        evidence += [{"claim": n} for n in sorted(_numbers(conv.answer) - allowed)]
    return {"hallucination_detected": bool(evidence), "evidence": evidence}


def judge_passes(judge, row):
    return not judge(row.conv)["hallucination_detected"]


# %% metrics
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def rates(verdicts, labels):
    """PASS is the positive class, as in note 05. verdicts and labels are True for PASS."""
    tp = sum(v and h for v, h in zip(verdicts, labels))
    fn = sum(h and not v for v, h in zip(verdicts, labels))
    tn = sum(not v and not h for v, h in zip(verdicts, labels))
    fp = sum(v and not h for v, h in zip(verdicts, labels))
    n = tp + fn + tn + fp
    agree = (tp + tn) / n
    chance = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / (n * n)
    return {"tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "tpr": tp / (tp + fn) if tp + fn else float("nan"),
            "tnr": tn / (tn + fp) if tn + fp else float("nan"),
            "kappa": (agree - chance) / (1 - chance) if chance < 1 else float("nan")}


def corrected_pass_rate(observed, tpr, tnr):
    """Note 05's correction: observed = true*TPR + (1-true)*(1-TNR), solved for true."""
    return (observed + tnr - 1) / (tpr + tnr - 1)


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for the table [[a, b], [c, d]]."""
    n1, n2, k = a + b, c + d, a + c
    prob = lambda x: math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    seen = prob(a)
    return min(1.0, sum(prob(x) for x in range(max(0, k - n2), min(k, n1) + 1) if prob(x) <= seen * (1 + 1e-9)))


def holm(pvalues):
    """Holm's adjusted p-values for one family of tests."""
    ranked = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for place, i in enumerate(ranked):
        running = max(running, min(1.0, (len(pvalues) - place) * pvalues[i]))
        adjusted[i] = running
    return adjusted


# %% part 1: code checks against the judge
def two_by_two(part, check, judge):
    return Counter((check(r.conv), judge_passes(judge, r)) for r in part)


def show_table(title, table):
    print(f"\n{title}")
    print(f"  code pass, judge pass {table[(True, True)]:4}")
    print(f"  code pass, judge FAIL {table[(True, False)]:4}")
    print(f"  code FAIL, judge pass {table[(False, True)]:4}")
    print(f"  code FAIL, judge FAIL {table[(False, False)]:4}")


print("\n=== Part 1: code checks against the judge, on dev ===")
show_table("both checks, lenient judge", two_by_two(dev, code_passes, lenient))
show_table("both checks, strict judge", two_by_two(dev, code_passes, strict))

print("\nread first: code FAIL, judge pass (strict judge)")
for r in dev:
    if not code_passes(r.conv) and judge_passes(strict, r):
        print(f"  {r.trace.trace_id} planted={r.trace.seeded_failure}: {r.conv.answer}")
        print(f"    cited {[u.rsplit('/', 1)[1] for u in r.conv.sources]}, retrieved {[d['url'].rsplit('/', 1)[1] for d in r.conv.documents]}")

print("\nboth FAIL, but the label says PASS (strict judge)")
for r in dev:
    if r.human_pass and not code_passes(r.conv) and not judge_passes(strict, r):
        print(f"  {r.trace.trace_id} planted={r.trace.seeded_failure}: {r.conv.answer}")
        print(f"    cited {[u.rsplit('/', 1)[1] for u in r.conv.sources]}, retrieved {[d['url'].rsplit('/', 1)[1] for d in r.conv.documents]}")

disagree = [r for r in dev if code_passes(r.conv) and not judge_passes(lenient, r)]
print("\ncode pass, lenient judge FAIL, by language:", dict(Counter(r.trace.language for r in disagree)))
print("  label PASS on", sum(r.human_pass for r in disagree), "of", len(disagree))
english = Counter(r.conv.answer for r in disagree if r.trace.language == "en")
print("  English rows:", dict(english))

print("\nLimit (d): does agreement with code say anything if they share a signal?")
failed_a = [r for r in dev if not check_citation(r.conv)]
print(f"  strict judge fails {sum(not judge_passes(strict, r) for r in failed_a)} of {len(failed_a)} rows that check A fails: its rule contains check A")
m = rates([judge_passes(strict, r) for r in dev], [r.human_pass for r in dev])
print(f"  strict judge TNR against the labels: {m['tn']}/{m['tn'] + m['fp']} = {m['tnr']:.3f}")

print("\nLimit (b): stopping early changes what you can measure (strict judge)")
for label, keep in [("every row", lambda r: True),
                    ("rows passing check A", lambda r: check_citation(r.conv)),
                    ("rows passing both checks", lambda r: code_passes(r.conv))]:
    part = [r for r in dev if keep(r)]
    m = rates([judge_passes(strict, r) for r in part], [r.human_pass for r in part])
    print(f"  {label:25} n={len(part):3}  human FAIL rows={m['tn'] + m['fp']:2}  TNR={m['tn']}/{m['tn'] + m['fp']}")

print("\nLimit (c): random sample against disagreement queue (lenient judge, all 1,400 rows)")
all_verdicts = {id(r): judge_passes(lenient, r) for r in rows}
all_code = {id(r): code_passes(r.conv) for r in rows}
truth = rates([all_verdicts[id(r)] for r in rows], [r.human_pass for r in rows])
true_pass = sum(r.human_pass for r in rows) / len(rows)
print(f"  all rows       n=1400 FAIL=42   TPR {truth['tpr']:.3f}  TNR {truth['tnr']:.3f}  true pass rate {true_pass:.3f}")


def sample_rates(part, weights=None):
    weights = weights or [1.0] * len(part)
    v = [all_verdicts[id(r)] for r in part]
    h = [r.human_pass for r in part]
    w_pass = sum(w for w, x in zip(weights, h) if x)
    w_fail = sum(w for w, x in zip(weights, h) if not x)
    if not w_pass or not w_fail:
        return float("nan"), float("nan"), float("nan")
    tpr = sum(w for w, a, x in zip(weights, v, h) if a and x) / w_pass
    tnr = sum(w for w, a, x in zip(weights, v, h) if not a and not x) / w_fail
    # Apply the sample's rates to the pass rate the judge shows on all rows, as note 05 does.
    usable = tpr + tnr > 1
    return tpr, tnr, corrected_pass_rate(observed, tpr, tnr) if usable else float("nan")


def stratified_sample(rng):
    """Every row code failed, plus a random sample of the rest. Weights undo the known odds of selection."""
    picked = rng.sample(passed_code, 105)
    return failed_code + picked, [1.0] * len(failed_code) + [len(passed_code) / len(picked)] * len(picked)


def percentiles(values):
    kept = sorted(v for v in values if v == v)
    return kept[int(.025 * len(kept))], kept[int(.975 * len(kept))], len(values) - len(kept)


observed = sum(all_verdicts[id(r)] for r in rows) / len(rows)
print(f"  the lenient judge passes {observed:.3f} of all rows; the correction below starts from that")
rng = random.Random(SEED)
queue = [r for r in rows if all_code[id(r)] != all_verdicts[id(r)]]
failed_code = [r for r in rows if not all_code[id(r)]]
passed_code = [r for r in rows if all_code[id(r)]]
tpr, tnr, cor = sample_rates(queue)
print(f"  queue          n={len(queue)} FAIL={sum(not r.human_pass for r in queue)}  TPR {tpr:.3f}  TNR {tnr:.3f}  corrected pass rate: not valid, TPR + TNR is below 1")
print("  over 2,000 draws, 2.5th to 97.5th percentile:")
for name, draw in [("random, 105 rows", lambda: (rng.sample(rows, 105), None)),
                   (f"stratified, {len(failed_code) + 105} rows", lambda: stratified_sample(rng))]:
    results = [sample_rates(*draw()) for _ in range(2000)]
    t, n, c = zip(*results)
    tl, th, skipped = percentiles(t)
    nl, nh, _ = percentiles(n)
    cl, ch, _ = percentiles(c)
    print(f"    {name:22} TPR {tl:.2f}-{th:.2f}  TNR {nl:.2f}-{nh:.2f}  corrected pass rate {cl:.3f}-{ch:.3f}  draws with no FAIL row: {skipped}")


# %% part 2: slice the judge's errors by flag
def length_bucket(row):
    words = len(row.conv.answer.split())
    return "<=11 words" if words <= 11 else "12-13 words" if words <= 13 else ">=14 words"


FLAGS = {"language": lambda r: r.trace.language,
         "route": lambda r: r.trace.route,
         "length": length_bucket,
         "citation present": lambda r: "yes" if r.conv.sources else "no",
         "code check": lambda r: "passes" if code_passes(r.conv) else "fails"}


def slice_report(part, judge):
    lines, tests = [], []
    for flag, of in FLAGS.items():
        for level in sorted({of(r) for r in part}):
            inside = [r for r in part if of(r) == level]
            rest = [r for r in part if of(r) != level]
            a = rates([judge_passes(judge, r) for r in inside], [r.human_pass for r in inside])
            lines.append((flag, level, a))
            if rest:
                b = rates([judge_passes(judge, r) for r in rest], [r.human_pass for r in rest])
                if a["tp"] + a["fn"] and b["tp"] + b["fn"]:
                    tests.append((len(lines) - 1, "tpr", fisher(a["tp"], a["fn"], b["tp"], b["fn"])))
                if a["tn"] + a["fp"] and b["tn"] + b["fp"]:
                    tests.append((len(lines) - 1, "tnr", fisher(a["tn"], a["fp"], b["tn"], b["fp"])))
    adjusted = holm([t[2] for t in tests])
    print(f"{len(tests)} slice-against-rest tests; p is Holm-adjusted across all of them")
    print(f"{'flag':17}{'level':13}{'TPR':>9} {'95% CI':>10} {'p':>7}{'TNR':>7} {'95% CI':>10} {'p':>7}")

    def cell(k, n, p):
        low, high = wilson(k, n)
        interval = f"{low:.2f}-{high:.2f}" if n else "-"
        shown = "-" if p is None else "<.001" if p < .001 else f"{p:.3f}"
        return f"{k}/{n}", interval, shown

    for i, (flag, level, m) in enumerate(lines):
        p = {t[1]: q for t, q in zip(tests, adjusted) if t[0] == i}
        t1, t2, t3 = cell(m["tp"], m["tp"] + m["fn"], p.get("tpr"))
        n1, n2, n3 = cell(m["tn"], m["tn"] + m["fp"], p.get("tnr"))
        print(f"{flag:17}{level:13}{t1:>9} {t2:>10} {t3:>7}{n1:>7} {n2:>10} {n3:>7}")


print("\n=== Part 2: lenient judge by slice, on dev ===")
slice_report(dev, lenient)

print("\nare the length and route slices the language slice again? TPR, English rows only:")
english_rows = [r for r in dev if r.trace.language == "en"]
for flag in ("length", "route"):
    for level in sorted({FLAGS[flag](r) for r in english_rows}):
        m = rates([judge_passes(lenient, r) for r in english_rows if FLAGS[flag](r) == level],
                  [r.human_pass for r in english_rows if FLAGS[flag](r) == level])
        print(f"  {flag:7}{level:13}{m['tp']}/{m['tp'] + m['fn']}")


# %% part 3: code the critiques
def tag(row, judge):
    """One tag per row. A person would write these while reading: here the rules make them mechanical."""
    result = judge(row.conv)
    claims = [e["claim"] for e in result["evidence"]]
    substantive = [c for c in claims if c != "low overlap"]
    if not result["hallucination_detected"]:
        return "missed evidence" if not row.human_pass else "agreement, no flaw"
    if not substantive:
        return "should not count" if row.human_pass else "right verdict, wrong reason"
    if row.human_pass:
        return "different criterion"
    return "right verdict, padded reason" if "low overlap" in claims else "agreement, no flaw"


def reading_list(part, judge, rng):
    """Every disagreement, every agreed FAIL (they are rare), and 30 agreed PASS rows."""
    wrong = [r for r in part if judge_passes(judge, r) != r.human_pass]
    agreed_fail = [r for r in part if not judge_passes(judge, r) and not r.human_pass]
    agreed_pass = [r for r in part if judge_passes(judge, r) and r.human_pass]
    return wrong + agreed_fail + rng.sample(agreed_pass, min(30, len(agreed_pass)))


print("\n=== Part 3: calibration record, on dev ===")
reading_rng = random.Random(SEED)
for version, judge in [("v0 lenient", lenient), ("v1 no overlap rule", strict), ("v2 numbers vs cited docs", scoped)]:
    m = rates([judge_passes(judge, r) for r in dev], [r.human_pass for r in dev])
    read = reading_list(dev, judge, reading_rng)
    tags = Counter(tag(r, judge) for r in read)
    print(f"{version}: TPR {m['tpr']:.3f}  TNR {m['tnr']:.3f}  kappa {m['kappa']:.3f}  (read {len(read)} rows)")
    for name, count in tags.most_common():
        print(f"    {count:4}  {name}")

print("\ncannot occur with these judges, whatever the data: 'cited evidence not in input' and")
print("'reasoning supports one verdict, label says the other', because the verdict is bool(evidence).")
show_table("v2 against the code checks, on dev", two_by_two(dev, code_passes, scoped))

print("\n=== Test, once, for the version the dev record chose ===")
m = rates([judge_passes(scoped, r) for r in test], [r.human_pass for r in test])
print(f"v2: TPR {m['tp']}/{m['tp'] + m['fn']} = {m['tpr']:.3f}  TNR {m['tn']}/{m['tn'] + m['fp']} = {m['tnr']:.3f}  kappa {m['kappa']:.3f}")
tl, th = wilson(m["tn"], m["tn"] + m["fp"])
print(f"    TNR 95% Wilson interval {tl:.2f} to {th:.2f}")


# %% part 4: ONLINE. Needs a real model. Nothing below runs without --online and your own call_judge.
def call_judge(row, documents=None, cue=None):
    """Return {"verdict": "PASS"|"FAIL", "critique": str, "quotes": [exact strings from the documents]}.

    Call your judge model here, with `documents` in place of the row's own when given, and `cue`
    added to the prompt when given. Use a different model family from the one under test (note 05).
    """
    raise NotImplementedError("Wire call_judge to your own judge model before running --online.")


def shift_rate(before, after):
    flips = sum(b["verdict"] != a["verdict"] for b, a in zip(before, after))
    return flips, len(before), wilson(flips, len(before))


def cue_test(part, cue, mentions_cue, judge=call_judge):
    """Does a cue that should not matter move the verdict, and does the critique say so?

    The second no-cue run measures how often the judge flips on its own. Compare against that.
    """
    first = [judge(r) for r in part]
    again = [judge(r) for r in part]
    cued = [judge(r, cue=cue) for r in part]
    flipped = [c for f, c in zip(first, cued) if f["verdict"] != c["verdict"]]
    return {"noise": shift_rate(first, again), "cue": shift_rate(first, cued),
            "flipped_and_mentioned": (sum(mentions_cue(c["critique"]) for c in flipped), len(flipped)),
            "mentioned_overall": (sum(mentions_cue(c["critique"]) for c in cued), len(cued))}


def without(documents, sentences_kept):
    """The documents, keeping only sentences for which sentences_kept returns True."""
    out = []
    for doc in documents:
        kept = [s for s in re.split(r"(?<=[.!?])\s+", doc["text"]) if sentences_kept(s)]
        out.append({**doc, "text": " ".join(kept)})
    return out


def edit_test(part, judge=call_judge, seed=SEED):
    """Remove what the critique says it relied on. The control removes one sentence it did not quote."""
    rng = random.Random(seed)
    tested, flips, control_flips, no_quotes = 0, 0, 0, 0
    for row in part:
        first = judge(row)
        quotes = first.get("quotes") or []
        if first["verdict"] != "PASS" or not quotes:
            no_quotes += 1
            continue
        relied = lambda s: any(q in s or s in q for q in quotes)
        sentences = [s for d in row.conv.documents for s in re.split(r"(?<=[.!?])\s+", d["text"])]
        others = [s for s in sentences if not relied(s)]
        if len(others) == len(sentences) or not others:
            no_quotes += 1  # quote not found in the documents: tag it "cited evidence not in input"
            continue
        tested += 1
        flips += judge(row, documents=without(row.conv.documents, lambda s: not relied(s)))["verdict"] != "PASS"
        drop = rng.choice(others)
        control_flips += judge(row, documents=without(row.conv.documents, lambda s: s != drop))["verdict"] != "PASS"
    return {"tested": tested, "skipped": no_quotes, "flips": flips, "control_flips": control_flips}


parser = argparse.ArgumentParser()
parser.add_argument("--online", action="store_true", help="run part 4 against call_judge")
if parser.parse_args().online:
    cue = "A senior support agent wrote this answer."
    print(cue_test(dev[:100], cue, lambda text: "senior" in text.lower()))
    print(edit_test(dev[:100]))
else:
    print("\nPart 4 not run: it needs a real model. Wire call_judge and pass --online.")
