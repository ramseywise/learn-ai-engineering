# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scoring whole conversations against a rubric, for notes/15 and the multi-turn section of notes/06.

Run from this folder (a few seconds, standard library only, downloads nothing, no API key):
    uv run conversation_scoring_lab.py

Larkfield Staffing is made up. Its agents hold structured screening conversations in six verticals and score each one
against a four-item rubric. Every transcript, candidate, human label and scorer here is generated from SEED. The scorers
are stubs with planted behaviours, and no model is called. A stub reads a turn's `evidence` number, where a real scorer
would read the text. The kappa, abstention, shrinkage and gate code is real. The numbers describe these assumptions, not
any product, and the human labels follow a rule we wrote, so a scorer that follows the same rule agrees partly by
construction. Scoring real people for real shifts needs its own fairness and legal review, which this lab doesn't do.

Knobs worth changing are the capitalised constants at the top and each section's default arguments. Each section prints a table
and asserts the invariants it depends on.
"""
# %%
import json
import math
import random
import statistics
from dataclasses import dataclass, field

SEED = 11
BOOTSTRAPS = 400
GOLD_SET = 1200  # labelled conversations in the regression suite, section 5
RERUNS = 200  # repeats of the whole gate, section 5
WRONG_PRICE, ABSTAIN_PRICE = 10.0, 1.0  # assumed, section 2: a wrong verdict, and a follow-up call instead of a verdict
SCORE_MEAN, SCORE_SD = .9, 1.6  # true log-odds of a human PASS, section 3. A mean of .9 is about 65% PASS


@dataclass(frozen=True)
class Vertical:
    name: str
    share: float  # share of conversations
    labels: int  # human labels we can afford, section 3
    skip_cert: float  # how often the agent never asks the certification question, section 2
    bias: float  # the planted score shift on the log-odds, section 3: positive reads too kind
    cert: str


VERTICALS = [
    Vertical("warehouse", .40, 120, .05, .0, "forklift licence"),
    Vertical("hospitality", .22, 60, .35, .9, "food hygiene certificate"),
    Vertical("nursing", .10, 30, .02, -1.3, "nursing registration"),
    Vertical("trucking", .12, 15, .10, -.5, "heavy goods licence"),
    Vertical("childcare", .10, 10, .15, 1.5, "first-aid certificate"),
    Vertical("security", .06, 6, .25, -1.0, "guard licence"),
]
BY_NAME = {v.name: v for v in VERTICALS}
RUBRIC_BASE = {"experience": .8, "availability": 1.5, "safety": 2.2, "certification": 1.2}  # log-odds that an item holds


def expit(x):
    return 1 / (1 + math.exp(-x))


def clamp(x):
    return min(1.0, max(0.0, x))


def pick_vertical(rng):
    return rng.choices(VERTICALS, weights=[v.share for v in VERTICALS])[0]


# %% The transcript generator
@dataclass
class Turn:
    criterion: str  # a rubric item, or "rapport" for small talk
    question: str
    answer: str
    evidence: float  # how far this answer, read alone, supports the item: 0 against, 1 for
    conflicts_earlier: bool = False  # only a reader of the whole conversation can see this


@dataclass
class Conversation:
    id: int
    vertical: str
    pattern: str
    turns: list = field(default_factory=list)
    holds: dict = field(default_factory=dict)  # the hidden truth, which a real team doesn't have
    asked_cert: bool = True
    human_cert: str = "NOT_ASKED"  # PASS, FAIL or NOT_ASKED
    human: str = "FAIL"  # the overall verdict on the conversation


def rubric_rule(holds, conflict=False):
    """Must hold certification and safety, and at least one of experience and availability. The labellers' rule."""
    return not conflict and holds["certification"] and holds["safety"] and (holds["experience"] or holds["availability"])


def item_turn(rng, criterion, holds, cert_name, hedged=False, evidence=None):
    question = {"experience": "How long have you done this kind of work?", "availability": "Which shifts can you cover?",
                "safety": "What do you do when you see a safety problem?", "certification": f"Is your {cert_name} current?"}[criterion]
    if hedged:  # a hedge moves the evidence towards the middle and keeps only a weak link to the truth
        answer = {"certification": "I think so, I'd have to check the date."}.get(criterion, "It depends, I'd have to check.")
        return Turn(criterion, question, answer, clamp(rng.gauss(.60 if holds else .42, .09)))
    answer = {"experience": ("Six years, on two sites.", "A few weeks, a while ago."),
              "availability": ("Nights and weekends are fine.", "Only one morning a week."),
              "safety": ("I stop work and report it to the supervisor.", "I carry on, it usually sorts itself out."),
              "certification": ("Yes, renewed this spring.", "No, it lapsed two years ago.")}[criterion][0 if holds else 1]
    return Turn(criterion, question, answer, clamp(rng.gauss(.85 if holds else .15, .08)) if evidence is None else evidence)


def rapport_turn(rng):
    return Turn("rapport", "Thanks for making time. How has your week been?", "Great, thanks for asking, happy to be here.", clamp(rng.gauss(.78, .08)))


