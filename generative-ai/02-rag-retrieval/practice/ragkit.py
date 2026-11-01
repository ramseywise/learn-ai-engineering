"""Shared code for the RAG & Retrieval pillar's running example.

Tallybook is a fictional invoicing product, and every document below is
synthetic. The module needs only numpy and runs with no API key and no download.

    uv run --with numpy python ragkit.py        # prints a retriever scoreboard

`embed` is a hand-built stand-in for an embedding model. It maps synonyms to a
shared concept and blurs identifiers, which is what a trained embedder tends to
do. It shows the mechanics. Its scores are not evidence about real embedders.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Doc:
    id: str
    title: str
    text: str
    area: str
    updated: str  # ISO date
    audience: str = "public"  # "public" or "internal"

    @property
    def full(self) -> str:
        return f"{self.title}. {self.text}"


DOCS = [
    Doc("kb-01", "API authentication errors",
        "A request that returns HTTP-403 reached the server with a key that lacks the required "
        "scope. Open Settings, then API keys, and check that the key has the invoices:write scope. "
        "A request that returns HTTP-401 has no valid key at all, usually because it expired.",
        "api", "2026-09-14"),
    Doc("kb-02", "Rotating API keys",
        "Create the new key first, deploy it, then revoke the old key. Keys expire after 12 months "
        "unless you set another lifetime. Tallybook emails the workspace owner 14 days before a key "
        "lapses. Revoking a key takes effect within 60 seconds.",
        "api", "2026-06-02"),
    Doc("kb-03", "API rate limits",
        "The API allows 120 calls per minute for each workspace. Above that it returns HTTP-429 with "
        "a Retry-After header in seconds. Back off for that long and try again. The Scale plan raises "
        "the limit to 600 calls per minute.",
        "api", "2026-08-21"),
    Doc("kb-04", "Refund policy",
        "Annual plans can be refunded in full within 30 days of payment. After 30 days we refund the "
        "unused months minus a 10 percent fee. Monthly plans are not refunded, but they stop at the end "
        "of the paid month. Refunds reach the original card in 5 to 10 working days.",
        "billing", "2026-10-01"),
    Doc("kb-05", "Refund policy (2024 archive)",
        "Annual plans can be refunded within 14 days of payment. No refunds are available after 14 days. "
        "This page is kept for customers who signed up before January 2025.",
        "billing", "2024-11-15"),
    Doc("kb-06", "Cancelling your subscription",
        "The workspace owner can cancel under Settings, then Plan. Your data stays readable for 90 days "
        "after the paid period ends. After that it is deleted. Cancelling does not issue a refund by "
        "itself; request one from the billing team.",
        "billing", "2026-07-30"),
    Doc("kb-07", "Changing plans",
        "Upgrades apply at once and charge the prorated difference. Downgrades apply at the next "
        "renewal. Moving from Scale to Starter removes extra seats and API access, so export anything "
        "you need before the renewal date.",
        "billing", "2026-05-11"),
    Doc("kb-08", "Invoice numbering",
        "Invoice numbers must run in an unbroken sequence in most EU countries. Tallybook assigns the "
        "next number when you send an invoice, not when you draft it. You can set the starting number "
        "once, before the first invoice is sent. Deleting a sent invoice is not possible.",
        "invoicing", "2026-03-19"),
    Doc("kb-09", "Credit notes",
        "To correct or reverse a sent invoice, issue a credit note against it. The credit note gets its "
        "own number and links to the original. A partial credit note reverses selected lines. The "
        "customer balance updates at once.",
        "invoicing", "2026-03-19"),
    Doc("kb-10", "VAT on EU sales",
        "For a business customer in another EU country, enter their VAT number and Tallybook applies the "
        "reverse charge, showing 0 percent VAT with the required wording. For a private customer, charge "
        "the VAT rate of the customer's country once you pass the 10,000 euro OSS threshold.",
        "invoicing", "2026-02-27"),
    Doc("kb-11", "Payment reminders",
        "Turn on automatic reminders under Settings, then Invoicing. Tallybook sends the first reminder "
        "3 days after the due date and the second after 14 days. You can add a late fee to the second "
        "reminder where local law allows it.",
        "invoicing", "2026-04-08"),
    Doc("kb-12", "Invoice email delivery",
        "If a customer never received an invoice, check the delivery log on the invoice page. A status of "
        "BOUNCE-550 means the address does not exist. Correct the address and resend. Messages come from "
        "invoices@tallybook.example, so ask the customer to allow that sender.",
        "invoicing", "2026-06-17"),
    Doc("kb-13", "Bank connection errors",
        "Bank feeds sync every 6 hours. Error BANK-112 means the bank requires you to approve access "
        "again, which EU rules demand every 180 days. Open Banking, choose the account and select "
        "Reconnect. Transactions missed during the gap are fetched automatically.",
        "banking", "2026-09-02"),
    Doc("kb-14", "Exporting your data",
        "Owners can export invoices, customers and transactions as CSV under Settings, then Export. "
        "Exports of more than 50,000 rows run in the background and arrive by email. The link in the "
        "email stays valid for 7 days.",
        "account", "2026-01-23"),
    Doc("kb-15", "Password reset and two-factor login",
        "Use Forgot password on the sign-in page to get a reset link, valid for 1 hour. If you lost your "
        "authenticator app, enter a recovery code. Without a recovery code, the workspace owner must "
        "remove two-factor login from your account.",
        "account", "2026-08-05"),
    Doc("kb-16", "Team members and roles",
        "Owners and admins can invite people under Settings, then Team. Accountants can read and write "
        "invoices but cannot change the plan. Viewers can only read. Starter includes 2 seats and Scale "
        "includes 25.",
        "account", "2026-04-29"),
    Doc("kb-17", "Webhooks",
        "Tallybook posts an event when an invoice is sent or paid. Verify the signature in the "
        "X-Tally-Signature header. If your endpoint does not return a 2xx status, we retry 5 times over "
        "24 hours and then disable the webhook.",
        "api", "2026-07-12"),
    Doc("kb-18", "Runbook: manual refund override",
        "Support engineers may override the refund window with approval from a team lead. Use the admin "
        "console, open the payment and choose Force refund. Never share this procedure with customers.",
        "billing", "2026-09-20", audience="internal"),
]
DOC_BY_ID = {d.id: d for d in DOCS}

# Labelled eval set: (query, ids that answer it, kind).
QUERIES = [
    ("HTTP-403 when calling the API", {"kb-01"}, "code"),
    ("what does BANK-112 mean", {"kb-13"}, "code"),
    ("BOUNCE-550 on an invoice", {"kb-12"}, "code"),
    ("HTTP-429 retry", {"kb-03"}, "code"),
    ("X-Tally-Signature header", {"kb-17"}, "code"),
    ("how do I reverse a sent invoice", {"kb-09"}, "keyword"),
    ("export invoices as CSV", {"kb-14"}, "keyword"),
    ("reset my password", {"kb-15"}, "keyword"),
    ("invite an accountant to the team", {"kb-16"}, "keyword"),
    ("invoice numbers must be in sequence", {"kb-08"}, "keyword"),
    ("can I get my money back", {"kb-04"}, "paraphrase"),
    ("access denied even though my token is valid", {"kb-01"}, "paraphrase"),
    ("too many requests from my integration", {"kb-03"}, "paraphrase"),
    ("the bank link stopped updating", {"kb-13"}, "paraphrase"),
    ("my client says the bill never arrived", {"kb-12"}, "paraphrase"),
    ("how do I close my account", {"kb-06"}, "paraphrase"),
    ("tax for a company in Germany", {"kb-10"}, "paraphrase"),
    ("chase customers who have not paid", {"kb-11"}, "paraphrase"),
    ("swap credentials safely without downtime", {"kb-02"}, "paraphrase"),
    ("move to a cheaper subscription", {"kb-07"}, "paraphrase"),
]

LONG_DOC = """# Refunds and cancellations

