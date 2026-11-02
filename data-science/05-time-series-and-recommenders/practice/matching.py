"""Generated bank lines and invoices for notes/04, plus blocking, pair features and ranking metrics.

Nothing here comes from a real ledger: every supplier name, invoice and payment is drawn from a seeded
random generator, so the matching problem is known exactly and the true links are available for scoring.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

SYLLABLES = "bro ka lin mor ven ta sel dru fen hal ost rik vel mar tor nes qui pel zan or".split()
TRADES = ["Joinery", "Freight", "Packaging", "Catering", "Electrical", "Cleaning", "Print", "Timber", "Tooling", "Software"]
SUFFIX = ["Ltd", "GmbH", "BV", "Oy", "AS"]
KINDS = ["single", "batch", "part", "none"]
FEATURES = ["amount_rel_diff", "amount_exact", "amount_near", "days_since_issue", "days_from_due",
            "name_sim", "ref_digits", "amount_rank", "name_rank", "n_candidates"]


def _names(rng, n):
    out = set()
    while len(out) < n:
        stem = "".join(rng.choice(SYLLABLES, rng.integers(2, 4))).capitalize()
        out.add(f"{stem} {rng.choice(TRADES)} {rng.choice(SUFFIX)}")
    return sorted(out)


def _mangle(name, rng):
    """A bank descriptor: upper case, truncated, sometimes with the legal suffix gone or a typing slip."""
    s = name.upper()
    if rng.random() < .5:
        s = s.rsplit(" ", 1)[0]
    if rng.random() < .25:
        s = s.split(" ")[0]
    if rng.random() < .25 and len(s) > 5:
        i = rng.integers(1, len(s) - 2)
        s = s[:i] + s[i + 1] + s[i] + s[i + 2:]
    return s[:18]


def _reference(number, rng):
    """Most payers leave the invoice number out. Some type it with a digit wrong."""
    u = rng.random()
    if u < .55:
        return ""
    digits = str(number)
    if u < .85:
        return f"INV {digits}"
    i = rng.integers(len(digits))
    return f"RE {digits[:i]}{(int(digits[i]) + 1) % 10}{digits[i + 1:]}"


def make_ledger(seed=0, n_suppliers=300, n_invoices=4000, days=540):
    """Return invoices, bank lines, and the true links between them."""
    rng = np.random.default_rng(seed)
    names = _names(rng, n_suppliers)
    weight = 1 / np.arange(1, n_suppliers + 1) ** .8
    typical = np.round(np.exp(rng.normal(6.2, 1.1, n_suppliers)), 2)
    recurring = rng.random(n_suppliers) < .3                     # flat monthly fee, same amount every time
    terms = rng.choice([14, 30, 30, 60], n_suppliers)

    sup = rng.choice(n_suppliers, n_invoices, p=weight / weight.sum())
    issued = np.sort(rng.integers(0, days, n_invoices))
    amt = np.where(recurring[sup], typical[sup], np.round(typical[sup] * np.exp(rng.normal(0, .5, n_invoices)), 2))
    round_up = rng.random(n_invoices) < .15                      # many suppliers bill round sums
    amt = np.where(round_up & ~recurring[sup], np.round(amt / 50) * 50 + 50, amt)
    invoices = pd.DataFrame({"invoice": np.arange(n_invoices), "supplier": sup, "name": np.array(names)[sup],
                             "number": rng.integers(100000, 999999, n_invoices), "issued": issued,
                             "due": issued + terms[sup], "amount": amt})

    lines, links = [], []
    unpaid = rng.permutation(n_invoices)
    i, line = 0, 0

    def add(amount, day, supplier, ref_number, kind, targets):
        nonlocal line
        hidden = rng.random() < .15                              # paid through a processor that hides the name
        label = f"PAYPROC*{rng.integers(1000, 9999)}" if hidden else _mangle(names[supplier], rng)
        ref = _reference(ref_number, rng) if ref_number is not None else ""
        lines.append(dict(line=line, text=f"{label} {ref}".strip(), amount=round(float(amount), 2), day=int(day), kind=kind))
        links.extend((line, t) for t in targets)
        line += 1

    while i < len(unpaid):
        row = invoices.iloc[unpaid[i]]
        pay_day = row.due + rng.integers(-10, 25)
        kind = rng.choice(["single", "batch", "part"], p=[.84, .08, .08])
        if kind == "batch":
            mates = invoices[(invoices.supplier == row.supplier) & (invoices.issued <= pay_day)
                             & (invoices.issued > pay_day - 90) & invoices.invoice.isin(unpaid[i + 1:])]
            n_extra = min(len(mates), rng.integers(1, 4))
            if n_extra == 0:
                kind = "single"
            else:
                extra = mates.sample(n_extra, random_state=int(rng.integers(1 << 30)))
                group = [row.invoice, *extra.invoice]
                add(row.amount + extra.amount.sum(), pay_day, row.supplier, None, "batch", group)
                unpaid = np.array([u for u in unpaid if u not in set(extra.invoice)])
                i += 1
                continue
        if kind == "part":
            first = round(float(row.amount) * rng.uniform(.3, .7), 2)
            add(first, pay_day, row.supplier, row.number, "part", [row.invoice])
            add(row.amount - first, pay_day + rng.integers(10, 40), row.supplier, row.number, "part", [row.invoice])
            i += 1
            continue
        u = rng.random()                                         # discounts and bank charges move the amount
        amount = row.amount * .98 if u < .08 else row.amount - rng.choice([1.5, 2.5, 5.0]) if u < .16 else row.amount
        add(amount, pay_day, row.supplier, row.number, "single", [row.invoice])
        i += 1

    n_none = int(.1 * line)                                       # payroll, tax and bank fees have no invoice
    for _ in range(n_none):
        label = rng.choice(["PAYROLL RUN", "TAX OFFICE", "BANK CHARGES", "CARD SETTLEMENT", "RENT STANDING ORDER"])
        lines.append(dict(line=line, text=str(label), amount=round(float(np.exp(rng.normal(6.5, 1.2))), 2),
                          day=int(rng.integers(0, days + 40)), kind="none"))
        line += 1
    lines = pd.DataFrame(lines).sort_values("day").reset_index(drop=True)
    links = pd.DataFrame(links, columns=["line", "invoice"])
    return invoices, lines, links


def ref_digits(numbers, text):
    """Digit positions that agree between each invoice number and a six-digit reference in the text.

    Returns -1 for every invoice if the text holds no reference, which is missing information, not disagreement.
    """
    found = re.search(r"\b\d{6}\b", text)
    if not found:
        return np.full(len(numbers), -1)
    ref = int(found.group())
    n, agree = numbers.copy(), np.zeros(len(numbers), int)
    for _ in range(6):
        agree += (n % 10) == (ref % 10)
        n, ref = n // 10, ref // 10
    return agree


class Similarity:
    """Character trigram TF-IDF cosine between bank text and supplier name."""

    def __init__(self, invoices, lines):
        self.names = sorted(invoices.name.unique())
        self.index = {n: i for i, n in enumerate(self.names)}
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 3), lowercase=True)
        self.N = self.vec.fit_transform(self.names)
        labels = lines.text.str.replace(r"\b(INV|RE)\s+\d+", "", regex=True)
        self.T = self.vec.transform(labels)

    def line_to_names(self, row):
        return np.asarray((self.T[row] @ self.N.T).todense()).ravel()


def block(invoices, lines, window=120, amount_tol=.03, name_min=.25, ref_min=5, keys=("amount", "name", "ref")):
    """Candidate pairs for each bank line.

    The date window applies to every key: only invoices issued in the `window` days before the payment.
    The other keys are alternatives, joined by OR, inside that window. With no keys the window alone decides.
    """
    sim = Similarity(invoices, lines)
    order = invoices.sort_values("issued")
    issued, amount = order.issued.to_numpy(), order.amount.to_numpy()
    numbers, idx = order.number.to_numpy(), order.invoice.to_numpy()
    name_id = order.name.map(sim.index).to_numpy()
    rows = []
    for r, ln in enumerate(lines.itertuples(index=False)):
        lo, hi = np.searchsorted(issued, ln.day - window), np.searchsorted(issued, ln.day, side="right")
        if lo == hi:
            continue
        sims = sim.line_to_names(r)[name_id[lo:hi]]
        rel = np.abs(amount[lo:hi] - ln.amount) / np.maximum(amount[lo:hi], 1)
        ref = ref_digits(numbers[lo:hi], ln.text)
        keep = np.zeros(hi - lo, bool) if keys else np.ones(hi - lo, bool)
        if "amount" in keys:
            keep |= rel <= amount_tol
        if "name" in keys:
            keep |= sims >= name_min
        if "ref" in keys:
            keep |= ref >= ref_min
        k = np.flatnonzero(keep)
        if len(k):
            rows.append(pd.DataFrame({"line": ln.line, "invoice": idx[k + lo], "name_sim": sims[k],
                                      "ref_digits": ref[k], "amount_rel_diff": rel[k]}))
    return pd.concat(rows, ignore_index=True)


def add_features(pairs, invoices, lines, links):
    """Join both sides of each pair, build the features, and grade the pair.

    Grade 2 is a true link. Grade 1 is another invoice from the right supplier: not the answer, but a
    reviewer who sees it knows they are in the right place. Grade 0 is everything else.
    """
    p = pairs.merge(invoices[["invoice", "supplier", "issued", "due", "amount"]], on="invoice")
    p = p.merge(lines[["line", "day", "amount", "kind"]].rename(columns={"amount": "paid"}), on="line")
    p["amount_exact"] = (np.abs(p.amount - p.paid) < .005).astype(int)
    p["amount_near"] = (p.amount_rel_diff <= .03).astype(int)
    p["days_since_issue"] = p.day - p.issued
    p["days_from_due"] = np.abs(p.day - p.due)
    p["amount_rank"] = p.groupby("line").amount_rel_diff.rank(method="min")
    p["name_rank"] = p.groupby("line").name_sim.rank(method="min", ascending=False)
    p["n_candidates"] = p.groupby("line").invoice.transform("size")
    truth = links.assign(linked=1)
    p = p.merge(truth, on=["line", "invoice"], how="left")
    p["linked"] = p.linked.fillna(0).astype(int)
    right = links.merge(invoices[["invoice", "supplier"]], on="invoice")[["line", "supplier"]].drop_duplicates().assign(same=1)
    p = p.merge(right, on=["line", "supplier"], how="left")
    p["grade"] = np.where(p.linked == 1, 2, np.where(p.same.fillna(0) == 1, 1, 0))
    return p.drop(columns="same").sort_values(["line", "invoice"]).reset_index(drop=True)


def ndcg_at(grade, score, group, k=5):
    """Mean NDCG@k over the groups that hold at least one relevant item, with gain 2**grade - 1."""
    out = []
    for g in np.unique(group):
        m = group == g
        y, s = grade[m], score[m]
        if y.max() == 0:
            continue
        order = np.lexsort((np.arange(len(s)), -s))[:k]
        disc = 1 / np.log2(np.arange(2, len(order) + 2))
        dcg = ((2.0 ** y[order] - 1) * disc).sum()
        ideal = ((2.0 ** np.sort(y)[::-1][:k] - 1) * (1 / np.log2(np.arange(2, min(k, len(y)) + 2)))).sum()
        out.append(dcg / ideal)
    return float(np.mean(out))


def top1(linked, score, group):
    """Share of the groups with a true link where the top-scored pair is a true link."""
    hit = []
    for g in np.unique(group):
        m = group == g
        if linked[m].max() == 0:
            continue
        hit.append(linked[m][np.argmax(score[m])])
    return float(np.mean(hit))