def converse(rng, cid, vertical, pattern="ordinary", may_skip=True, skip_if_unqualified=0.0, skip_override=None):
    """One screening conversation. `pattern` plants the case section 4 needs."""
    v = BY_NAME[vertical] if isinstance(vertical, str) else vertical
    fit = rng.gauss(0, 1)
    holds = {c: rng.random() < expit(base + 1.3 * fit) for c, base in RUBRIC_BASE.items()}
    conv = Conversation(cid, v.name, pattern)
    skip = v.skip_cert if skip_override is None else skip_override
    if not may_skip:
        skip = 0.0
    elif not holds["certification"]:
        skip = clamp(skip + skip_if_unqualified)

    turns = [rapport_turn(rng)]
    conflict = False
    if pattern == "late_disqualifier":  # strong all the way, then the last answer rules the candidate out
        holds = dict.fromkeys(RUBRIC_BASE, True) | {"certification": False}
        turns += [item_turn(rng, c, True, v.cert) for c in ("experience", "availability", "safety")]
        turns += [rapport_turn(rng), item_turn(rng, "certification", False, v.cert)]
    elif pattern == "recovery":  # the candidate misreads three questions, the agent rephrases, and the answers are good
        holds = dict.fromkeys(RUBRIC_BASE, True)
        for c in ("experience", "safety", "certification"):
            turns += [Turn(c, "(first asking)", "Sorry, I'm not sure what you mean by that.", clamp(rng.gauss(.15, .06))),
                      item_turn(rng, c, True, v.cert)]
        turns.append(item_turn(rng, "availability", True, v.cert))
    elif pattern == "contradiction":  # each answer reads fine alone, and the two can't both be true
        holds = dict.fromkeys(RUBRIC_BASE, True)
        conflict = True
        turns += [item_turn(rng, c, True, v.cert) for c in RUBRIC_BASE]
        turns.append(Turn("experience", "When did you start on the sites?", "I started there this spring.", clamp(rng.gauss(.74, .07)), conflicts_earlier=True))
    elif pattern == "padded":  # a weak candidate in a long, friendly conversation
        holds = {"experience": False, "availability": True, "safety": False, "certification": True}
        turns += [item_turn(rng, c, holds[c], v.cert) for c in RUBRIC_BASE]
        turns += [rapport_turn(rng) for _ in range(rng.randint(8, 12))]
    else:
        conv.asked_cert = rng.random() >= skip
        for c in RUBRIC_BASE:
            if c == "certification":
                if conv.asked_cert:
                    hedged = rng.random() < .30
                    turns.append(item_turn(rng, c, holds[c], v.cert, hedged=hedged))
                    flip = .20 if hedged else .03
                    conv.human_cert = "PASS" if holds[c] != (rng.random() < flip) else "FAIL"
            else:
                turns.append(item_turn(rng, c, holds[c], v.cert))
    conv.turns, conv.holds = turns, holds
    if pattern != "ordinary":
        conv.human_cert = "PASS" if holds["certification"] else "FAIL"
    conv.human = "PASS" if rubric_rule(holds, conflict) else "FAIL"
    return conv


# %% The agreement statistics. The lab implements these itself so the arithmetic is on the page
def weighted_kappa(a, b, categories=None, weights=None):
    """Chance-corrected agreement. weights: None (any miss counts the same), "linear" or "quadratic" (far misses cost more).

    kappa = 1 - observed disagreement / disagreement expected from the two marginals. It is undefined (nan) when chance
    alone predicts no disagreement, as when both raters give one label to every row.
    """
    categories = sorted(set(a) | set(b)) if categories is None else list(categories)
    index = {c: i for i, c in enumerate(categories)}
    k, n = len(categories), len(a)
    observed = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        observed[index[x]][index[y]] += 1
    row = [sum(observed[i]) for i in range(k)]
    col = [sum(observed[i][j] for i in range(k)) for j in range(k)]
    span = max(k - 1, 1)
    weight = {None: lambda i, j: float(i != j), "linear": lambda i, j: abs(i - j) / span,
              "quadratic": lambda i, j: ((i - j) / span) ** 2}[weights]
    seen = sum(weight(i, j) * observed[i][j] for i in range(k) for j in range(k)) / n
    expected = sum(weight(i, j) * row[i] * col[j] for i in range(k) for j in range(k)) / n / n
    return float("nan") if expected == 0 else 1 - seen / expected


def agreement(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a)


def bootstrap_kappa(rng, a, b, weights=None):
    n, values = len(a), []
    for _ in range(BOOTSTRAPS):
        rows = [rng.randrange(n) for _ in range(n)]
        value = weighted_kappa([a[i] for i in rows], [b[i] for i in rows], weights=weights)
        if value == value:
            values.append(value)
    values.sort()
    return values[int(.025 * len(values))], values[int(.975 * len(values))]


def rates(human, scorer, positive="PASS"):
    """TPR and TNR on the rows where human gave a verdict. PASS is the positive class, as in the note."""
    pos = [s == positive for h, s in zip(human, scorer) if h == positive]
    neg = [s != positive for h, s in zip(human, scorer) if h != positive]
    return sum(pos) / max(len(pos), 1), sum(neg) / max(len(neg), 1)


def from_confusion(tp, fn, fp, tn):
    return ["PASS"] * (tp + fn) + ["FAIL"] * (fp + tn), ["PASS"] * tp + ["FAIL"] * fn + ["PASS"] * fp + ["FAIL"] * tn


def check_kappa():
    # The two judges in note 15's script.
    assert round(weighted_kappa(*from_confusion(54, 6, 16, 24)), 2) == .52
    assert round(weighted_kappa(*from_confusion(75, 15, 7, 3)), 2) == .10
    labels = [1, 2, 3, 4, 5, 3, 3, 2]
    other = [2, 2, 3, 5, 4, 3, 1, 2]
    assert weighted_kappa(labels, labels) == 1.0
    assert round(weighted_kappa(labels, other, weights="linear"), 4) == .5238
    assert round(weighted_kappa(labels, other, weights="quadratic"), 4) == .6889
    assert abs(weighted_kappa(labels, other, weights="quadratic") - weighted_kappa(other, labels, weights="quadratic")) < 1e-12
    binary = (["PASS", "PASS", "FAIL", "PASS"], ["PASS", "FAIL", "FAIL", "PASS"])
    assert abs(weighted_kappa(*binary) - weighted_kappa(*binary, weights="quadratic")) < 1e-12  # two labels: weights change nothing
    assert math.isnan(weighted_kappa(["PASS"] * 5, ["PASS"] * 5))  # undefined, not perfect