## Refund windows
Annual plans can be refunded in full within 30 days of payment. After 30 days we refund the unused months minus a 10 percent fee. Monthly plans are not refunded.

## How refunds are paid
Refunds go back to the original card. They reach the customer in 5 to 10 working days. If the card has expired, the bank forwards the money to the replacement card. Tallybook cannot pay a refund to a different card or to a bank account.

## Cancelling a workspace
The workspace owner can cancel under Settings, then Plan. Data stays readable for 90 days after the paid period ends, and then it is deleted. Export anything you need first, because deleted data cannot be restored.

## Disputed charges
If a customer disputes a charge with their bank, the workspace is frozen until the dispute closes. Disputes usually take 30 to 60 days. Contact the billing team before you open a dispute, because a refund is faster than a chargeback.
"""

STOP = {"the", "is", "a", "an", "of", "to", "in", "and", "for", "on", "how", "what", "do", "i",
        "my", "it", "that", "this", "with", "when", "be", "at", "can", "you", "your", "we", "or",
        "by", "as", "are", "does", "not", "who", "have", "has", "even", "though", "from", "get"}


def tokenize(text: str) -> list[str]:
    """Keep codes like HTTP-403 whole, lowercase ordinary words, drop stop words."""
    tokens = re.findall(r"[A-Za-z0-9]+(?:[-_:][A-Za-z0-9]+)*", text)
    return [t if any(c.isdigit() for c in t) else t.lower()
            for t in tokens if t.lower() not in STOP]


class BM25:
    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(tokenize(t)) for t in texts]
        self.len = [sum(c.values()) for c in self.tf]
        self.avgdl = sum(self.len) / len(texts)
        self.df = Counter(t for c in self.tf for t in c)
        self.N = len(texts)

    def idf(self, term: str) -> float:
        df = self.df[term]
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def scores(self, query: str) -> np.ndarray:
        out = np.zeros(self.N)
        for term in tokenize(query):
            for i in range(self.N):
                tf = self.tf[i][term]
                if tf:
                    norm = 1 - self.b + self.b * self.len[i] / self.avgdl
                    out[i] += self.idf(term) * tf * (self.k1 + 1) / (tf + self.k1 * norm)
        return out


# Each group is one concept: the toy embedder gives its words the same axis.
CONCEPTS = [
    "refund refunded refunds money reimburse repay back reimbursement",
    "error errors fail fails failed failure stopped broken wrong problem",
    "forbidden denied scope permission permissions access lacks rejected",
    "key keys token tokens credential credentials secret",
    "rotate rotating swap replace replacement revoke revoking",
    "invoice invoices bill bills billed",
    "customer customers client clients",
    "cancel cancelling cancelled cancellation close closing terminate leave",
    "account workspace organisation",
    "subscription plan plans tier",
    "cheaper downgrade downgrades lower",
    "upgrade upgrades higher",
    "limit limits rate throttle throttled many quota calls requests",
    "tax vat taxes",
    "company business businesses",
    "germany eu european country countries",
    "reminder reminders chase chasing nudge overdue due",
    "paid unpaid pay payment payments late",
    "bank banks banking",
    "connection connections link links feed feeds sync synced updating reconnect",
    "email emails mail arrived received delivery delivered bounce sender",
    "export exports download csv backup",
    "password passwords sign-in login",
    "team seats members colleague colleagues invite",
    "reverse reversal correct correction undo credit",
    "number numbers numbering sequence",
    "webhook webhooks event events endpoint",
    "signature verify verification",
    "api integration",
    "downtime outage safely",
]
_CONCEPT_OF = {w: i for i, group in enumerate(CONCEPTS) for w in group.split()}
EMBED_DIM = 128


def _axis(name: str) -> np.ndarray:
    seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed).standard_normal(EMBED_DIM)


def embed(texts: list[str]) -> np.ndarray:
    """Toy embedder: unit vectors of shape (len(texts), 128).

    Synonyms share an axis. A code such as HTTP-403 is reduced to its letter
    prefix, so HTTP-403 and HTTP-429 land close together, the blur real embedders
    are known for. Stands in for a real model without a download.
    """
    out = np.zeros((len(texts), EMBED_DIM))
    for row, text in enumerate(texts):
        for tok in tokenize(text):
            if any(c.isdigit() for c in tok):
                tok = re.split(r"[-_:0-9]", tok)[0].lower() or "code"
            concept = _CONCEPT_OF.get(tok)
            name = f"concept-{concept}" if concept is not None else f"word-{tok}"
            weight = 2.0 if concept is not None else 0.5
            out[row] += weight * _axis(name)
    return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)


def top_k(scores: np.ndarray, ids: list[str], k: int) -> list[str]:
    """Ids of the k highest scores. Ties break toward the earlier id."""
    order = sorted(range(len(ids)), key=lambda i: (-scores[i], i))[:k]
    return [ids[i] for i in order if scores[i] > 0]


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal rank fusion over ranked lists of ids."""
    scores: dict[str, float] = {}
    for ranked in rankings:
        for rank, doc in enumerate(ranked, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1 / (k + rank)
    return sorted(scores, key=lambda d: (-scores[d], d))


class Retriever:
    """BM25, dense and hybrid search over any list of Doc."""

    def __init__(self, docs: list[Doc] = DOCS):
        self.docs = docs
        self.ids = [d.id for d in docs]
        self.bm25 = BM25([d.full for d in docs])
        self.vectors = embed([d.full for d in docs])

    def sparse(self, query: str, k: int = 5) -> list[str]:
        return top_k(self.bm25.scores(query), self.ids, k)

    def dense(self, query: str, k: int = 5) -> list[str]:
        return top_k(self.vectors @ embed([query])[0], self.ids, k)

    def hybrid(self, query: str, k: int = 5, pool: int = 10) -> list[str]:
        return rrf([self.sparse(query, pool), self.dense(query, pool)])[:k]


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return len(set(ranked[:k]) & relevant) / len(relevant)


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for rank, doc in enumerate(ranked, start=1):
        if doc in relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    dcg = sum(1 / math.log2(r + 1) for r, d in enumerate(ranked[:k], 1) if d in relevant)
    ideal = sum(1 / math.log2(r + 1) for r in range(1, min(len(relevant), k) + 1))
    return dcg / ideal


def evaluate(search, queries=QUERIES, k: int = 3) -> dict[str, float]:
    """Mean recall@k, MRR and nDCG@k of `search(query, k=...) -> ranked ids`."""
    runs = [(search(q, k=max(k, 10)), rel) for q, rel, _ in queries]
    return {
        f"recall@{k}": float(np.mean([recall_at_k(r, rel, k) for r, rel in runs])),
        "mrr": float(np.mean([reciprocal_rank(r, rel) for r, rel in runs])),
        f"ndcg@{k}": float(np.mean([ndcg_at_k(r, rel, k) for r, rel in runs])),
    }


if __name__ == "__main__":
    retriever = Retriever()
    for name, search in [("bm25", retriever.sparse), ("dense", retriever.dense),
                         ("hybrid", retriever.hybrid)]:
        print(f"{name:7}", {m: round(v, 3) for m, v in evaluate(search).items()})
        for kind in ["code", "keyword", "paraphrase"]:
            subset = [q for q in QUERIES if q[2] == kind]
            print(f"  {kind:11}", round(evaluate(search, subset)["recall@3"], 3))
