# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn"]
# ///
"""Bank-to-invoice matching that has to survive the accounts, for notes/04: a double-entry ledger with a period close.

Run from this folder (under a minute on a laptop CPU, downloads nothing, needs no key):
    uv run ledger_reconciliation_lab.py
    uv run ledger_reconciliation_lab.py --gate 0.5            # force the confidence gate
    uv run ledger_reconciliation_lab.py --fx-share 0.3        # more suppliers billing in USD

What is real: the double-entry mechanics, the invariants and the arithmetic. What is generated: every supplier, invoice
and bank line comes from matching.py, with credit notes and USD billing added here, all from a seed. The business, the
exchange rates and the prices of a wrong link are invented.

Fictional tax assumptions, not tax advice and not any country's rules: the buyer reclaims all input VAT. Each supplier
charges one rate, 20%, 7.5% or 0%. Invoice amounts are gross. Net is gross / (1 + rate), rounded half up to the cent, and
VAT is what remains. A credit note uses its invoice's rate. A discount or a settlement difference does not adjust VAT.
USD invoices are booked at the day's rate, and the difference at payment goes to FX gain or loss.
"""
# %%
import argparse
import copy
import dataclasses
import hashlib
import itertools
import json
import sys
import time
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from matching import FEATURES, add_features, block, make_ledger
from sklearn.ensemble import HistGradientBoostingClassifier

SEED = 11
SUPPLIERS, INVOICES, DAYS = 80, 900, 300
P1_END = 179                               # period 1 is days 0 to 179; period 2 runs to the last bank line
OPENING_CASH = Decimal("2000000.00")
VAT_RATES = [Decimal("0.20"), Decimal("0.20"), Decimal("0.075"), Decimal("0")]   # fictional
FX_SHARE, CREDIT_NOTE_SHARE = 0.10, 0.05   # suppliers billing in USD; single payments with a credit note first
FX_BAND = Decimal("0.005")                 # a USD payment must be within this of the open USD amount at the day's rate
FEE_ALLOWANCE, DISCOUNT = Decimal("5.00"), Decimal("0.02")   # settlement differences we let the machine book
REF_DIGITS = 5                             # a reference agreeing on this many digits names an invoice
WRONG_LINK_COST, REVIEW_COST = 25.0, 2.0   # invented prices for choosing the gate, see DS 01/13
ZERO = Decimal("0.00")
CENT = Decimal("0.01")

BANK, VAT_INPUT, SUSPENSE, AP, CAPITAL, RETAINED = 1000, 1400, 1900, 2000, 3000, 3100
PURCHASES, WAGES, RENT, OTHER_TAX, BANK_FEES, CARD = 5000, 6100, 6200, 6300, 6400, 6500
SETTLEMENT, FX_REALISED, FX_UNREALISED = 7100, 7800, 7810
ACCOUNTS = {BANK: "Bank", VAT_INPUT: "VAT reclaimable", SUSPENSE: "Bank lines awaiting review", AP: "Accounts payable",
            CAPITAL: "Capital", RETAINED: "Retained earnings", PURCHASES: "Purchases", WAGES: "Wages", RENT: "Rent",
            OTHER_TAX: "Other taxes", BANK_FEES: "Bank charges", CARD: "Card settlements",
            SETTLEMENT: "Discounts and settlement differences", FX_REALISED: "FX gain or loss, realised",
            FX_UNREALISED: "FX gain or loss, unrealised"}
PROFIT_AND_LOSS = {PURCHASES, WAGES, RENT, OTHER_TAX, BANK_FEES, CARD, SETTLEMENT, FX_REALISED, FX_UNREALISED}
NO_INVOICE = {"PAYROLL RUN": WAGES, "TAX OFFICE": OTHER_TAX, "BANK CHARGES": BANK_FEES, "CARD SETTLEMENT": CARD,
              "RENT STANDING ORDER": RENT}