# %% 1. Agreement on a skewed label
def agreement_section(n=400):
    rng = random.Random(SEED)
    # The safety item, on a skewed set: most candidates describe a safe procedure.
    truth = [rng.random() < .92 for _ in range(n)]
    polish = [rng.random() < .35 for _ in range(n)]  # a polished answer, which fools the two scorers built alike
    evidence = [clamp(rng.gauss(.80 if t else .25, .17)) for t in truth]
    human = ["PASS" if t != (rng.random() < .01) else "FAIL" for t in truth]
    second = ["PASS" if t != (rng.random() < .03) else "FAIL" for t in truth]
    lenient = ["FAIL" if e < .10 else "PASS" for e in evidence]
    careful = ["PASS" if e + rng.gauss(0, .14) >= .55 else "FAIL" for e in evidence]
    shared_read = [e + rng.gauss(0, .17) + (.45 if p else 0) for e, p in zip(evidence, polish)]
    twin_a = ["PASS" if r + rng.gauss(0, .03) >= .55 else "FAIL" for r in shared_read]
    twin_b = ["PASS" if r + rng.gauss(0, .03) >= .55 else "FAIL" for r in shared_read]

    print(f"1. Agreement on one rubric item, {n} generated conversations, {human.count('PASS') / n:.0%} human PASS")
    print("   pair                       raw   kappa  95% bootstrap     TPR   TNR")
    results = {}
    for name, a, b in [("second human vs human", second, human), ("lenient scorer vs human", lenient, human),
                       ("careful scorer vs human", careful, human), ("twin A vs human", twin_a, human),
                       ("twin A vs twin B", twin_a, twin_b)]:
        kappa, (low, high) = weighted_kappa(a, b), bootstrap_kappa(rng, a, b)
        tpr, tnr = rates(b, a)
        results[name] = dict(raw=agreement(a, b), kappa=kappa, tnr=tnr)
        print(f"   {name:25s} {agreement(a, b):.3f}  {kappa:5.2f}  [{low:5.2f}, {high:5.2f}]  {tpr:.2f}  {tnr:.2f}")
    print("   Raw agreement prefers the lenient scorer to the careful one, and kappa and TNR reverse that. The twins agree with")
    print("   each other because they share a blind spot, which says nothing about whether they agree with a person.")
    assert results["lenient scorer vs human"]["raw"] > results["careful scorer vs human"]["raw"]
    assert results["lenient scorer vs human"]["kappa"] < results["careful scorer vs human"]["kappa"]
    assert results["careful scorer vs human"]["tnr"] > results["lenient scorer vs human"]["tnr"] + .3
    assert results["twin A vs twin B"]["kappa"] > results["twin A vs human"]["kappa"]

    print("\n   One scorer with TPR 0.90 and TNR 0.80 at four base rates: kappa moves though the scorer hasn't changed")
    previous = 2.0
    for share in (.50, .80, .92, .98):
        tp, fn, fp, tn = share * .90, share * .10, (1 - share) * .20, (1 - share) * .80
        size = 100_000
        kappa = weighted_kappa(*from_confusion(*(round(x * size) for x in (tp, fn, fp, tn))))
        print(f"   human PASS {share:.0%}: raw {tp + tn:.3f}  kappa {kappa:.2f}")
        assert kappa < previous
        previous = kappa
    print("   So compare kappas on the same label mix, and read TPR and TNR beside them.")

    # A 1-to-5 grade, where the size of a miss matters. Two scorers with near-equal exact agreement.
    grades = rng.choices([1, 2, 3, 4, 5], weights=[.05, .15, .35, .30, .15], k=n)
    near = [g if rng.random() < .55 else max(1, min(5, g + rng.choice((-1, 1)))) for g in grades]
    far = [g if rng.random() < .58 else rng.choice([x for x in (1, 2, 3, 4, 5) if abs(x - g) >= 2]) for g in grades]
    print(f"\n   A 1-5 grade, {n} generated rows. The near scorer misses by one, the far scorer misses by two or more")
    print("   scorer   exact   kappa  linear  quadratic")
    row = {}
    for name, s in (("near", near), ("far", far)):
        row[name] = [weighted_kappa(s, grades, categories=range(1, 6), weights=w) for w in (None, "linear", "quadratic")]
        print(f"   {name:7s}  {agreement(s, grades):.3f}  {row[name][0]:5.2f}  {row[name][1]:6.2f}  {row[name][2]:9.2f}")
    assert row["near"][2] > row["far"][2] + .2
    return results


# %% 2. Not enough evidence is not a low score
def naive_cert(rng, conv):
    """Scores absence as zero, which is what an averaging rubric does when a question was never asked."""
    turn = next((t for t in conv.turns if t.criterion == "certification"), None)
    return "PASS" if turn is not None and turn.evidence + rng.gauss(0, .05) >= .5 else "FAIL"


def abstaining_cert(rng, conv, band=0.0):
    """ABSTAIN when nothing was asked, or when the answer sits inside the band around the threshold."""
    turn = next((t for t in conv.turns if t.criterion == "certification"), None)
    if turn is None:
        return "ABSTAIN"
    read = turn.evidence + rng.gauss(0, .05)
    if abs(read - .5) < band:
        return "ABSTAIN"
    return "PASS" if read >= .5 else "FAIL"


def expected_cost(wrong, abstained, n, wrong_price, abstain_price):
    return (wrong * wrong_price + abstained * abstain_price) / n


def batch(seed, n, **kwargs):
    rng = random.Random(seed)
    return [converse(rng, i, pick_vertical(rng), **kwargs) for i in range(n)], rng


def abstain_section(n=4000, wrong_price=WRONG_PRICE, abstain_price=ABSTAIN_PRICE):
    conversations, rng = batch(SEED + 1, n)
    print(f"\n2. A question never asked, {n} generated conversations. The certification item, scored against the hidden truth")
    print("   vertical     never asked  truly hold it  naive says hold  abstainer says hold  coverage")
    gaps = {}
    for v in VERTICALS:
        rows = [c for c in conversations if c.vertical == v.name]
        naive = [naive_cert(rng, c) for c in rows]
        abstain = [abstaining_cert(rng, c) for c in rows]
        scored = [a for a in abstain if a != "ABSTAIN"]
        truly = sum(c.holds["certification"] for c in rows) / len(rows)
        naive_rate, abstain_rate = naive.count("PASS") / len(rows), scored.count("PASS") / len(scored)
        never = sum(not c.asked_cert for c in rows) / len(rows)
        gaps[v.name] = dict(naive=truly - naive_rate, abstain=abs(truly - abstain_rate), never=never)
        print(f"   {v.name:12s} {never:10.0%}  {truly:13.0%}  {naive_rate:15.0%}  {abstain_rate:19.0%}  {len(scored) / len(rows):8.0%}")
    print("   The naive scorer makes hospitality look like the weakest vertical. The agent's skipped question is what it measured.")
    assert gaps["hospitality"]["naive"] > gaps["warehouse"]["naive"] + .1
    assert max(g["abstain"] for g in gaps.values()) < max(g["naive"] for g in gaps.values())

    print(f"\n   Coverage against error. Prices are assumed: a wrong verdict {wrong_price:.0f}, a follow-up call {abstain_price:.0f}")
    print("   scorer            coverage  error on scored  wrong  of them never asked  cost per conversation")
    table = []
    for label, band in [("naive", None), ("abstain, band 0", 0.0), ("abstain, band .05", .05), ("abstain, band .10", .10),
                        ("abstain, band .20", .20), ("abstain, band .30", .30), ("abstain, band .50", .50)]:
        rng_local = random.Random(SEED + 2)  # the same reading noise for every row of the table
        verdicts = [naive_cert(rng_local, c) if band is None else abstaining_cert(rng_local, c, band) for c in conversations]
        scored = [(c, v) for c, v in zip(conversations, verdicts) if v != "ABSTAIN"]
        wrong = [c for c, v in scored if (v == "PASS") != c.holds["certification"]]
        never = sum(not c.asked_cert for c in wrong)
        cost = expected_cost(len(wrong), n - len(scored), n, wrong_price, abstain_price)
        error = len(wrong) / len(scored) if scored else 0.0
        table.append(dict(label=label, band=band, coverage=len(scored) / n, error=error, cost=cost))
        print(f"   {label:17s} {len(scored) / n:8.1%}  {error:15.1%}  {len(wrong):5d}  {never:19d}  {cost:21.2f}")
    assert table[0]["coverage"] == 1.0 and table[1]["error"] < table[0]["error"]
    assert table[1]["coverage"] > table[3]["coverage"]  # the band really abstains
    assert all(a["coverage"] >= b["coverage"] for a, b in zip(table[1:], table[2:]))  # a wider band can only abstain more
    assert all(a["error"] >= b["error"] for a, b in zip(table[1:5], table[2:5]))
    best = min(table, key=lambda r: r["cost"])
    print(f"   Lowest cost at these prices: {best['label']}. A band of .50 abstains on nearly everything, and its error of 0 means")
    print("   nothing, which is why coverage is reported beside it. Change the prices at the top of the file and the best band moves.")

    # Two ways abstention can mislead on its own. Both are the agent's behaviour leaking into the score.
    worse, rng2 = batch(SEED + 3, n, skip_override=.60)
    errors = {}
    for label, group in (("current agent", conversations), ("agent that stops asking", worse)):
        verdicts = [abstaining_cert(rng2, c) for c in group]
        kept = [(c, v) for c, v in zip(group, verdicts) if v != "ABSTAIN"]
        errors[label] = sum((v == "PASS") != c.holds["certification"] for c, v in kept) / len(kept)
        print(f"   {label:24s} error on scored {errors[label]:5.1%}, coverage {len(kept) / len(group):4.0%}")
    print("   Error on scored rows can't see the second agent. Coverage has to be a tracked number of its own.")
    assert abs(errors["current agent"] - errors["agent that stops asking"]) < .02

    biased, rng3 = batch(SEED + 4, n, skip_if_unqualified=.40)
    verdicts = [abstaining_cert(rng3, c) for c in biased]
    scored = [v for v in verdicts if v != "ABSTAIN"]
    truly = sum(c.holds["certification"] for c in biased) / n
    print(f"   If the agent skips the question more for candidates without the certificate: truly hold it {truly:.0%},")
    print(f"   abstainer says {scored.count('PASS') / len(scored):.0%}. Abstaining stops the false fails, and the rows left are no longer a fair sample.")
    assert scored.count("PASS") / len(scored) > truly + .03
    return table