def cents(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def money(x):
    """Enter float-land's numbers through a string, once, at the door."""
    return cents(Decimal(str(round(float(x), 2))))


# %% The ledger: an append-only journal, and nothing else
class PostingRejected(Exception):
    pass


class CloseRefused(Exception):
    def __init__(self, failures):
        super().__init__("; ".join(failures))
        self.failures = failures


@dataclass(frozen=True)
class Posting:
    account: int
    debit: Decimal = ZERO
    credit: Decimal = ZERO
    invoice: int | None = None   # payables lines name the invoice, which is what makes a subledger possible
    doc: Decimal = ZERO          # signed change in the invoice's document-currency balance


@dataclass(frozen=True)
class Entry:
    id: int
    day: int
    memo: str
    lines: tuple
    source: str
    actor: str
    confidence: float | None = None
    key: str | None = None
    reverses: int | None = None
    reason: str = ""

    def canonical(self):
        return json.dumps(dataclasses.asdict(self), default=str, sort_keys=True)


def debits(lines):
    return sum((p.debit for p in lines), ZERO)


def credits(lines):
    return sum((p.credit for p in lines), ZERO)


class Ledger:
    """Entries go in through post() or reverse() and never change. Balances are always read from the journal."""

    def __init__(self):
        self.journal, self.hashes = [], []
        self.closed_through = -1
        self.active_keys, self.reversed_ids = {}, set()

    def post(self, day, memo, lines, source, actor="system", confidence=None, key=None, reverses=None, reason=""):
        lines = tuple(lines)
        if day <= self.closed_through:
            raise PostingRejected(f"day {day} is in a closed period (closed through {self.closed_through})")
        if len(lines) < 2:
            raise PostingRejected("an entry needs at least two lines")
        for p in lines:
            if p.account not in ACCOUNTS:
                raise PostingRejected(f"unknown account {p.account}")
            for v in (p.debit, p.credit):
                if not isinstance(v, Decimal) or v != v.quantize(CENT) or v < 0:
                    raise PostingRejected(f"amount {v!r} must be a non-negative Decimal in whole cents")
            if (p.debit > 0) == (p.credit > 0):
                raise PostingRejected("each line is a debit or a credit, not both or neither")
        if debits(lines) != credits(lines):
            raise PostingRejected(f"debits {debits(lines)} do not equal credits {credits(lines)}")
        if key is not None and key in self.active_keys:
            raise PostingRejected(f"{key} is already posted as entry {self.active_keys[key]}: reverse it first")
        entry = Entry(len(self.journal), day, memo, lines, source, actor, confidence, key, reverses, reason)
        self.journal.append(entry)
        previous = self.hashes[-1] if self.hashes else ""
        self.hashes.append(hashlib.sha256((previous + entry.canonical()).encode()).hexdigest())
        if key is not None:
            self.active_keys[key] = entry.id
        return entry

    def reverse(self, entry_id, day, reason, actor):
        """The only way to undo anything: a mirror entry, dated in an open period. The original stays on the record."""
        if entry_id in self.reversed_ids:
            raise PostingRejected(f"entry {entry_id} is already reversed")
        old = self.journal[entry_id]
        if old.source == "reversal":
            raise PostingRejected("a reversal is not reversed; post the entry again")
        mirror = [Posting(p.account, p.credit, p.debit, p.invoice, -p.doc) for p in old.lines]
        entry = self.post(day, f"reversal of entry {entry_id}: {old.memo}", mirror, "reversal", actor, reverses=entry_id, reason=reason)
        self.reversed_ids.add(entry_id)
        if old.key is not None:
            self.active_keys.pop(old.key, None)
        return entry

    def balances(self, through=None):
        """Debit minus credit per account."""
        out = {a: ZERO for a in ACCOUNTS}
        for e in self.journal:
            if through is None or e.day <= through:
                for p in e.lines:
                    out[p.account] += p.debit - p.credit
        return out

    def open_items(self):
        """Per invoice, what is owed in euros and in the document currency. Read from the journal every time."""
        eur, doc = {}, {}
        for e in self.journal:
            for p in e.lines:
                if p.account == AP and p.invoice is not None:
                    eur[p.invoice] = eur.get(p.invoice, ZERO) + p.credit - p.debit
                    doc[p.invoice] = doc.get(p.invoice, ZERO) + p.doc
        return eur, doc

    def verify_chain(self):
        previous = ""
        if len(self.hashes) != len(self.journal):
            return False
        for entry, stored in zip(self.journal, self.hashes):
            previous = hashlib.sha256((previous + entry.canonical()).encode()).hexdigest()
            if previous != stored:
                return False
        return True


# %% The generated world: matching.py's ledger, plus VAT, credit notes and USD
@dataclass(frozen=True)
class Invoice:
    id: int
    supplier: int
    name: str
    issued: int
    currency: str
    doc: Decimal
    rate: Decimal
    gross: Decimal
    net: Decimal
    vat: Decimal
    vat_rate: Decimal


@dataclass(frozen=True)
class CreditNote:
    invoice: int
    day: int
    gross: Decimal
    net: Decimal
    vat: Decimal


def split_vat(gross, rate):
    net = cents(gross / (1 + rate))
    return net, gross - net


@dataclass
class World:
    invoices: dict
    credit_notes: list
    lines: pd.DataFrame
    links: dict
    rates: list
    line_doc: dict
    frame_invoices: pd.DataFrame
    frame_links: pd.DataFrame


def make_world(seed, fx_share=FX_SHARE, credit_share=CREDIT_NOTE_SHARE):
    frame, lines, links = make_ledger(seed, n_suppliers=SUPPLIERS, n_invoices=INVOICES, days=DAYS)
    rng = np.random.default_rng(seed + 1000)
    horizon = int(lines.day.max()) + 5
    walk = 0.92 * np.exp(np.cumsum(rng.normal(0, .003, horizon)))        # invented EUR per USD
    rates = [Decimal(str(round(float(r), 6))) for r in walk]
    usd = rng.random(SUPPLIERS) < fx_share
    vat = [VAT_RATES[i] for i in rng.integers(0, len(VAT_RATES), SUPPLIERS)]
    invoices = {}
    for r in frame.itertuples(index=False):
        doc = money(r.amount)
        rate = rates[r.issued] if usd[r.supplier] else Decimal(1)
        gross = cents(doc * rate)
        net, tax = split_vat(gross, vat[r.supplier])
        invoices[int(r.invoice)] = Invoice(int(r.invoice), int(r.supplier), r.name, int(r.issued), "USD" if usd[r.supplier] else "EUR",
                                           doc, rate, gross, net, tax, vat[r.supplier])
    targets = links.groupby("line").invoice.apply(list).to_dict()
    new_amount, line_doc, notes = {}, {}, []
    for ln in lines.itertuples(index=False):
        tied = targets.get(ln.line, [])
        original = money(ln.amount)
        if not tied:
            new_amount[ln.line] = original
            continue
        first = invoices[tied[0]]
        if first.currency == "USD":
            doc_paid = first.doc if ln.kind == "single" else original
            line_doc[ln.line] = doc_paid
            new_amount[ln.line] = cents(doc_paid * rates[ln.day] * Decimal(str(round(1 + rng.uniform(0, .003), 5))))
        elif ln.kind == "single" and rng.random() < credit_share and ln.day - first.issued >= 2:
            credit = cents(first.gross * Decimal(str(round(rng.uniform(.1, .3), 3))))
            net, tax = split_vat(credit, first.vat_rate)
            notes.append(CreditNote(first.id, int(rng.integers(first.issued + 1, ln.day)), credit, net, tax))
            new_amount[ln.line] = original - credit
        else:
            new_amount[ln.line] = original
    lines = lines.assign(amount_dec=lines.line.map(new_amount))
    lines["amount"] = lines.amount_dec.map(float)
    eur_frame = frame.assign(amount=[float(invoices[i].gross) for i in frame.invoice])
    return World(invoices, notes, lines, targets, rates, line_doc, eur_frame, links)


def fit_pair_model(seed, fx_share, credit_share):
    """Pair probabilities, trained on another generated ledger, with matching.py's blocking and features."""
    w = make_world(seed, fx_share, credit_share)
    pairs = add_features(block(w.frame_invoices, w.lines), w.frame_invoices, w.lines, w.frame_links)
    m = HistGradientBoostingClassifier(learning_rate=.08, max_iter=250, max_leaf_nodes=15, random_state=0, early_stopping=False)
    return m.fit(pairs[FEATURES], pairs.linked)


def candidates(world, model):
    pairs = add_features(block(world.frame_invoices, world.lines), world.frame_invoices, world.lines, world.frame_links)
    pairs["p"] = model.predict_proba(pairs[FEATURES])[:, 1]
    return {line: g.sort_values(["p", "invoice"], ascending=[False, True]) for line, g in pairs.groupby("line")}


def supplier_margin(cands):
    """Best pair probability minus the best pair at any other supplier: how sure the model is whose payment this is."""
    top = cands.iloc[0]
    others = cands[cands.supplier != top.supplier]
    return float(top.p - (others.p.iloc[0] if len(others) else 0.0))


# %% Settlement plans and the invariants a plan must pass
@dataclass
class Alloc:
    invoice: int
    carrying: Decimal   # euros of payable this payment clears
    doc: Decimal        # document-currency amount it clears


@dataclass
class Plan:
    line: int
    day: int
    amount: Decimal
    allocs: list
    kind: str = "settle"
    value_day: int | None = None   # the day the money moved, which sets the rate; a person may post it later

    def rate_day(self):
        return self.day if self.value_day is None else self.value_day


class Book:
    """A ledger plus what it must agree with outside itself: the invoice register and the bank statement."""

    def __init__(self, world):
        self.world, self.ledger = world, Ledger()
        self.ledger.post(0, "opening capital", [Posting(BANK, debit=OPENING_CASH), Posting(CAPITAL, credit=OPENING_CASH)], "opening")
        self.queue = {}           # line -> amount held in suspense for a person
        self.bank_entry = {}      # line -> entry id of the entry that took the money out of the bank
        self.allocated = {}       # line -> invoices the live entry settled, () if none
        self.auto_lines = set()
        self.by_supplier = {}
        self.posted_invoices = {}
        self.reval_entries = []
        self.eur, self.doc = {}, {}

    # Open balances, kept in step with every post so a plan need not re-read the journal.
    def track(self, entry):
        for p in entry.lines:
            if p.account == AP and p.invoice is not None:
                self.eur[p.invoice] = self.eur.get(p.invoice, ZERO) + p.credit - p.debit
                self.doc[p.invoice] = self.doc.get(p.invoice, ZERO) + p.doc
        return entry

    def post_invoice(self, inv):
        self.posted_invoices[inv.id] = inv
        self.by_supplier.setdefault(inv.supplier, []).append(inv.id)
        lines = [Posting(PURCHASES, debit=inv.net), Posting(AP, credit=inv.gross, invoice=inv.id, doc=inv.doc)]
        if inv.vat > 0:
            lines.append(Posting(VAT_INPUT, debit=inv.vat))
        return self.track(self.ledger.post(inv.issued, f"invoice {inv.id} {inv.name}", lines, "invoice", key=f"invoice:{inv.id}"))

    def post_credit_note(self, cn):
        lines = [Posting(AP, debit=cn.gross, invoice=cn.invoice, doc=-cn.gross), Posting(PURCHASES, credit=cn.net)]
        if cn.vat > 0:
            lines.append(Posting(VAT_INPUT, credit=cn.vat))
        return self.track(self.ledger.post(cn.day, f"credit note on invoice {cn.invoice}", lines, "credit_note"))

    def expected_eur(self, invoice, day):
        inv = self.world.invoices[invoice]
        return self.eur[invoice] if inv.currency == "EUR" else cents(self.doc[invoice] * self.world.rates[day])

    def violations(self, plan, clearing_held=False):
        """Every accounting reason this plan may not be posted. Empty means it may."""
        out = []
        if not plan.allocs:
            return ["nothing to allocate"]
        if plan.amount <= 0:
            out.append("non-positive payment")
        if not clearing_held and f"bank:{plan.line}" in self.ledger.active_keys:
            out.append("bank line already posted")
        invs = [self.world.invoices[a.invoice] for a in plan.allocs]
        if len({i.supplier for i in invs}) != 1:
            out.append("one payment across several suppliers")
        if len({a.invoice for a in plan.allocs}) != len(plan.allocs):
            out.append("invoice allocated twice")
        for a, i in zip(plan.allocs, invs):
            if i.id not in self.posted_invoices or i.issued > plan.day:
                out.append(f"invoice {i.id} not issued by day {plan.day}")
            elif a.carrying > self.eur[i.id] or self.eur[i.id] <= 0:
                out.append(f"overpays invoice {i.id}: open {self.eur[i.id]}, allocating {a.carrying}")
            elif i.currency == "USD" and a.doc > self.doc[i.id] + CENT:
                out.append(f"overpays invoice {i.id} in USD")
        if out:
            return out
        cleared = sum((a.carrying for a in plan.allocs), ZERO)
        difference = cleared - plan.amount
        if invs[0].currency == "USD":
            wanted = cents(sum((a.doc for a in plan.allocs), ZERO) * self.world.rates[plan.rate_day()])
            if abs(plan.amount - wanted) > cents(wanted * FX_BAND):
                out.append(f"USD amount {plan.amount} is outside the band around {wanted}")
        elif difference < 0:
            out.append(f"pays {-difference} more than it clears")
        elif difference > 0:
            full = all(a.carrying == self.eur[a.invoice] for a in plan.allocs)
            gross = sum((self.world.invoices[a.invoice].gross for a in plan.allocs), ZERO)
            if not full or difference > max(FEE_ALLOWANCE, cents(gross * DISCOUNT)):
                out.append(f"unexplained difference of {difference}")
        return out

    def plan_lines(self, plan, credit_account=BANK):
        lines = [Posting(AP, debit=a.carrying, invoice=a.invoice, doc=-a.doc) for a in plan.allocs]
        lines.append(Posting(credit_account, credit=plan.amount))
        difference = sum((a.carrying for a in plan.allocs), ZERO) - plan.amount
        fx = self.world.invoices[plan.allocs[0].invoice].currency == "USD"
        if difference > 0:
            lines.append(Posting(FX_REALISED if fx else SETTLEMENT, credit=difference))
        elif difference < 0:
            lines.append(Posting(FX_REALISED if fx else SETTLEMENT, debit=-difference))
        return lines

    def post_plan(self, plan, actor, confidence=None, reason=""):
        problems = self.violations(plan)
        if problems:
            raise PostingRejected("; ".join(problems))
        names = ",".join(str(a.invoice) for a in plan.allocs)
        entry = self.track(self.ledger.post(plan.day, f"bank line {plan.line} to invoice {names}", self.plan_lines(plan), "bank", actor,
                                            confidence, f"bank:{plan.line}", reason=reason))
        self.bank_entry[plan.line] = entry.id
        self.allocated[plan.line] = tuple(sorted(a.invoice for a in plan.allocs))
        return entry

    def post_no_invoice(self, line, day, amount, account, actor):
        entry = self.ledger.post(day, f"bank line {line}, no invoice: {ACCOUNTS[account]}",
                                 [Posting(account, debit=amount), Posting(BANK, credit=amount)], "bank", actor, key=f"bank:{line}")
        self.bank_entry[line], self.allocated[line] = entry.id, ()
        return entry

    def to_suspense(self, line, day, amount, why):
        entry = self.ledger.post(day, f"bank line {line} held: {why}", [Posting(SUSPENSE, debit=amount), Posting(BANK, credit=amount)],
                                 "bank", "gate", key=f"bank:{line}", reason=why)
        self.queue[line] = amount
        self.bank_entry[line] = entry.id
        return entry

    # %% Period close
    def checks(self, day, statement_total):
        """Every check run on the raw journal, against the two outside sources. Returns the failures."""
        fails = []
        bad = [e.id for e in self.ledger.journal if debits(e.lines) != credits(e.lines)]
        if bad:
            fails.append(f"unbalanced entries {bad[:3]}")
        total_d = sum((debits(e.lines) for e in self.ledger.journal), ZERO)
        total_c = sum((credits(e.lines) for e in self.ledger.journal), ZERO)
        if total_d != total_c:
            fails.append(f"trial balance off by {total_d - total_c}")
        if not self.ledger.verify_chain():
            fails.append("audit chain broken: an entry entered or changed outside post()")
        balances = self.ledger.balances()
        eur, _ = self.ledger.open_items()
        subledger = sum(eur.values(), ZERO)
        if subledger != -balances[AP]:
            fails.append(f"payables control {-balances[AP]} differs from the sum of open items {subledger}")
        negative = [i for i, v in eur.items() if v < 0]
        if negative:
            fails.append(f"{len(negative)} invoices overpaid, for example invoice {negative[0]} at {eur[negative[0]]}")
        wanted_vat = sum((i.vat for i in self.world.invoices.values() if i.issued <= day), ZERO)
        wanted_vat -= sum((c.vat for c in self.world.credit_notes if c.day <= day), ZERO)
        if wanted_vat != balances[VAT_INPUT]:
            fails.append(f"VAT account {balances[VAT_INPUT]} differs from the invoice register's {wanted_vat}")
        bank = OPENING_CASH - statement_total
        if balances[BANK] != bank:
            gap = abs(balances[BANK] - bank)
            hint = "; a gap divisible by 9 often means two digits swapped" if gap % 9 == 0 and gap > 0 else ""
            fails.append(f"bank account {balances[BANK]} differs from the statement {bank} by {gap}{hint}")
        held = sum(self.queue.values(), ZERO)
        if balances[SUSPENSE] != held:
            fails.append(f"suspense {balances[SUSPENSE]} differs from the review queue {held}")
        return fails

    def close(self, day, statement_total):
        fails = self.checks(day, statement_total)
        if fails:
            raise CloseRefused(fails)
        pnl = {a: v for a, v in self.ledger.balances().items() if a in PROFIT_AND_LOSS and v != 0}
        net = sum(pnl.values(), ZERO)
        lines = [Posting(a, credit=v) if v > 0 else Posting(a, debit=-v) for a, v in pnl.items()]
        lines.append(Posting(RETAINED, debit=net) if net > 0 else Posting(RETAINED, credit=-net))
        self.ledger.post(day, "close profit and loss to retained earnings", lines, "close", "close", key=f"close:{day}")
        self.ledger.closed_through = day
        return net

    def revalue(self, day):
        """Open USD payables move to the closing rate, and the move is undone on the first day of the next period."""
        self.reval_entries = []
        for i in sorted(k for k, v in self.eur.items() if v > 0 and self.world.invoices[k].currency == "USD"):
            target = cents(self.doc[i] * self.world.rates[day])
            move = target - self.eur[i]
            if move == 0:
                continue
            lines = ([Posting(FX_UNREALISED, debit=move), Posting(AP, credit=move, invoice=i)] if move > 0
                     else [Posting(AP, debit=-move, invoice=i), Posting(FX_UNREALISED, credit=-move)])
            self.reval_entries.append(self.track(self.ledger.post(day, f"revalue invoice {i}", lines, "revaluation")).id)

    def undo_revaluation(self, day):
        for e in self.reval_entries:
            self.track(self.ledger.reverse(e, day, "automatic reversal of closing revaluation", "system"))
        self.reval_entries = []


# %% Who decides: the truth (a person with supplier statements), and the proposal search
def truth_plan(book, row, post_day=None):
    """What a person with the supplier's statement would allocate. Used for the review queue and for corrections."""
    world, line, value_day, amount = book.world, int(row.line), int(row.day), row.amount_dec
    day = value_day if post_day is None else post_day
    targets = world.links.get(line, [])
    if row.kind == "part":
        i = targets[0]
        if world.invoices[i].currency == "EUR":
            return Plan(line, day, amount, [Alloc(i, min(amount, book.eur[i]), min(amount, book.eur[i]))], value_day=value_day)
        doc_paid = world.line_doc[line]
        if doc_paid >= book.doc[i] - CENT:
            return Plan(line, day, amount, [Alloc(i, book.eur[i], book.doc[i])], value_day=value_day)
        return Plan(line, day, amount, [Alloc(i, cents(book.eur[i] * doc_paid / book.doc[i]), doc_paid)], value_day=value_day)
    return Plan(line, day, amount, [Alloc(i, book.eur[i], book.doc[i]) for i in targets], value_day=value_day)


def propose(book, row, cands):
    """Search the top supplier's open invoices for allocations the arithmetic allows. Returns a plan, or a reason not to."""
    world, line, day, amount = book.world, int(row.line), int(row.day), row.amount_dec
    supplier = int(cands.iloc[0].supplier)
    open_ids = [i for i in book.by_supplier.get(supplier, []) if book.eur[i] > 0]
    if not open_ids:
        return None, "no open invoice at this supplier"
    fx = world.invoices[open_ids[0]].currency == "USD"

    def fits(i):
        want = book.expected_eur(i, day)
        if fx:
            return abs(amount - want) <= cents(want * FX_BAND)
        gap = want - amount
        return ZERO <= gap <= max(FEE_ALLOWANCE, cents(world.invoices[i].gross * DISCOUNT))

    def full(i):
        return Alloc(i, book.eur[i], book.doc[i])

    named = cands[(cands.ref_digits >= REF_DIGITS) & cands.invoice.isin(open_ids)]
    if len(named):
        i = int(named.iloc[0].invoice)
        if fits(i):
            return Plan(line, day, amount, [full(i)]), None
        if not fx and amount < book.eur[i]:
            return Plan(line, day, amount, [Alloc(i, amount, amount)], "partial"), None
    exact = [i for i in open_ids if book.expected_eur(i, day) == amount] if not fx else []
    if len(exact) == 1:
        return Plan(line, day, amount, [full(exact[0])]), None
    if len(exact) > 1:
        return None, "several invoices fit exactly"
    near = [i for i in open_ids if fits(i)]
    if len(near) == 1:
        return Plan(line, day, amount, [full(near[0])]), None
    if len(near) > 1:
        return None, "several invoices fit exactly"
    found = []
    for size in (2, 3, 4):
        for combo in itertools.combinations(open_ids[-14:], size):
            want = sum((book.expected_eur(i, day) for i in combo), ZERO)
            if want == amount or (fx and abs(amount - want) <= cents(want * FX_BAND)):
                found.append(combo)
    if len(found) == 1:
        return Plan(line, day, amount, [full(i) for i in found[0]], "batch"), None
    if len(found) > 1:
        return None, "several sets of invoices sum to it"
    return None, "amount fits no open invoice or set"


# %% One run of the books under one policy
@dataclass
class Result:
    book: Book
    auto: int = 0
    right: int = 0
    wrong: int = 0
    wrong_eur: Decimal = ZERO
    reasons: dict = field(default_factory=dict)
    held_for_confidence: int = 0
    corrected: int = 0
    closes: list = field(default_factory=list)
    snapshot: Book | None = None
    statement_p1: Decimal = ZERO
    example_wrong: int | None = None
    by_kind: dict = field(default_factory=dict)


def is_right(world, line, allocated):
    return tuple(sorted(world.links.get(line, []))) == allocated


def run_books(world, cands, policy, gate=0.5):
    """policy: 'person' (truth, all by hand), 'per_line' (top pick, no gate, no state),
    'confidence' (top pick behind a gate) or 'gated' (a gate, then a plan that must pass the invariants)."""
    book = Book(world)
    res = Result(book)
    credit_notes = sorted(world.credit_notes, key=lambda c: c.day)
    events = [(i.issued, 0, n, i) for n, i in enumerate(world.invoices.values())]
    events += [(c.day, 1, n, c) for n, c in enumerate(credit_notes)]
    events += [(int(r.day), 2, n, r) for n, r in enumerate(world.lines.itertuples(index=False))]
    events.sort(key=lambda e: e[:3])
    rows = {int(r.line): r for r in world.lines.itertuples(index=False)}
    last_day = max(e[0] for e in events)

    def clear_properly(day):
        """The review queue and the supplier-statement check: a person works through both before the close."""
        wrong_now = [ln for ln in sorted(book.auto_lines) if rows[ln].day <= day and not is_right(world, ln, book.allocated[ln])]
        for ln in wrong_now:
            book.track(book.ledger.reverse(book.bank_entry[ln], day, "supplier statement disagrees", "clerk"))
            book.allocated.pop(ln)
            book.auto_lines.discard(ln)
        for ln in wrong_now:
            r = rows[ln]
            if r.kind == "none":
                book.post_no_invoice(ln, day, r.amount_dec, NO_INVOICE[r.text], "clerk")
            else:
                book.post_plan(truth_plan(book, r, day), "clerk", reason="corrected after reversal")
            res.corrected += 1
        for ln in sorted(book.queue, key=lambda k: rows[k].day):
            amount = book.queue.pop(ln)
            r = rows[ln]
            if r.kind == "none":
                lines = [Posting(NO_INVOICE[r.text], debit=amount), Posting(SUSPENSE, credit=amount)]
                book.ledger.post(day, f"clear held line {ln}", lines, "review", "clerk", key=f"cleared:{ln}")
                book.allocated[ln] = ()
                continue
            plan = truth_plan(book, r, day)
            problems = book.violations(plan, clearing_held=True)
            assert not problems, f"a person's plan failed on line {ln}: {problems}"
            book.track(book.ledger.post(day, f"clear held line {ln} to invoice", book.plan_lines(plan, SUSPENSE), "review", "clerk", key=f"cleared:{ln}"))
            book.allocated[ln] = tuple(sorted(a.invoice for a in plan.allocs))

    def clear_naively(day):
        """The same people clear the queue for the naive matchers, with the line's amount and no settlement logic."""
        for ln in sorted(book.queue, key=lambda k: rows[k].day):
            amount = book.queue.pop(ln)
            left, lines = amount, []
            targets = world.links.get(ln, [])
            for n, i in enumerate(targets):
                part = left if n == len(targets) - 1 else min(left, world.invoices[i].gross)
                if part > 0:
                    lines.append(Posting(AP, debit=part, invoice=i))
                left -= part
            if not targets:
                lines = [Posting(NO_INVOICE.get(rows[ln].text, SUSPENSE), debit=amount)]
            lines.append(Posting(SUSPENSE, credit=amount))
            book.track(book.ledger.post(day, f"clear held line {ln}", lines, "review", "clerk", key=f"cleared:{ln}"))

    def period_end(day):
        statement = sum((r.amount_dec for r in rows.values() if r.day <= day), ZERO)
        if policy == "gated":
            clear_properly(day)
        elif policy != "person":
            clear_naively(day)
        if policy in ("gated", "person"):
            book.revalue(day)
        if day == P1_END:
            res.snapshot = copy.deepcopy(book)
            res.statement_p1 = statement
        try:
            net = book.close(day, statement)
            res.closes.append((day, "closed", net))
            return True
        except CloseRefused as refused:
            res.closes.append((day, "refused", refused.failures))
            return False

    closed_p1 = False
    for day, kind, _, item in events:
        if not closed_p1 and day > P1_END:
            ok = period_end(P1_END)
            if ok:
                book.undo_revaluation(P1_END + 1)
            closed_p1 = True
        if kind == 0:
            book.post_invoice(item)
        elif kind == 1:
            book.post_credit_note(item)
        else:
            act_on_line(book, res, world, cands, item, policy, gate)
    period_end(max(last_day, P1_END + 1))
    return res


def act_on_line(book, res, world, cands, row, policy, gate):
    line, day, amount = int(row.line), int(row.day), row.amount_dec
    c = cands.get(line)
    if policy == "person":
        if row.kind == "none":
            book.post_no_invoice(line, day, amount, NO_INVOICE[row.text], "clerk")
        else:
            book.post_plan(truth_plan(book, row), "clerk")
        return
    if row.text in NO_INVOICE:                    # every matcher gets the text rules, so the comparison is about invoices
        book.post_no_invoice(line, day, amount, NO_INVOICE[row.text], "rule")
        book.auto_lines.add(line)
        score(res, world, row, (), amount)
        return
    if policy in ("per_line", "confidence"):
        if c is None or (policy == "confidence" and supplier_margin(c) < gate):
            book.to_suspense(line, day, amount, "low confidence")
            res.held_for_confidence += 1
            return
        posted = None
        for i in c.invoice:                       # the top pick that has been issued and booked
            if int(i) in book.posted_invoices:
                posted = int(i)
                break
        if posted is None:
            book.to_suspense(line, day, amount, "no candidate")
            return
        book.track(book.ledger.post(day, f"bank line {line} to invoice {posted}",
                                    [Posting(AP, debit=amount, invoice=posted), Posting(BANK, credit=amount)],
                                    "bank", policy, float(c.iloc[0].p), f"bank:{line}"))
        book.allocated[line] = (posted,)
        book.auto_lines.add(line)
        score(res, world, row, (posted,), amount)
        return
    # The gated path.
    if c is None or supplier_margin(c) < gate:
        book.to_suspense(line, day, amount, "low confidence")
        res.held_for_confidence += 1
        return
    plan, why = propose(book, row, c)
    if plan is None:
        res.reasons[why] = res.reasons.get(why, 0) + 1
        book.to_suspense(line, day, amount, why)
        return
    problems = book.violations(plan)
    if problems:
        res.reasons["refused by the invariants"] = res.reasons.get("refused by the invariants", 0) + 1
        book.to_suspense(line, day, amount, problems[0])
        return
    book.post_plan(plan, "matcher", supplier_margin(c), reason=plan.kind)
    book.auto_lines.add(line)
    score(res, world, row, book.allocated[line], amount)


def score(res, world, row, allocated, amount):
    res.auto += 1
    kind = res.by_kind.setdefault(row.kind, [0, 0])
    kind[1] += 1
    if is_right(world, int(row.line), allocated):
        res.right += 1
        kind[0] += 1
    else:
        res.wrong += 1
        res.wrong_eur += amount
        if res.example_wrong is None:
            res.example_wrong = int(row.line)


# %% The naive floating-point book
def float_section(person):
    print("2. Float money beside Decimal, on the same clean books")
    a, b = 0.1 + 0.2, Decimal("0.1") + Decimal("0.2")
    print(f"   0.1 + 0.2 in float is {a!r}; in Decimal it is {b}. round(2.675, 2) gives {round(2.675, 2)}, half up gives {cents(Decimal('2.675'))}")
    totals = {}
    for e in person.ledger.journal:
        for p in e.lines:
            totals[p.account] = totals.get(p.account, 0.0) + float(p.debit) - float(p.credit)
    residual = sum(totals.values())
    print(f"   Float book, every entry in order: debits minus credits is {residual!r}")
    exact_ok = residual == 0.0
    tolerant_ok = abs(residual) < 0.05
    planted = residual + 0.03                # a real three-cent one-sided error
    print(f"   Close test, exactly zero:       clean book {'passes' if exact_ok else 'REFUSED, a false alarm'}")
    print(f"   Close test, under 0.05 either way: clean book {'passes' if tolerant_ok else 'refused'}, "
          f"and with a real 0.03 one-sided error planted it {'still PASSES, a miss' if abs(planted) < 0.05 else 'refuses'}")
    exact = sum(debits(e.lines) for e in person.ledger.journal) - sum(credits(e.lines) for e in person.ledger.journal)
    assert exact == ZERO
    assert exact_ok is False or residual == 0.0
    # A float open balance, then the second part payment, tested the way a naive matcher tests it.
    second, misses = 0, 0
    open_f, open_d = {}, {}
    parts = person.world.lines[person.world.lines.kind == "part"].sort_values(["day", "line"])
    for r in parts.itertuples(index=False):
        i = person.world.links[int(r.line)][0]
        if person.world.invoices[i].currency != "EUR":
            continue
        if i not in open_f:
            open_f[i] = float(person.world.invoices[i].gross)
            open_d[i] = person.world.invoices[i].gross
        if open_d[i] == r.amount_dec:
            second += 1
            misses += open_f[i] != float(r.amount_dec)
        open_f[i] -= float(r.amount_dec)
        open_d[i] -= r.amount_dec
    print(f"   Second part payments that clear an invoice: {second}. A float matcher testing open == amount misses {misses} of them")
    rate_f, rate_d = 0.075, Decimal("0.075")
    nets = [i.gross for i in person.world.invoices.values()]
    moved = [cents(n * rate_d) - money(round(float(n) * rate_f, 2)) for n in nets]
    differ = sum(1 for m in moved if m != 0)
    print(f"   VAT at 7.5% on {len(nets)} amounts: float round() disagrees with half-up rounding on {differ}, by {sum(abs(m) for m in moved)} in total\n")
    assert differ > 0


# %% The whole lab
def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--seed", type=int, default=SEED)
    ap_.add_argument("--gate", type=float, default=None, help="confidence gate; by default chosen by price on another ledger")
    ap_.add_argument("--fx-share", type=float, default=FX_SHARE)
    ap_.add_argument("--credit-share", type=float, default=CREDIT_NOTE_SHARE)
    args = ap_.parse_args()
    start = time.time()
    print("Generated books. Fictional VAT, invented rates and prices: no number here describes a real business or tax rule.\n")

    # %% 1. The ledger's own rules
    print("1. What the ledger refuses, before any matching")
    probe = Ledger()
    ok = [Posting(BANK, debit=Decimal("10.00")), Posting(CAPITAL, credit=Decimal("10.00"))]
    probe.post(5, "fine", ok, "test", key="once")
    attempts = [("debits do not equal credits", lambda: probe.post(5, "x", [Posting(BANK, debit=Decimal("10.00")), Posting(CAPITAL, credit=Decimal("9.99"))], "test")),
                ("a float amount", lambda: probe.post(5, "x", [Posting(BANK, debit=10.0), Posting(CAPITAL, credit=10.0)], "test")),
                ("half a cent", lambda: probe.post(5, "x", [Posting(BANK, debit=Decimal("1.005")), Posting(CAPITAL, credit=Decimal("1.005"))], "test")),
                ("the same key twice", lambda: probe.post(5, "x", ok, "test", key="once")),
                ("reversing a reversal", lambda: probe.reverse(probe.reverse(0, 6, "demo", "demo").id, 7, "demo", "demo"))]
    for name, attempt in attempts:
        try:
            attempt()
            raise AssertionError(f"{name} should have been refused")
        except PostingRejected as e:
            print(f"   {name:30s} refused: {e}")
    try:
        probe.journal[0].memo = "edited"
        raise AssertionError("entries must be frozen")
    except dataclasses.FrozenInstanceError:
        print(f"   {'editing a posted entry':30s} refused: entries are frozen, so the only correction is a reversal")
    print()

    world = make_world(args.seed, args.fx_share, args.credit_share)
    tuning = make_world(args.seed + 1, args.fx_share, args.credit_share)
    model = fit_pair_model(args.seed + 2, args.fx_share, args.credit_share)
    cands, tune_cands = candidates(world, model), candidates(tuning, model)

    person = run_books(world, cands, "person")
    assert [c[1] for c in person.closes] == ["closed", "closed"], person.closes
    assert person.book.ledger.balances()[AP] == ZERO, "with the truth, every invoice ends settled"
    assert all(v == 0 for v in person.book.ledger.open_items()[0].values())
    kinds = world.lines.kind.value_counts().to_dict()
    usd = sum(i.currency == "USD" for i in world.invoices.values())
    fx_net = -person.book.ledger.balances(through=None)[RETAINED]
    print(f"   Generated books: {len(world.invoices)} invoices ({usd} in USD), {len(world.credit_notes)} credit notes, {len(world.lines)} bank lines {kinds}")
    print(f"   A person with every supplier's statement closes both periods; payables end at {person.book.ledger.balances()[AP]}, retained result {fx_net}\n")
    float_section(person.book)

    # %% 3. Choosing the gate, on another ledger
    print("3. The confidence gate, priced on a second generated ledger. "
          f"Assumed: a wrong link costs {WRONG_LINK_COST:.0f} to find and fix, a review {REVIEW_COST:.0f}")
    print("     gate   auto-posted  wrong  held for a person  cost per 1,000 lines")
    table = []
    for gate in (0.0, .1, .2, .3, .5, .7, .8, .9, .95):
        r = run_books(tuning, tune_cands, "gated", gate)
        n = len(tuning.lines)
        held = n - r.auto
        cost = (r.wrong * WRONG_LINK_COST + held * REVIEW_COST) / n * 1000
        table.append((cost, gate))
        print(f"     {gate:4.2f} {r.auto:13d} {r.wrong:6d} {held:18d} {cost:21,.0f}")
    gate = args.gate if args.gate is not None else min(table)[1]
    print(f"   Using gate {gate}\n")

    # %% 4. Three matchers
    per_line = run_books(world, cands, "per_line")
    conf = run_books(world, cands, "confidence", gate)
    gated = run_books(world, cands, "gated", gate)
    print("4. Three matchers on the same lines. Right means exactly the invoices the line truly settles, or none")
    print(f"   {'':34s} {'per-line top pick':>18s} {'gate only':>10s} {'gate + invariants':>18s}")

    def row(label, values):
        print(f"   {label:34s} {values[0]!s:>18s} {values[1]!s:>10s} {values[2]!s:>18s}")

    results = (per_line, conf, gated)
    row("lines posted by machine", [r.auto for r in results])
    row("  right", [r.right for r in results])
    row("  wrong", [r.wrong for r in results])
    row("  wrong, in euros", [f"{r.wrong_eur:,.0f}" for r in results])
    row("held for a person", [len(world.lines) - r.auto for r in results])
    open_stats = []
    for r in results:
        eur, _ = r.book.ledger.open_items()
        open_stats.append((sum(1 for v in eur.values() if v < 0), sum(1 for v in eur.values() if v > 0), sum((abs(v) for v in eur.values()), ZERO)))
    eur_g = gated.book.ledger.open_items()[0]
    row("invoices overpaid at the end", [s[0] for s in open_stats])
    row("invoices still open at the end", [s[1] for s in open_stats])
    row("payables error at the end, euros", [f"{s[2]:,.0f}" for s in open_stats])
    tb = [sum((debits(e.lines) for e in r.book.ledger.journal), ZERO) == sum((credits(e.lines) for e in r.book.ledger.journal), ZERO) for r in results]
    row("trial balance balances", tb)
    row("period 1 close", [r.closes[0][1] for r in results])
    print("   Every invoice was truly paid by the end, so every euro of payables left is an error. The right answer ends at zero")
    print(f"   Why the per-line close failed: {per_line.closes[0][2][0] if per_line.closes[0][1] == 'refused' else 'it did not'}")
    print(f"   By kind, right of posted, gate + invariants: { {k: f'{v[0]} of {v[1]}' for k, v in sorted(gated.by_kind.items())} }")
    print(f"   Passed the gate, then the arithmetic refused: {dict(sorted(gated.reasons.items(), key=lambda kv: -kv[1]))}")
    print(f"   Stopped by the gate itself: {gated.held_for_confidence}")
    print(f"   Wrong links reversed and reposted after the supplier-statement check: {gated.corrected}. This check is a perfect oracle here, a real one isn't")
    print("   The invariants catch what is impossible. A wrong link that fits the arithmetic still passes, which is why wrong isn't zero.\n")
    assert sum(eur_g.values(), ZERO) == ZERO and not any(v < 0 for v in eur_g.values())
    assert gated.right + gated.wrong == gated.auto
    assert tb[0] and tb[1] and tb[2], "the naive books balance: balancing does not mean right"

    # %% 5. Close, with planted errors
    print("5. Period 1 close, on a clean copy and with one planted error at a time")
    clean = gated.snapshot
    day, statement = P1_END, gated.statement_p1
    assert clean.checks(day, statement) == []
    print(f"   clean books: all checks pass, trial balance {sum((debits(e.lines) for e in clean.ledger.journal), ZERO):,}")

    bank_entries = [e for e in clean.ledger.journal if e.source == "bank" and e.key and e.id not in clean.ledger.reversed_ids and e.lines[0].account == AP
                    and all(p.account in (AP, BANK) for p in e.lines) and e.lines[-1].credit >= 100]
    target = next(e for e in bank_entries if str(e.lines[-1].credit).replace(".", "")[0] != str(e.lines[-1].credit).replace(".", "")[1])
    invoice_entry = next(e for e in clean.ledger.journal if e.source == "invoice" and e.id not in clean.ledger.reversed_ids
                         and clean.world.invoices[int(e.memo.split()[1])].vat_rate == Decimal("0.20"))

    def plant_one_sided(b):
        """A legacy import writes straight into the table, debit only, past post()."""
        e = Entry(len(b.ledger.journal), day, "legacy import", (Posting(PURCHASES, debit=Decimal("0.03")),), "import", "legacy")
        b.ledger.journal.append(e)

    def plant_untagged(b):
        """Balanced, in the control account, naming no invoice: a manual journal to make a supplier's figure look right."""
        b.ledger.post(day, "manual adjustment", [Posting(AP, debit=Decimal("250.00")), Posting(PURCHASES, credit=Decimal("250.00"))], "manual", "someone")

    def plant_wrong_vat(b):
        """Balanced, right payable, wrong rate: booked at 7.5% where the supplier charges 20%."""
        inv = b.world.invoices[int(invoice_entry.memo.split()[1])]
        b.track(b.ledger.reverse(invoice_entry.id, day, "rebooked", "someone"))
        net, tax = split_vat(inv.gross, Decimal("0.075"))
        b.track(b.ledger.post(day, f"invoice {inv.id} rebooked", [Posting(PURCHASES, debit=net), Posting(VAT_INPUT, debit=tax), Posting(AP, credit=inv.gross, invoice=inv.id, doc=inv.doc)], "invoice", "someone"))

    def plant_transposition(b):
        """Balanced, but the bank figure has two digits swapped, so the books disagree with the statement."""
        amount = target.lines[-1].credit
        digits = str(amount)
        swapped = Decimal(digits[1] + digits[0] + digits[2:])
        b.track(b.ledger.reverse(target.id, day, "rekeyed", "someone"))
        allocated = [p for p in target.lines if p.account == AP][0]
        b.track(b.ledger.post(day, "rekeyed payment", [Posting(AP, debit=swapped, invoice=allocated.invoice), Posting(BANK, credit=swapped)], "bank", "someone"))

    def plant_overpaid(b):
        """Balanced, in the bank and the payables, but more than the invoice ever owed."""
        i = next(k for k, v in b.eur.items() if v == 0 and b.world.invoices[k].currency == "EUR")
        b.ledger.post(day, "duplicate payment", [Posting(AP, debit=Decimal("40.00"), invoice=i), Posting(SUSPENSE, credit=Decimal("40.00"))], "manual", "someone")

    plants = [("one-sided legacy import of 0.03", plant_one_sided), ("balanced, payables with no invoice", plant_untagged),
              ("balanced, VAT at the wrong rate", plant_wrong_vat), ("balanced, two bank digits swapped", plant_transposition),
              ("balanced, an invoice overpaid", plant_overpaid)]
    print(f"   {'planted error':38s} {'balances?':>10s}   first reason the close gave")
    for name, plant in plants:
        b = copy.deepcopy(clean)
        plant(b)
        tb_ok = sum((debits(e.lines) for e in b.ledger.journal), ZERO) == sum((credits(e.lines) for e in b.ledger.journal), ZERO)
        try:
            b.close(day, statement)
            raise AssertionError(f"close accepted: {name}")
        except CloseRefused as refused:
            print(f"   {name:38s} {'yes' if tb_ok else 'NO':>10s}   {refused.failures[0]}" + (f"  (+{len(refused.failures) - 1} more)" if len(refused.failures) > 1 else ""))
    b = copy.deepcopy(clean)
    plant_wrong_vat(b)
    inv = b.world.invoices[int(invoice_entry.memo.split()[1])]
    wrong_entry = next(e for e in reversed(b.ledger.journal) if e.memo == f"invoice {inv.id} rebooked")
    b.track(b.ledger.reverse(wrong_entry.id, day, "wrong rate", "reviewer"))
    net, tax = split_vat(inv.gross, inv.vat_rate)
    b.track(b.ledger.post(day, f"invoice {inv.id} rebooked correctly", [Posting(PURCHASES, debit=net), Posting(VAT_INPUT, debit=tax), Posting(AP, credit=inv.gross, invoice=inv.id, doc=inv.doc)], "invoice", "reviewer"))
    b.close(day, statement)
    print("   Fixing the VAT error with a reversal and a correct entry: the close now passes, and all three entries stay on the record")
    print(f"   Clean run: {gated.closes[0][1]} on day {gated.closes[0][0]}, then {gated.closes[1][1]} on day {gated.closes[1][0]}\n")

    # %% 6. Reversal and the audit trail
    print("6. Reversal, not edit, and what the trail shows")
    final = gated.book.ledger
    ln = gated.example_wrong
    if ln is not None:
        print(f"   Bank line {ln}, truly invoice(s) {world.links.get(ln, 'none')}:")
        for e in final.journal:
            if e.memo.startswith(f"bank line {ln} ") or e.memo.startswith(f"reversal of entry") and final.journal[e.reverses].memo.startswith(f"bank line {ln} ") or e.memo.startswith(f"clear held line {ln} "):
                conf_text = f"confidence {e.confidence:.2f}" if e.confidence is not None else ""
                print(f"     entry {e.id:5d} day {e.day:3d} {e.actor:8s} {e.memo[:50]:50s} {conf_text} {e.reason}")
    p1 = final.balances(through=P1_END)
    sample = next(e for e in final.journal if e.day <= P1_END and e.source == "bank" and e.id not in final.reversed_ids and e.lines[0].account == AP and e.lines[0].debit > 0)
    demo = copy.deepcopy(gated.book)
    try:
        demo.ledger.post(P1_END, "backdated fix", [Posting(BANK, debit=Decimal("1.00")), Posting(PURCHASES, credit=Decimal("1.00"))], "manual", "someone")
        raise AssertionError("closed period accepted a post")
    except PostingRejected as e:
        print(f"   A backdated post: refused: {e}")
    demo.track(demo.ledger.reverse(sample.id, final.journal[-1].day + 1, "later query from the supplier", "clerk"))
    assert demo.ledger.balances(through=P1_END) == p1, "a later reversal must not move a closed period"
    print(f"   A reversal of entry {sample.id}, from a closed period, is dated today: period 1's balances are unchanged, today's move by {sample.lines[0].debit}")
    assert gated.book.ledger.verify_chain()
    tampered = copy.deepcopy(gated.book)
    old = tampered.ledger.journal[sample.id]
    tampered.ledger.journal[sample.id] = dataclasses.replace(old, memo=old.memo + " (edited)")
    assert not tampered.ledger.verify_chain()
    print(f"   Hash chain over {len(final.journal):,} entries: verifies. Editing one memo behind the API: the chain breaks at that entry")
    actors = pd.Series([e.actor for e in final.journal]).value_counts().to_dict()
    print(f"   Who posted: {actors}")
    reversals = sum(e.source == "reversal" for e in final.journal)
    print(f"   Reversals on record: {reversals}, of which revaluations undone: {sum(e.source == 'reversal' and e.actor == 'system' for e in final.journal)}")
    print(f"\nRuntime {time.time() - start:.0f} s. Results describe this generated ledger and these invented prices and rules.")


if __name__ == "__main__":
    main()