# %% 3. One threshold or one per vertical. The method and its derivation are in DS 01/13, "When customers differ"
def fit_offset(scores, labels):
    """The log-odds offset that makes expected passes equal observed ones, by bisection, with its approximate variance.

    Same fit as data-science/01-classical-ml/practice/tenant_thresholds.py. With all labels one way there is no finite
    answer, so `finite` is False and the fit aims half a label from the edge.
    """
    events, n = sum(labels), len(labels)
    finite = 0 < events < n
    target = events if finite else (.5 if events == 0 else n - .5)
    low, high = -25.0, 25.0
    for _ in range(50):
        mid = (low + high) / 2
        if sum(expit(s + mid) for s in scores) < target:
            low = mid
        else:
            high = mid
    d = (low + high) / 2
    information = sum(expit(s + d) * (1 - expit(s + d)) for s in scores)
    return d, 1 / max(information, 1e-9), finite


def shrink_offsets(fits):
    """Pool towards the pooled offset. The note's tau^2 by moments, with the shared answer moved from zero to `center`."""
    usable = [(d, var) for d, var, finite in fits.values() if finite]
    center = sum(d / var for d, var in usable) / sum(1 / var for _, var in usable)
    tau2 = max(sum((((d - center) ** 2) - var) / var for d, var in usable) / sum(1 / var for _, var in usable), 0.0)
    return {name: center + (d - center) * tau2 / (tau2 + var) for name, (d, var, _) in fits.items()}, tau2, center


def regret(zs, bias, offset):
    """Expected extra wrong verdicts per conversation above verdicts from the true probability. Uses no sampled label."""
    extra = 0.0
    for z in zs:
        p = expit(z)
        passed = z + bias + offset >= 0
        extra += ((1 - p) if passed else p) - min(p, 1 - p)
    return extra / len(zs)


def calibration_run(seeds, test, draw_offsets, scale):
    """Regret per vertical under one shared offset, each vertical alone, alone with a fallback, and shrunk."""
    totals = {v.name: dict.fromkeys(("shared", "alone", "fallback", "shrunk"), 0.0) for v in VERTICALS}
    tau2s, no_fit = [], 0
    for seed in range(seeds):
        rng = random.Random(SEED * 1000 + seed)
        biases = {v.name: (rng.gauss(0, scale) if draw_offsets else v.bias * scale) + 0.0 for v in VERTICALS}
        data, fits = {}, {}
        for v in VERTICALS:
            zs = [rng.gauss(SCORE_MEAN, SCORE_SD) for _ in range(v.labels)]
            scores = [z + biases[v.name] for z in zs]
            ys = [rng.random() < expit(z) for z in zs]
            data[v.name] = (scores, ys)
            fits[v.name] = fit_offset(scores, ys)
        all_scores = [s for scores, _ in data.values() for s in scores]
        all_labels = [y for _, ys in data.values() for y in ys]
        shared, _, _ = fit_offset(all_scores, all_labels)
        shrunk, tau2, _ = shrink_offsets(fits)
        tau2s.append(tau2)
        for v in VERTICALS:
            d, _, finite = fits[v.name]
            no_fit += not finite
            literal = d if finite else (-30.0 if d < 0 else 30.0)  # the fit taken literally: all PASS, so pass everyone
            zs = [rng.gauss(SCORE_MEAN, SCORE_SD) for _ in range(test)]
            for method, offset in (("shared", shared), ("alone", literal), ("fallback", d if finite else shared), ("shrunk", shrunk[v.name])):
                totals[v.name][method] += regret(zs, biases[v.name], offset) / seeds
    methods = ("shared", "alone", "fallback", "shrunk")
    weighted = {m: sum(v.share * totals[v.name][m] for v in VERTICALS) for m in methods}
    small = [v for v in VERTICALS if v.labels <= 15]
    smalls = {m: statistics.mean(totals[v.name][m] for v in small) for m in methods}
    return totals, weighted, smalls, tau2s, no_fit


def calibration_section(seeds=200, test=500, spread=1.0):
    print(f"\n3. One threshold or one per vertical. {seeds} seeds, {test} fresh generated rows per vertical, with few labels per vertical")
    print("   Method: fit one log-odds offset per vertical and shrink towards the pooled fit. Derivation in DS 01/13, 'When customers differ'.")
    summary = {}
    for label, draw, scale in ((f"offsets drawn fresh each seed, sd {spread}", True, spread), ("the planted offsets, the same every seed", False, spread), ("control: no vertical differs", False, 0.0)):
        totals, weighted, smalls, tau2s, no_fit = calibration_run(seeds, test, draw, scale)
        print(f"\n   {label}. Mean tau^2 {statistics.mean(tau2s):.2f}, sd {statistics.stdev(tau2s):.2f}. {no_fit} of {seeds * len(VERTICALS)} fits had no finite answer")
        print("   vertical     labels  bias  shared  alone  alone+fallback  shrunk")
        for v in VERTICALS:
            t = totals[v.name]
            shown = "drawn" if draw else f"{v.bias * scale + 0.0:5.1f}"
            print(f"   {v.name:12s} {v.labels:6d} {shown}  {t['shared']:6.3f}  {t['alone']:5.3f}  {t['fallback']:14.3f}  {t['shrunk']:6.3f}")
        print(f"   traffic-weighted          {weighted['shared']:8.3f}  {weighted['alone']:5.3f}  {weighted['fallback']:14.3f}  {weighted['shrunk']:6.3f}")
        print(f"   the three smallest, mean      {smalls['shared']:6.3f}  {smalls['alone']:5.3f}  {smalls['fallback']:14.3f}  {smalls['shrunk']:6.3f}")
        summary[label] = dict(weighted=weighted, smalls=smalls, totals=totals)
    drawn, planted, control = summary.values()
    assert drawn["weighted"]["shrunk"] < drawn["weighted"]["shared"]
    assert drawn["smalls"]["shrunk"] < drawn["smalls"]["alone"]  # the case for pooling is the small verticals
    assert drawn["smalls"]["shrunk"] < drawn["smalls"]["fallback"] and control["smalls"]["shrunk"] < control["smalls"]["fallback"] / 5
    assert control["weighted"]["shrunk"] < control["weighted"]["alone"]  # no real differences: alone pays for noise, pooling doesn't
    print("\n   Regret is extra wrong verdicts per conversation above using the true probability. We planted a pure shift, which is")
    print("   what one offset can fix. A vertical whose score ranks differently needs its own check, and this lab doesn't run one.")
    print("   Shrinkage has a price: it pulls a truly far-out vertical back towards the pack. Read nursing in the second table.")
    return summary


# %% 4. Score the conversation, or average the turns
def turn_score(rng, turn):
    """A per-turn scorer sees one turn. Its signature is the limit: it can't know about any other turn."""
    return clamp(turn.evidence + rng.gauss(0, .04))


def mean_of_turns(rng, conv):
    return statistics.mean(turn_score(rng, t) for t in conv.turns)


def min_of_turns(rng, conv):
    return min(turn_score(rng, t) for t in conv.turns)


def whole_conversation(rng, conv, miss=.10):
    """Reads the transcript in order: the last answer per item stands, then the rubric rule. It sometimes loses the thread."""
    careless = rng.random() < miss
    state = {}
    for t in (reversed(conv.turns) if careless else conv.turns):  # careless: the first answer wins instead of the last
        if t.criterion != "rapport":
            state[t.criterion] = turn_score(rng, t) >= .5
    if any(c not in state for c in RUBRIC_BASE):
        return "ABSTAIN"
    conflict = not careless and any(t.conflicts_earlier for t in conv.turns)
    return "PASS" if rubric_rule(state, conflict) else "FAIL"


def best_threshold(rng, conversations, statistic):
    scored = [(statistic(rng, c), c.human == "PASS") for c in conversations]
    grid = [i / 100 for i in range(5, 96)]
    return max(grid, key=lambda t: sum((s >= t) == y for s, y in scored))


PATTERNS = {"ordinary": .70, "late_disqualifier": .075, "recovery": .075, "contradiction": .075, "padded": .075}


def show_transcript(rng, conv):
    print(f"   A generated {conv.pattern} conversation, {conv.vertical}, human says {conv.human}:")
    for t in conv.turns:
        print(f"     {turn_score(rng, t):.2f}  [{t.criterion:13s}] {t.answer}")


def turn_section(n=3000):
    rng = random.Random(SEED + 5)
    # Both per-turn rules get their best threshold on ordinary rows, so they aren't handicapped on the rows they were built for.
    dev = [converse(rng, i, pick_vertical(rng), may_skip=False) for i in range(800)]
    t_mean, t_min = best_threshold(rng, dev, mean_of_turns), best_threshold(rng, dev, min_of_turns)
    names, weights = zip(*PATTERNS.items())
    conversations = [converse(rng, i, pick_vertical(rng), pattern=rng.choices(names, weights=weights)[0], may_skip=False) for i in range(n)]
    verdicts = {"mean": [], "min": [], "whole": []}
    for c in conversations:
        verdicts["mean"].append("PASS" if mean_of_turns(rng, c) >= t_mean else "FAIL")
        verdicts["min"].append("PASS" if min_of_turns(rng, c) >= t_min else "FAIL")
        verdicts["whole"].append(whole_conversation(rng, c))
    assert "ABSTAIN" not in verdicts["whole"]  # may_skip=False: every item was asked

    print(f"\n4. Mean of turns, min of turns, or the whole conversation. {n} generated conversations, thresholds {t_mean:.2f} and {t_min:.2f} tuned on ordinary rows")
    show_transcript(rng, next(c for c in conversations if c.pattern == "late_disqualifier"))
    print(f"   The mean of these turns clears the {t_mean:.2f} threshold, so a mean-of-turns scorer passes it.\n")
    print("   pattern            rows  human PASS  mean right  min right  whole right  mean and whole differ")
    table = {}
    for pattern in names:
        rows = [i for i, c in enumerate(conversations) if c.pattern == pattern]
        humans = [conversations[i].human for i in rows]
        accuracy = {k: sum(verdicts[k][i] == conversations[i].human for i in rows) / len(rows) for k in verdicts}
        differ = sum(verdicts["mean"][i] != verdicts["whole"][i] for i in rows) / len(rows)
        table[pattern] = accuracy
        print(f"   {pattern:17s}  {len(rows):4d}  {humans.count('PASS') / len(rows):10.0%}  {accuracy['mean']:10.0%}  {accuracy['min']:9.0%}  {accuracy['whole']:11.0%}  {differ:21.0%}")
    humans = [c.human for c in conversations]
    kappas = {k: weighted_kappa(verdicts[k], humans) for k in verdicts}
    print(f"   all rows: kappa against human, mean {kappas['mean']:.2f}, min {kappas['min']:.2f}, whole {kappas['whole']:.2f}")
    print("   The whole scorer follows the labellers' rule by construction, so its lead is what the mean can't express, not a")
    print("   measurement of any whole-conversation judge. Min fixes the late failure and breaks on the recovery.")

    # The scores themselves, read with their own rng so the table above doesn't move.
    read = random.Random(SEED + 9)
    means, mins, right = {}, {}, {}
    for pattern in names:
        rows = [c for c in conversations if c.pattern == pattern]
        m, low = [mean_of_turns(read, c) for c in rows], [min_of_turns(read, c) for c in rows]
        means[pattern] = statistics.mean(m)
        mins[pattern] = statistics.mean(low)
        right[pattern] = (sum((x >= .50) == (c.human == "PASS") for x, c in zip(m, rows)) / len(rows),
                          sum((x >= .80) == (c.human == "PASS") for x, c in zip(low, rows)) / len(rows))
    print("\n   Can another threshold rescue a per-turn score? The human verdicts don't follow the order of the scores")
    print("   pattern            human PASS  mean score  min score  right with mean >= .50  right with min >= .80")
    for pattern in names:
        rows = [c for c in conversations if c.pattern == pattern]
        share = sum(c.human == "PASS" for c in rows) / len(rows)
        print(f"   {pattern:17s}  {share:10.0%}  {means[pattern]:10.2f}  {mins[pattern]:9.2f}  {right[pattern][0]:22.0%}  {right[pattern][1]:21.0%}")
    print("   A repaired conversation (all PASS) has a lower mean than the padded and late-failure ones (all FAIL), and a")
    print("   contradictory one (all FAIL) scores above ordinary rows. A cut that rescues one of them gives up ordinary rows.")
    assert table["late_disqualifier"]["mean"] < table["late_disqualifier"]["whole"] - .3
    assert table["recovery"]["min"] < table["recovery"]["whole"] - .3
    assert table["contradiction"]["mean"] < .3 and table["padded"]["mean"] < table["padded"]["whole"]
    assert table["contradiction"]["whole"] > .8
    assert means["recovery"] < min(means["padded"], means["late_disqualifier"]) and means["contradiction"] > means["ordinary"]
    return table, kappas


# %% 5. A paired gate for a scorer change. Conventions from notes/10: run then assert, three answers plus rerun
def run_phase(seed, n, change="planted", broken_vertical="trucking", drop=2.0):
    """Phase 1. The same labelled conversations scored by both versions. In a real suite this writes results.jsonl."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        v = pick_vertical(rng)
        human = rng.random() < .55
        signal = 1.0 if human else -1.0
        difficulty = rng.gauss(0, .70)  # how hard this conversation is to read, shared by both versions: this is why pairing helps
        base = signal + difficulty + rng.gauss(0, .65)
        if change == "noop":
            candidate = base + rng.gauss(0, .15)  # the same scorer run again: most reads repeat, a few near the line flip
        else:
            candidate = signal + difficulty + rng.gauss(0, .15)  # the new prompt reads a little more cleanly everywhere
            if v.name == broken_vertical and not human:
                candidate += drop  # and stops noticing a lapsed licence in one vertical
        rows.append(dict(id=i, vertical=v.name, human=human, baseline=int((base >= 0) == human), candidate=int((candidate >= 0) == human),
                         pass_base=base >= 0, pass_cand=candidate >= 0, error=rng.random() < .005))
    return rows


def paired_ci(d, z):
    mean = sum(d) / len(d)
    se = math.sqrt(sum((x - mean) ** 2 for x in d) / (len(d) - 1) / len(d))
    return mean, mean - z * se, mean + z * se


def verdict(low, high, floor):
    return "block" if high < floor else "pass" if low >= floor else "inconclusive"


def assert_phase(rows, overall_floor=-.03, slice_floor=-.10, min_slice=20, max_error_rate=.02, family_wise=True):
    """Phase 2: free and deterministic. Emits the gate shape from notes/10. A thin slice is never a pass."""
    scored = [r for r in rows if not r["error"]]
    errors = len(rows) - len(scored)
    if errors / len(rows) > max_error_rate:
        return dict(gate="scorer_change", verdict="rerun", passed=False, rows_scored=len(scored), errors=errors, next_action="Fix the run. No verdict on the scorer.")
    overall = paired_ci([r["candidate"] - r["baseline"] for r in scored], 1.96)
    names = sorted({r["vertical"] for r in scored})
    alpha = .05 / len(names) if family_wise else .05  # Bonferroni across the slices: see notes/09, "Too many slices"
    z = statistics.NormalDist().inv_cdf(1 - alpha / 2)
    slices = []
    for name in names:
        d = [r["candidate"] - r["baseline"] for r in scored if r["vertical"] == name]
        if len(d) < min_slice:
            slices.append(dict(slice=name, n=len(d), verdict="too few rows"))
            continue
        mean, low, high = paired_ci(d, z)
        slices.append(dict(slice=name, n=len(d), delta=round(mean, 3), ci=[round(low, 3), round(high, 3)], verdict=verdict(low, high, slice_floor)))
    blocked = [s for s in slices if s["verdict"] == "block"]
    unsure = [s["slice"] for s in slices if s["verdict"] in ("inconclusive", "too few rows")]
    overall_verdict = verdict(overall[1], overall[2], overall_floor)
    final = "block" if blocked or overall_verdict == "block" else "inconclusive" if unsure or overall_verdict == "inconclusive" else "pass"
    action = f"Read the FAIL rows in {blocked[0]['slice']}" if blocked else f"Too little evidence for {', '.join(unsure)}: grow those slices or have a person read them" if unsure else "None"
    return dict(gate="scorer_change", verdict=final, passed=final == "pass", rows_scored=len(scored), errors=errors,
                metrics=dict(accuracy_delta=dict(value=round(overall[0], 3), ci=[round(overall[1], 3), round(overall[2], 3)], verdict=overall_verdict)),
                worst_slices=sorted(slices, key=lambda s: s.get("delta", 0))[:2], all_slices=slices, next_action=action)


def unpaired_ci(a, b, z=1.96):
    """What you'd compute from two separate pass rates. It ignores that the rows are the same conversations."""
    pa, pb = sum(a) / len(a), sum(b) / len(b)
    se = math.sqrt(pa * (1 - pa) / len(a) + pb * (1 - pb) / len(b))
    return pb - pa, pb - pa - z * se, pb - pa + z * se


def gate_section(n=GOLD_SET, reruns=RERUNS):
    print(f"\n5. A regression gate for a scorer prompt change. {n} generated conversations with human labels, both versions on the same rows")
    rows = run_phase(SEED + 6, n)
    scored = [r for r in rows if not r["error"]]
    base = [r["baseline"] for r in scored]
    cand = [r["candidate"] for r in scored]
    print(f"   overall accuracy, baseline {sum(base) / len(base):.3f}, candidate {sum(cand) / len(cand):.3f}")
    print(f"   overall pass rate, baseline {sum(r['pass_base'] for r in scored) / len(scored):.3f}, candidate {sum(r['pass_cand'] for r in scored) / len(scored):.3f}")
    report = assert_phase(rows)
    print("   vertical      rows   delta  family-wise CI       verdict")
    for s in report["all_slices"]:
        ci = f"[{s['ci'][0]:+.3f}, {s['ci'][1]:+.3f}]" if "ci" in s else ""
        print(f"   {s['slice']:12s} {s['n']:5d}  {s.get('delta', 0):+.3f}  {ci:19s}  {s['verdict']}")
    overall = report["metrics"]["accuracy_delta"]
    overall_ci = f"[{overall['ci'][0]:+.3f}, {overall['ci'][1]:+.3f}]"
    print(f"   overall      {report['rows_scored']:5d}  {overall['value']:+.3f}  {overall_ci:19s}  {overall['verdict']}   (floor -0.03; slice floor -0.10)")
    print("   what the gate emits:")
    emitted = {k: v for k, v in report.items() if k != "all_slices"}
    print("   " + json.dumps(emitted))
    # The headline clears it, the slice stops it. This holds for this SEED's draw of rows, not for every seed.
    assert overall["verdict"] == "pass" and report["verdict"] != "pass", f"SEED {SEED}'s draw of rows tripped this, not a gate bug: the story needs a clean overall verdict, and this draw's is {overall['verdict']} {overall_ci}"

    paired = paired_ci([c - b for b, c in zip(base, cand)], 1.96)
    apart = unpaired_ci(base, cand)
    print(f"\n   Why paired: all {len(scored)} scored rows at 95%, paired CI width {paired[2] - paired[1]:.3f}, unpaired on the same rows {apart[2] - apart[1]:.3f}")
    assert paired[2] - paired[1] < apart[2] - apart[1]

    # A thin slice is never a pass: one big clean slice plus five clean rows, so thinness is the only thing wrong.
    clean = dict(baseline=1, candidate=1, error=False)
    thin = assert_phase([dict(clean, vertical="big") for _ in range(200)] + [dict(clean, vertical="thin") for _ in range(5)])
    assert thin["verdict"] == "inconclusive" and not thin["passed"]

    small = assert_phase(run_phase(SEED + 7, 300))
    assert small["verdict"] != "pass"
    worst = small["worst_slices"][0]
    print(f"   The same change on {300} rows: gate says {small['verdict']}, worst slice {worst['slice']} n={worst['n']} {worst.get('ci', '')}. {small['next_action']}")

    print(f"\n   {reruns} reruns of the whole gate, fresh rows each time")
    print("   change, slice CIs                         overall blocks  gate blocks  gate passes  inconclusive")
    outcome = {}
    for label, change, family_wise in (("planted regression, Bonferroni", "planted", True), ("no change, Bonferroni", "noop", True), ("no change, plain 95% per slice", "noop", False)):
        counts = dict(block=0, passed=0, unsure=0, overall=0)
        for seed in range(reruns):
            result = assert_phase(run_phase(SEED * 7 + seed, n, change=change), family_wise=family_wise)
            counts["block"] += result["verdict"] == "block"
            counts["passed"] += result["verdict"] == "pass"
            counts["unsure"] += result["verdict"] == "inconclusive"
            counts["overall"] += result["metrics"]["accuracy_delta"]["verdict"] == "block"
        outcome[label] = counts
        print(f"   {label:40s} {counts['overall'] / reruns:15.1%}  {counts['block'] / reruns:11.1%}  {counts['passed'] / reruns:11.1%}  {counts['unsure'] / reruns:12.1%}")
    assert outcome["planted regression, Bonferroni"]["block"] > .8 * reruns, "this suite is too small to block the planted regression"
    assert outcome["planted regression, Bonferroni"]["overall"] < .1 * reruns
    assert outcome["no change, Bonferroni"]["block"] <= .02 * reruns

    bonferroni, plain = outcome["no change, Bonferroni"], outcome["no change, plain 95% per slice"]
    cost = (plain["passed"] - bonferroni["passed"]) / reruns
    saved = (plain["block"] - bonferroni["block"]) / reruns
    print(f"   Bonferroni costs {cost * 100:.1f} points of no-change passes here and {'prevents no false blocks' if not saved else f'prevents {saved * 100:.1f} points of false blocks'} at this floor.")

    infra = run_phase(SEED + 8, n)
    for r in infra[:n // 20]:
        r["error"] = True
    assert assert_phase(infra)["verdict"] == "rerun"
    print("   With 5% of rows errored by infrastructure the gate says rerun, not block. The same rule as notes/10.")
    return report, outcome


# %%
def main():
    check_kappa()
    print("Larkfield Staffing is fictional. All data is generated from a seed and the scorers are stubs with planted behaviour.\n")
    agreement_section()
    abstain_section()
    calibration_section()
    turn_section()
    gate_section()
    print("\nAll invariants held.")


if __name__ == "__main__":
    main()
