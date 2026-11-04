# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy"]
# ///
"""Retrieval over text that changes by legal effect, on a generated rulebook, for notes/07.

Run from this folder (under a second, downloads nothing, needs no API key):
    uv run versioned_rules_lab.py
    uv run versioned_rules_lab.py --seed 11 --k 5
    uv run versioned_rules_lab.py --show-rulebook      # also print the raw text the parser reads

Everything is generated from a seed: the Brindlemark Payments Authority, its rulebook, its amendments, the gold
questions, the customer controls. Brindlemark is invented and none of this is law or legal advice. Every printed number
describes this generated rulebook and these generated questions. None of them is a finding about real regulation, real
parsers or real models. No model is called: the obligation extractor is a transparent set of regular expressions
standing in for one, so the scores in section 4 measure the harness.

Things to change and watch move:
  - `extract_rules`: add a rule for "No X may ...". Modality, who and the change-detection score all rise.
  - `FUZZY_THRESHOLD`: lower or raise it and see which planted citations slip past the fuzzy check.
  - `Book.in_force`: compare on `published_on` instead of `effective_from` and watch the asserts fire.
  - `--k`: a larger k hides wrong versions in recall and raises the wrong-version rate of the naive indexes.
"""
# %%
import argparse
import random
import re
import sys
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from difflib import SequenceMatcher
from functools import cache

from ragkit import BM25

SEED, K = 7, 3
TODAY = date(2026, 11, 1)  # a fixed "now", so the output does not change with the calendar
FUZZY_THRESHOLD = 0.9      # the fuzzy quote check in generative-ai/08-eval/notes/07
AUTHORITY = "Brindlemark Payments Authority"
FIELDS = ["who", "modality", "action", "deadline", "condition", "source_article", "version"]


# %% The generator: structured truth first, raw text rendered from it
@dataclass(frozen=True)
class Clause:
    """One obligation as the generator knows it. This is the gold record for extraction."""
    who: str
    modality: str  # "must" or "must_not"
    action: str
    deadline: str | None = None
    condition: str | None = None
    form: str = "must"  # how the sentence is phrased; see render()


def O(who, action, deadline=None, condition=None, form="must"):
    modality = "must_not" if form in ("must_not", "no_may") else "must"
    return Clause(who, modality, action, deadline, condition, form)


def render(c: Clause) -> str:
    det = "An" if c.who[0] in "aeiou" else "A"
    tail = f" {c.deadline}" if c.deadline else ""
    if c.form == "where":
        return f"Where {c.condition}, {det.lower()} {c.who} must {c.action}{tail}."
    if c.form == "no_may":
        return f"No {c.who} may {c.action}{tail}" + (f" unless {c.condition}." if c.condition else ".")
    verb = {"must": "must", "must_not": "must not", "shall": "shall", "required": "is required to"}[c.form]
    word = "unless" if c.modality == "must_not" else "if"
    return f"{det} {c.who} {verb} {c.action}{tail}" + (f" {word} {c.condition}." if c.condition else ".")


@dataclass(frozen=True)
class Wording:
    """The text of one version of a paragraph, and the obligations it truly contains."""
    text: str
    clauses: tuple = ()


def W(clause: Clause) -> Wording:
    return Wording(render(clause), (clause,))


def S(text: str, *clauses) -> Wording:
    """A sentence the renderer does not write: passive voice, or two duties in one sentence."""
    return Wording(text, clauses)


def T(text: str) -> Wording:
    """Text with no duty in it: a definition, a power, a procedural rule."""
    return Wording(text)


@dataclass
class Para:
    question: str | None
    first: Wording
    changes: list = field(default_factory=list)  # (instrument, Wording or None for a repeal, gold label)
    uses: tuple = ()                             # (article key, paragraph number) of the definitions it relies on
    inserted_by: str | None = None


@dataclass
class Art:
    key: str
    title: str
    paras: list
    inserted_by: str | None = None
    repealed_by: str | None = None


@dataclass(frozen=True)
class Instrument:
    key: str
    name: str
    published_on: date
    effective_from: date


@dataclass(frozen=True)
class TruthVersion:
    pid: str
    instrument: str
    text: str
    clauses: tuple
    published_on: date
    effective_from: date
    effective_to: date | None
    repeal: bool
    label: str | None


FILLER = [
    ("Annual report", "The Authority publishes an annual report on the complaints it receives from customers."),
    ("Fee schedule of the Authority", "The Authority sets the fees that a payment firm pays for its authorisation each year."),
    ("Public register", "The public register lists each payment firm and each agent, with the date of authorisation."),
    ("Language of filings", "Filings with the Authority are accepted in the official language or in translation."),
    ("Electronic filing", "A filing made through the portal counts as received on the day the portal records it."),
    ("Notices from the Authority", "A notice from the Authority counts as served two days after it is sent to the firm."),
    ("Supervisory visits", "The Authority schedules supervisory visits on the basis of risk and customer numbers."),
    ("Consultation", "The Authority consults payment firms and customers on proposed amendments to this Rulebook."),
    ("Forms", "The forms that this Rulebook refers to are published on the website of the Authority."),
    ("Calculation of time", "A period counted in days includes weekends and public holidays."),
    ("Waivers", "The Authority can waive a provision for a payment firm for a stated period, by written notice."),
    ("Transitional matters", "A licence granted before this Rulebook took effect continues as an authorisation."),
]


def generate(seed: int):
    """Return (instruments, parts, numbers). Numbers and dates vary with the seed. The direction of each change doesn't."""
    r = random.Random(seed)

    def on(y, m, d):
        return date(y, m, d) + timedelta(days=r.randint(0, 9))

    ins = {i.key: i for i in [
        Instrument("BASE", "Rulebook", on(2023, 1, 9), on(2023, 3, 1)),
        Instrument("A24", "Amending Instrument 2024/1", on(2024, 2, 5), on(2024, 7, 1)),
        Instrument("A25", "Amending Instrument 2025/1", on(2025, 3, 3), on(2025, 6, 1)),
        Instrument("R25", "Correcting Instrument 2025/2", on(2025, 9, 8), on(2025, 7, 1)),  # retroactive
        Instrument("A26", "Amending Instrument 2026/1", on(2026, 2, 2), on(2026, 9, 1)),
        Instrument("P27", "Amending Instrument 2026/2", on(2026, 10, 5), on(2027, 3, 1)),   # published, not yet in force
    ]}
    ch = r.choice
    notify_h = [ch([72, 96]), ch([24, 36]), ch([12, 18])]
    inform_d = [2, ch([3, 4])]
    report_w = ["thirty", "twenty"]
    notice_d = [30, ch([45, 60])]
    recon_d = [ch([3, 4]), 1]
    keep_y = [5, ch([7, 8])]
    suspicious = [ch([5, 7]), ch([2, 3])]
    customers = [ch([5000, 10000]), ch([1000, 2000])]
    outage_h = ch([2, 4])
    transfer = [ch([10000, 15000]), ch([20000, 25000])]
    dormant_m = [ch([12, 18]), ch([24, 36])]

    defs = Art("defs", "Definitions", [
        Para("which outages count as a reportable incident",
             T(f'"reportable incident" means an outage of a payment service that affects more than {customers[0]} customers '
               f"or lasts longer than {outage_h} hours."),
             [("A25", T(f'"reportable incident" means an outage of a payment service that affects more than {customers[1]} '
                        f"customers or lasts longer than {outage_h} hours."), "definition_changed")]),
        Para("what money counts as safeguarded funds",
             T('"safeguarded funds" means customer money that a payment firm holds pending settlement.')),
        Para("how large is a high-value transfer",
             T(f'"high-value transfer" means a single transfer of more than {transfer[0]} marks.'),
             [("A26", T(f'"high-value transfer" means a single transfer of more than {transfer[1]} marks.'),
               "definition_changed")]),
        Para("how long before an account is treated as dormant",
             T(f'"dormant account" means an account with no customer-initiated transaction for {dormant_m[0]} months.'),
             [("P27", T(f'"dormant account" means an account with no customer-initiated transaction for {dormant_m[1]} months.'),
               "definition_changed")]),
        Para(None, T('"agent" means a person who provides payment services for a payment firm under a written contract.')),
    ])
    scope = Art("scope", "Scope", [
        Para(None, T("This Rulebook applies to every payment firm authorised by the Authority and to every agent acting for one.")),
        Para(None, T("The Authority can issue guidance on this Rulebook. Guidance does not change the effect of any Article.")),
    ])

    def notify(h):
        return O("payment firm", "notify the Authority of each reportable incident, as defined in §defs,",
                 f"within {h} hours of detection")

    def inform(d, form="where"):
        return O("payment firm", "inform that firm", f"within {d} days of detection",
                 "a reportable incident under §defs affects another payment firm", form)

    def final_report(w):
        return S(f"A final incident report must be filed by each payment firm within {w} days of recovery.",
                 O("payment firm", "file a final incident report", f"within {w} days of recovery"))

    incident = Art("incident", "Incident notification", [
        Para("how quickly must a firm tell the Authority about a reportable incident after detection", W(notify(notify_h[0])),
             [("A24", W(notify(notify_h[1])), "tightened"), ("P27", W(notify(notify_h[2])), "tightened")],
             uses=(("defs", 1),)),
        Para("when an incident hits another firm how fast must that firm be informed", W(inform(inform_d[0])),
             [("A25", W(inform(inform_d[1])), "loosened")], uses=(("defs", 1),)),
        Para("deadline to file the final report after recovery from an incident", final_report(report_w[0]),
             [("R25", final_report(report_w[1]), "tightened")]),
    ])

    def outsource_notice(d):
        return O("payment firm", "give the Authority notice of an outsourcing of a critical function",
                 f"at least {d} days before the contract is signed")

    approve = "the Authority has approved the provider in writing"
    outsourcing = Art("outsourcing", "Outsourcing", [
        Para("how much notice before outsourcing a critical function", W(outsource_notice(notice_d[0])),
             [("A25", W(outsource_notice(notice_d[1])), "tightened")]),
        Para("can a firm outsource the safeguarding of customer money to a provider",
             W(O("payment firm", "outsource the safeguarding of safeguarded funds, as defined in §defs,", None, approve, "no_may")),
             [("P27", W(O("payment firm", "outsource the safeguarding of safeguarded funds, as defined in §defs,", None, None, "no_may")),
               "tightened")], uses=(("defs", 2),)),
        Para(None, T("An application that is incomplete must be treated as not received.")),
    ])

    def reconcile(d):
        return O("payment firm", "reconcile safeguarded funds, as defined in §defs,", f"within {d} days of each settlement date")

    safeguarding = Art("safeguarding", "Safeguarding", [
        Para("how often must safeguarded funds be reconciled", W(reconcile(recon_d[0])),
             [("A26", W(reconcile(recon_d[1])), "tightened")], uses=(("defs", 2),)),
        Para("may a firm mix customer money with its own money",
             W(O("payment firm", "mix safeguarded funds with its own money", None, None, "must_not")), uses=(("defs", 2),)),
        Para("what happens when a reconciliation finds a shortfall",
             W(O("payment firm", "top up the safeguarding account", "within 2 days of the finding", "a reconciliation finds a shortfall", "where"))),
        Para("where does a wallet operator hold customer funds",
             W(O("wallet operator", "hold safeguarded funds in a designated account")), inserted_by="A25", uses=(("defs", 2),)),
    ])

    def retain(y):
        return S(f"Customer transaction records must be retained by each payment firm for at least {y} years.",
                 O("payment firm", "retain customer transaction records", f"for at least {y} years"))

    records = Art("records", "Records", [
        Para("how long must customer transaction records be retained", retain(keep_y[0]),
             [("A24", retain(keep_y[1]), "tightened")]),
        Para("how long is the register of agents kept",
             W(O("payment firm", "keep a register of its agents", "for at least 3 years")),
             [("A26", W(O("payment firm", "keep a register of its agents", "for at least 3 years", None, "shall")), "reworded")]),
    ])

    def no_fee(cond):
        return O("payment firm", "charge a fee on a dormant account", None, cond, "must_not")

    dormant = Art("dormant", "Dormant accounts", [
        Para("when must the customer be told an account has gone dormant",
             W(O("payment firm", "notify the customer", "within 30 days of the change of status",
                 "an account becomes a dormant account under §defs", "where")), uses=(("defs", 4),)),
        Para("may a firm charge a fee on a dormant account", W(no_fee(None)),
             [("A26", W(no_fee("the customer agreed to the fee in writing")), "loosened")], uses=(("defs", 4),)),
    ])
    screen = O("payment firm", "verify the source of funds for each high-value transfer, as defined in §defs,", "before execution")
    # "before execution" is not caught as a deadline by the rules: a real phrasing they get wrong.
    transfers = Art("transfers", "Transfer checks", [
        Para("what check runs on the source of funds for large transfers", W(screen),
             [("A24", W(replace(screen, form="shall")), "reworded")], uses=(("defs", 3),)),
        Para("how soon must a suspicious transfer be reported to the Authority",
             W(O("payment firm", "report a suspicious transfer to the Authority", f"within {suspicious[0]} days of the finding")),
             [("A26", W(O("payment firm", "report a suspicious transfer to the Authority", f"within {suspicious[1]} days of the finding",
                          "the transfer exceeds 1000 marks")), "mixed")]),
        Para("what must a card issuer do when a card is reported lost",
             S("A card issuer must block a lost card within 2 hours of a report and must not charge the customer for the block.",
               O("card issuer", "block a lost card", "within 2 hours of a report"),
               O("card issuer", "charge the customer for the block", None, None, "must_not"))),
    ])
    statements = Art("statements", "Paper statements", [
        Para("how soon after quarter end must a paper statement be posted",
             W(O("payment firm", "post a paper statement to each customer", "within 10 days of each quarter end"))),
        Para("can a firm charge for a paper statement",
             W(O("payment firm", "charge for a paper statement", None, "the customer asked for more than one each quarter", "must_not"))),
    ], repealed_by="A25")
    cheques = Art("cheques", "Cheque clearing", [
        Para("how quickly must a cheque be cleared after deposit",
             W(O("payment firm", "clear a cheque", "within 3 days of deposit")),
             [("A25", W(O("payment firm", "clear a cheque", "within 3 days of deposit", None, "shall")), "reworded")]),
    ], repealed_by="P27")
    complaints = Art("complaints", "Complaints", [
        Para("how long does a firm have to answer a complaint",
             W(O("payment firm", "answer a complaint", "within 15 days of receipt", None, "required"))),
        Para("does a firm owe interest on a late refund",
             W(O("payment firm", "pay interest on a late refund", None, "the delay exceeds 5 days"))),
        Para(None, T("A complaint about a paper statement under §statements is handled under this Article.")),
    ])

    def fee_schedule(who):
        return O(who, "publish its fee schedule", "within 5 days of a change")

    agents = Art("agents", "Agents and fees", [
        Para("how soon must a new agent be registered with the Authority",
             W(O("payment firm", "register each agent with the Authority", "within 10 days of appointment"))),
        Para("how soon must a changed fee schedule be published", W(fee_schedule("wallet operator")),
             [("A26", W(fee_schedule("payment firm")), "mixed")]),
    ])
    instant = Art("instant", "Instant payments", [
        Para("how quickly must an instant payment be credited",
             W(O("payment firm", "credit an instant payment", "within 60 minutes of acceptance"))),
        Para("when must an agent show the total fee",
             W(O("agent", "display the total fee", None, "a customer starts a payment"))),
    ], inserted_by="A26")
    payee = Art("payee", "Confirmation of payee", [
        Para("must a firm check the payee name on a first transfer",
             W(O("payment firm", "show the result of a payee name check", None, "a customer starts a first transfer"))),
    ], inserted_by="P27")

    parts = [
        ("I", "General provisions", [("Scope and interpretation", [scope, defs])]),
        ("II", "Operational resilience", [("Incidents", [incident]), ("Outsourcing", [outsourcing])]),
        ("III", "Customer money", [("Safeguarding", [safeguarding]), ("Records", [records]), ("Dormancy", [dormant])]),
        ("IV", "Conduct", [("Transfers", [transfers, cheques]), ("Customers", [complaints, statements, agents])]),
    ]
    # Filler articles land in random chapters, so article numbers change with the seed.
    chapters = [c for _, _, cs in parts for _, c in cs]
    for title, text in r.sample(FILLER, 9):
        target = r.choice(chapters)
        target.insert(r.randint(0, len(target)), Art("filler_" + title, title, [Para(None, T(text))]))
    late = [("IV", 1, instant), ("IV", 1, payee)]
    return ins, parts, late


# %% Render the raw text the parser reads
def expand_refs(s: str, numbers: dict) -> str:
    return re.sub(r"§(\w+)", lambda m: f"Article {numbers[m.group(1)]}", s)


def wrap_para(n: int, text: str) -> str:
    # Continuation lines are indented, so "Article 2, within ..." at a line start can't be read as a heading.
    return textwrap.fill(f"({n}) {text}", width=88, initial_indent="    ", subsequent_indent="        ",
                         break_on_hyphens=False, break_long_words=False)


class Rulebook:
    """Generated truth, plus the raw text. The parser sees only `.raw`."""

    def __init__(self, seed: int):
        self.instruments, self.parts, self.late = generate(seed)
        self.numbers, self.articles = {}, {}
        n = 0
        for _, _, chapters in self.parts:
            for _, arts in chapters:
                for a in arts:
                    n += 1
                    self.numbers[a.key] = n
                    self.articles[a.key] = a
        for _, _, a in self.late:
            n += 1
            self.numbers[a.key] = n
            self.articles[a.key] = a
        self.raw = self._render(seed)
        self.truth = self._truth()

    def pid(self, key: str, para: int) -> str:
        return f"{self.numbers[key]}({para})"

    def x(self, s: str) -> str:
        return expand_refs(s, self.numbers)

    def _instr_head(self, i: Instrument) -> list[str]:
        return [f"INSTRUMENT {i.key}: {i.name} of the {AUTHORITY} (fictional, generated, not law)",
                f"Published: {i.published_on}", f"In force: {i.effective_from}"]

    def _render(self, seed: int) -> str:
        out = self._instr_head(self.instruments["BASE"])
        for numeral, part_title, chapters in self.parts:
            out.append(f"PART {numeral} {part_title}")
            for c, (chapter_title, arts) in enumerate(chapters, 1):
                out.append(f"CHAPTER {c} {chapter_title}")
                for a in arts:
                    out.append(f"Article {self.numbers[a.key]} {a.title}")
                    for j, p in enumerate(a.paras, 1):
                        if not p.inserted_by:
                            out.append(wrap_para(j, self.x(p.first.text)))
        order = sorted((i for i in self.instruments.values() if i.key != "BASE"), key=lambda i: i.published_on)
        for i in order:
            out += ["", *self._instr_head(i)]
            for numeral, c, a in self.late:
                if a.inserted_by == i.key:
                    out.append(f"Article {self.numbers[a.key]} is inserted in PART {numeral}, CHAPTER {c}, titled {a.title}:")
                    out += [wrap_para(j, self.x(p.first.text)) for j, p in enumerate(a.paras, 1)]
            for a in self.articles.values():
                if a.repealed_by == i.key:
                    out.append(f"Article {self.numbers[a.key]} is repealed.")
                for j, p in enumerate(a.paras, 1):
                    ref = f"Article {self.numbers[a.key]}({j})"
                    if p.inserted_by == i.key:
                        out += [f"{ref} is inserted:", wrap_para(j, self.x(p.first.text))]
                    for key, wording, _ in p.changes:
                        if key != i.key:
                            continue
                        out += [f"{ref} is repealed."] if wording is None else \
                               [f"{ref} is replaced by:", wrap_para(j, self.x(wording.text))]
        return "\n".join(out) + "\n"

    def _truth(self) -> dict:
        truth = {}
        for a in self.articles.values():
            for j, p in enumerate(a.paras, 1):
                start = self.instruments[p.inserted_by or a.inserted_by or "BASE"]
                label = "added" if (p.inserted_by or a.inserted_by) else None
                steps = [(start, p.first, label)] + [(self.instruments[k], w, l) for k, w, l in p.changes]
                if a.repealed_by:
                    steps.append((self.instruments[a.repealed_by], None, "removed"))
                steps.sort(key=lambda s: s[0].effective_from)
                rows = []
                for s, (i, w, l) in enumerate(steps):
                    end = steps[s + 1][0].effective_from if s + 1 < len(steps) else None
                    clauses = tuple(replace(c, action=self.x(c.action), condition=self.x(c.condition) if c.condition else None)
                                    for c in (w.clauses if w else ()))
                    rows.append(TruthVersion(self.pid(a.key, j), i.key, self.x(w.text) if w else "", clauses,
                                             i.published_on, i.effective_from, end, w is None, l))
                truth[self.pid(a.key, j)] = rows
        return truth


# %% Parse raw text into provisions with versions
@dataclass
class Version:
    pid: str               # "7(2)"
    article: int
    para: int
    path: str              # "Part II > Chapter 1 > Article 7 Incident notification > (2)"
    title: str
    text: str
    instrument: str
    published_on: date
    effective_from: date
    effective_to: date | None = None  # exclusive; filled in once every instrument is read
    repeal: bool = False              # a tombstone: from effective_from on, the provision is gone

    @property
    def vid(self) -> str:
        return f"{self.pid}@{self.effective_from}"

    def in_force_on(self, d: date) -> bool:
        return not self.repeal and self.effective_from <= d and (self.effective_to is None or d < self.effective_to)


HEAD = re.compile(r"^INSTRUMENT (\w+): ")
PART = re.compile(r"^PART (\w+) (.+)$")
CHAPTER = re.compile(r"^CHAPTER (\d+) (.+)$")
ARTICLE = re.compile(r"^Article (\d+) (?!is )(.+)$")
INSERT_ART = re.compile(r"^Article (\d+) is inserted in PART (\w+), CHAPTER (\d+), titled (.+):$")
REPEAL = re.compile(r"^Article (\d+)(?:\((\d+)\))? is repealed\.$")
EDIT = re.compile(r"^Article (\d+)\((\d+)\) is (replaced by|inserted):$")
PARA = re.compile(r"^ {4}\((\d+)\) (.*)$")
CONT = re.compile(r"^ {8}(.*)$")


def parse(raw: str) -> dict:
    """A line-based state machine. Returns {pid: [Version, ...]} sorted by effective date."""
    versions, meta = defaultdict(list), {}
    chapter_titles = {}
    part = chapter = instr = pub = eff = None
    article, current = None, None

    def close_para():
        nonlocal current
        if current:
            current.text = re.sub(r"\s+", " ", current.text).strip()
            versions[current.pid].append(current)
            current = None

    for line in raw.splitlines():
        if (m := CONT.match(line)):
            current.text += " " + m.group(1)
            continue
        close_para()
        if (m := HEAD.match(line)):
            instr = m.group(1)
        elif line.startswith("Published: "):
            pub = date.fromisoformat(line.split(": ")[1])
        elif line.startswith("In force: "):
            eff = date.fromisoformat(line.split(": ")[1])
        elif (m := PART.match(line)):
            part = m.group(1)
        elif (m := CHAPTER.match(line)):
            chapter = m.group(1)
            chapter_titles[(part, chapter)] = m.group(2)
        elif (m := INSERT_ART.match(line)):
            article = int(m.group(1))
            meta[article] = (m.group(2), m.group(3), m.group(4))
        elif (m := ARTICLE.match(line)):
            article = int(m.group(1))
            meta[article] = (part, chapter, m.group(2))
        elif (m := REPEAL.match(line)):
            art, para = int(m.group(1)), m.group(2)
            targets = [p for p in versions if p == f"{art}({para})"] if para else \
                      [p for p in versions if p.startswith(f"{art}(")]
            for p in targets:
                last = versions[p][-1]
                versions[p].append(replace(last, text="", instrument=instr, published_on=pub, effective_from=eff, repeal=True))
        elif (m := EDIT.match(line)):
            article = int(m.group(1))
        elif (m := PARA.match(line)):
            n = int(m.group(1))
            p_part, p_ch, title = meta[article]
            path = f"Part {p_part} > Chapter {p_ch} > Article {article} {title} > ({n})"
            current = Version(f"{article}({n})", article, n, path, title, m.group(2), instr, pub, eff)
    close_para()
    for rows in versions.values():
        rows.sort(key=lambda v: v.effective_from)
        for a, b in zip(rows, rows[1:]):
            a.effective_to = b.effective_from
    return dict(versions)


class Book:
    def __init__(self, versions: dict):
        self.versions = versions
        self.by_vid = {v.vid: v for rows in versions.values() for v in rows}
        self.live = [v for v in self.by_vid.values() if not v.repeal]

    @cache
    def in_force(self, as_of: date, known_on: date | None = None) -> tuple:
        """Provisions in force on as_of. known_on answers a second question: what could you have known on that day?

        A retroactive correction is in force from a date before anyone could read it, so the two dates are separate.
        """
        out = []
        for rows in self.versions.values():
            seen = [v for v in rows if known_on is None or v.published_on <= known_on]
            started = [v for v in seen if v.effective_from <= as_of]
            if started and not started[-1].repeal:
                out.append(started[-1])
        return tuple(out)

    def snapshot(self, as_of: date) -> dict:
        return {v.pid: v for v in self.in_force(as_of)}

    def published_view(self, as_of: date) -> list:
        """The latest text published by as_of, per provision. Mistakes publication for legal effect."""
        out = []
        for rows in self.versions.values():
            seen = [v for v in rows if v.published_on <= as_of]
            if seen:
                newest = max(seen, key=lambda v: (v.published_on, v.effective_from))
                if not newest.repeal:
                    out.append(newest)
        return out

    def status(self, pid: str, as_of: date) -> str:
        rows = self.versions.get(pid)
        if not rows:
            return "unknown"
        current = self.snapshot(as_of).get(pid)
        pending = [v for v in rows if v.published_on <= as_of < v.effective_from]
        word = f"in force ({current.vid})" if current else \
            ("repealed" if any(v.repeal and v.effective_from <= as_of for v in rows) else "not yet in force")
        if pending:
            p = pending[-1]
            word += f"; published change from {p.effective_from}" + (" repeals it" if p.repeal else "")
        return word


# %% As-of retrieval against the naive indexes
class Index:
    """ragkit's BM25 over one chosen set of versions. `allow` runs before ranking, as a filter in the query."""

    def __init__(self, versions):
        self.versions = list(versions)
        self.bm25 = BM25([f"{v.title}. {v.text}" for v in self.versions])

    def search(self, query: str, k: int, allow=None) -> list[str]:
        scores = self.bm25.scores(query)
        hits = [(-s, v.vid) for s, v in zip(scores, self.versions) if s > 0 and (allow is None or allow(v))]
        return [vid for _, vid in sorted(hits)[:k]]


class Retrievers:
    def __init__(self, book: Book):
        self.book = book
        self.all = Index(book.live)
        self.latest = Index(book.published_view(TODAY))

    def run(self, name: str, q: str, as_of: date, k: int) -> list[str]:
        if name == "as-of":
            return self.all.search(q, k, lambda v: v.in_force_on(as_of))
        if name == "published-on filter":
            allowed = {v.vid for v in self.book.published_view(as_of)}
            return self.all.search(q, k, lambda v: v.vid in allowed)
        if name == "latest-only":
            return self.latest.search(q, k)
        if name == "all-versions":
            return self.all.search(q, k)
        raise ValueError(name)


RETRIEVERS = ["as-of", "published-on filter", "latest-only", "all-versions"]


@dataclass(frozen=True)
class GoldQ:
    question: str
    as_of: date
    target: str         # the provision asked about
    gold: str | None    # the version in force, or None when nothing is in force
    kind: str


def build_gold(rb: Rulebook) -> list[GoldQ]:
    """Questions from generator truth, not from the parser. One per version, plus the windows between dates."""
    out = []

    def mid(a, b):
        return a + (b - a) // 2

    for a in rb.articles.values():
        for j, p in enumerate(a.paras, 1):
            if not p.question:
                continue
            pid = rb.pid(a.key, j)
            rows = rb.truth[pid]
            for s, v in enumerate(rows):
                prev = rows[s - 1] if s else None
                if v.published_on < v.effective_from and v.published_on <= TODAY:
                    # The window between publication and effect: the old text still governs.
                    d = mid(v.published_on, min(v.effective_from, TODAY))
                    if prev is not None:
                        out.append(GoldQ(p.question, d, pid, None if prev.repeal else f"{pid}@{prev.effective_from}", "published, not in force"))
                if v.repeal:
                    d = max(v.effective_from + timedelta(days=10), TODAY)
                    out.append(GoldQ(p.question, d, pid, None, "repealed"))
                    continue
                vid = f"{pid}@{v.effective_from}"
                if v.published_on > v.effective_from:
                    out.append(GoldQ(p.question, mid(v.effective_from, v.published_on), pid, vid, "retroactive"))
                if v.effective_from > TODAY:
                    out.append(GoldQ(p.question, v.effective_from + timedelta(days=10), pid, vid, "future date"))
                elif v.effective_to and v.effective_to <= TODAY:
                    out.append(GoldQ(p.question, mid(v.effective_from, v.effective_to), pid, vid, "superseded"))
                else:
                    kind = "never amended" if len(rows) == 1 else "current"
                    out.append(GoldQ(p.question, TODAY, pid, vid, kind))
                if prev is None and (p.inserted_by or a.inserted_by):
                    out.append(GoldQ(p.question, v.published_on - timedelta(days=30), pid, None, "not commenced"))
    return out


def score_retrieval(ret: Retrievers, gold: list[GoldQ], k: int) -> dict:
    """recall@k on answerable questions; wrong@k: a not-in-force version of the target came back; wrong@1: rank 1 is not in force."""
    book = ret.book
    table = {name: defaultdict(lambda: Counter()) for name in RETRIEVERS}
    for q in gold:
        for name in RETRIEVERS:
            hits = ret.run(name, q.question, q.as_of, k)
            vs = [book.by_vid[h] for h in hits]
            for bucket in (q.kind, "ALL"):
                c = table[name][bucket]
                c["n"] += 1
                if q.gold:
                    c["answerable"] += 1
                    c["hit"] += q.gold in hits
                c["wrong_k"] += any(v.pid == q.target and not v.in_force_on(q.as_of) for v in vs)
                c["wrong_1"] += bool(vs) and not vs[0].in_force_on(q.as_of)
    return table


def print_retrieval(table: dict, k: int) -> None:
    kinds = sorted({b for t in table.values() for b in t} - {"ALL"})
    head = f"{'question kind':26}{'n':>4}" + "".join(f"{n:>24}" for n in RETRIEVERS)
    print(head)
    print(f"{'':30}" + f"{'recall  wrong@' + str(k) + '':>24}" * len(RETRIEVERS))
    for kind in kinds + ["ALL"]:
        row = f"{kind:26}{table['as-of'][kind]['n']:>4}"
        for name in RETRIEVERS:
            c = table[name][kind]
            recall = f"{c['hit'] / c['answerable']:.2f}" if c["answerable"] else "  - "
            row += f"{recall + '    ' + format(c['wrong_k'] / c['n'], '.2f'):>24}"
        print(row)
    print("rank 1 not in force:" + " " * 10 + "".join(
        f"{table[n]['ALL']['wrong_1'] / table[n]['ALL']['n']:>24.2f}" for n in RETRIEVERS))


# %% Cross-reference expansion
REF = re.compile(r"Article (\d+)(?:\((\d+)\))?")
TERM = re.compile(r'^"([^"]+)" means')


def resolve_refs(book: Book, v: Version, view: dict) -> tuple[list, list]:
    """Follow the references in v.text inside one view of the book. Returns (versions found, dangling references)."""
    found, dangling = [], []
    for art, para in REF.findall(v.text):
        if para:
            targets = [view[f"{art}({para})"]] if f"{art}({para})" in view else []
        else:
            targets = [t for t in view.values() if t.article == int(art)]
            # "as defined in Article 2" means one paragraph of Article 2, the one defining a term this text uses.
            defined = [t for t in targets if (m := TERM.match(t.text)) and m.group(1) in v.text]
            targets = defined or targets
        if targets:
            found += targets
        else:
            dangling.append(f"Article {art}" + (f"({para})" if para else ""))
    return found, dangling


def with_expansion(book: Book, hits: list[str], view: dict) -> list[str]:
    out = list(hits)
    for vid in hits:
        for t in resolve_refs(book, book.by_vid[vid], view)[0]:
            if t.vid not in out:
                out.append(t.vid)
    return out


XREF_QUESTIONS = [
    # (article key, paragraph, question). Phrased in the operative paragraph's words, as a customer would ask it.
    ("incident", 1, "does this event count, and how fast must a firm notify the Authority of a reportable incident after detection"),
    ("incident", 2, "does this event count, and how fast must a firm inform another payment firm hit by a reportable incident"),
    ("transfers", 1, "does this payment count, and what must a firm verify about the source of funds for a high-value transfer before execution"),
    ("dormant", 1, "does this account count, and how fast must a firm notify the customer when an account becomes dormant"),
    ("safeguarding", 1, "is this money covered, and how fast must a firm reconcile safeguarded funds after each settlement date"),
]


def build_xref_gold(rb: Rulebook) -> list:
    rows = []
    for key, j, question in XREF_QUESTIONS:
        pid = rb.pid(key, j)
        d_key, d_j = rb.articles[key].paras[j - 1].uses[0]
        def_pid = rb.pid(d_key, d_j)
        dates = sorted({v.effective_from + timedelta(days=20) for v in rb.truth[def_pid] if v.effective_from <= TODAY} | {TODAY})
        for d in dates:
            gold = set()
            for p in (pid, def_pid):
                gold |= {f"{p}@{v.effective_from}" for v in rb.truth[p]
                         if not v.repeal and v.effective_from <= d and (v.effective_to is None or d < v.effective_to)}
            rows.append((question, d, gold))
    return rows


def score_xref(ret: Retrievers, rows: list, k: int) -> dict:
    book, out = ret.book, {}
    latest = {v.pid: v for v in book.published_view(TODAY)}
    for name in ["no expansion", "expand to latest", "expand as-of"]:
        full = wrong = 0
        for question, d, gold in rows:
            hits = ret.run("as-of", question, d, k)
            if name == "expand to latest":
                hits = with_expansion(book, hits, latest)
            elif name == "expand as-of":
                hits = with_expansion(book, hits, book.snapshot(d))
            full += gold <= set(hits)
            wrong += any(not book.by_vid[h].in_force_on(d) for h in hits)
        out[name] = (full / len(rows), wrong / len(rows))
    return out


# %% Obligation extraction: a rule-based stand-in for a model
@dataclass(frozen=True)
class Obligation:
    who: str
    modality: str
    action: str
    deadline: str | None
    condition: str | None
    source_article: str
    version: str


MODAL = re.compile(r"^(?:Where (?P<lead>[^,]+), )?(?P<who>.+?) (?P<modal>must not|shall not|must|shall|is required to) (?P<rest>.+?)\.?$", re.IGNORECASE)
DEADLINE = re.compile(r",?\s*\b(within [^,.;]+?|no later than [^,.;]+?|for at least [^,.;]+?|at least \d+ \w+ before [^,.;]+?)(?=\s+(?:unless|if)\b|[,.;]|$)")
CONDITION = re.compile(r"\s+(?:unless|if)\s+(.+)$")


def extract_rules(v: Version) -> list[Obligation]:
    """Three regular expressions. Deliberately limited: it misses "No X may", misreads passives, reads one duty per sentence."""
    if TERM.match(v.text):
        return []
    m = MODAL.match(v.text)
    if not m:
        return []
    rest, condition = m.group("rest"), m.group("lead")
    if (c := CONDITION.search(rest)):
        condition, rest = c.group(1), rest[:c.start()]
    deadline = None
    if (d := DEADLINE.search(rest)):
        deadline, rest = d.group(1), rest[:d.start()] + rest[d.end():]
    who = re.sub(r"^(a|an|each|every|the)\s+", "", m.group("who").strip(), flags=re.IGNORECASE).lower()
    modality = "must_not" if m.group("modal").lower().endswith("not") else "must"
    return [Obligation(who, modality, rest.strip(), deadline, condition, v.pid, v.vid)]


def gold_extractor(rb: Rulebook):
    index = {f"{pid}@{t.effective_from}": t for pid, rows in rb.truth.items() for t in rows}

    def extract(v: Version) -> list[Obligation]:
        return [Obligation(c.who, c.modality, c.action, c.deadline, c.condition, v.pid, v.vid)
                for c in index[v.vid].clauses]
    return extract


def norm(s: str | None) -> str | None:
    return None if s is None else " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def similar(a: str, b: str, threshold: float = 0.8) -> bool:
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / max(len(x | y), 1) >= threshold


def field_correct(f: str, g: Obligation, e: Obligation) -> bool:
    if f == "action":
        return similar(g.action, e.action)
    a, b = getattr(g, f), getattr(e, f)
    return norm(a) == norm(b) if f in ("who", "deadline", "condition") else a == b


def score_extraction(book: Book, gold, extract) -> dict:
    """Align by version and position in the paragraph. A missed record is wrong on every field."""
    right, total, tp, fp, fn = Counter(), 0, 0, 0, 0
    errors = []
    for v in book.live:
        g, e = gold(v), extract(v)
        total += len(g)
        tp += min(len(g), len(e))
        fp += max(0, len(e) - len(g))
        fn += max(0, len(g) - len(e))
        if len(e) > len(g):
            errors.append((v.vid, "spurious record", e[len(g)].who))
        for i, gr in enumerate(g):
            er = e[i] if i < len(e) else None
            if er is None:
                errors.append((v.vid, "missed record", gr.action[:48]))
            for f in FIELDS:
                ok = er is not None and field_correct(f, gr, er)
                right[f] += ok
                if er is not None and not ok:
                    errors.append((v.vid, f, f"{getattr(er, f)!r} vs gold {getattr(gr, f)!r}"))
    return {"fields": {f: right[f] / total for f in FIELDS}, "precision": tp / (tp + fp), "recall": tp / (tp + fn),
            "n": total, "errors": errors}


# %% Change detection
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "five": 5, "ten": 10, "fifteen": 15, "twenty": 20, "thirty": 30, "sixty": 60}
UNIT_MINUTES = {"minute": 1, "hour": 60, "day": 1440, "week": 10080, "month": 43200, "year": 525600}
SPAN = re.compile(r"(\d+|" + "|".join(NUM_WORDS) + r") (minute|hour|day|week|month|year)s?")


def span_minutes(deadline: str) -> int | None:
    m = SPAN.search(deadline.lower())
    if not m:
        return None
    n = NUM_WORDS.get(m.group(1)) or int(m.group(1))
    return n * UNIT_MINUTES[m.group(2)]


def compare_deadline(old: str | None, new: str | None) -> str | None:
    if norm(old) == norm(new):
        return None
    if old is None:
        return "tightened"
    if new is None:
        return "loosened"
    a, b = span_minutes(old), span_minutes(new)
    if a is None or b is None or a == b:
        return "mixed"
    # "within 3 days": shorter is tighter. "for at least 7 years" or "at least 60 days before": longer is tighter.
    longer_is_tighter = norm(old).startswith(("for ", "at least"))
    return "tightened" if (b > a) == longer_is_tighter else "loosened"


def classify_pair(old: Obligation, new: Obligation) -> str:
    signals = set()
    if old.modality != new.modality or norm(old.who) != norm(new.who) or not similar(old.action, new.action):
        signals.add("mixed")
    if (d := compare_deadline(old.deadline, new.deadline)):
        signals.add(d)
    if norm(old.condition) != norm(new.condition):
        if old.condition is None:
            signals.add("loosened")     # a new condition narrows when the duty applies
        elif new.condition is None:
            signals.add("tightened")    # the duty now applies without the exception
        else:
            signals.add("mixed")
    if not signals:
        return "reworded"
    return signals.pop() if len(signals) == 1 else "mixed"


def classify_change(old: Version | None, new: Version | None, extract) -> str:
    text = (new or old).text
    if TERM.match(text):
        return "definition_changed"
    o, n = extract(old) if old else [], extract(new) if new else []
    if old is None:
        return "added" if n else "text_only"
    if new is None:
        return "removed" if o else "text_only"
    if not o and not n:
        return "text_only"       # the extractor saw no duty. That is not the same as "nothing changed": it goes to review.
    if len(o) != len(n):
        return "mixed"
    labels = {classify_pair(a, b) for a, b in zip(o, n)} - {"reworded"}
    if not labels:
        return "reworded"
    return labels.pop() if len(labels) == 1 else "mixed"


def diff_snapshots(book: Book, a: date, b: date, extract) -> dict:
    """{pid: label} for every provision whose in-force version differs between two dates."""
    before, after = book.snapshot(a), book.snapshot(b)
    out = {}
    for pid in sorted(set(before) | set(after)):
        old, new = before.get(pid), after.get(pid)
        if old is new or (old and new and old.vid == new.vid):
            continue
        out[pid] = classify_change(old, new, extract)
    return out


def gold_changes(rb: Rulebook) -> dict:
    """{instrument key: {pid: label}} straight from the generator."""
    out = defaultdict(dict)
    for pid, rows in rb.truth.items():
        for t in rows:
            if t.label:
                out[t.instrument][pid] = t.label
    return out


# %% Downstream customer controls
CONTROL_SPECS = [
    # Controls at Fennick Pay, a fictional customer of a fictional compliance tool, mapped to the paragraphs they implement.
    ("C-01", "Incident escalation runbook", [("incident", 1), ("incident", 2)]),
    ("C-02", "Post-incident report calendar", [("incident", 3)]),
    ("C-03", "Vendor onboarding checklist", [("outsourcing", 1), ("outsourcing", 2)]),
    ("C-04", "Daily reconciliation job", [("safeguarding", 1)]),
    ("C-05", "Record retention schedule", [("records", 1)]),
    ("C-06", "Agent register procedure", [("records", 2)]),
    ("C-07", "Dormancy mailer", [("dormant", 1)]),
    ("C-08", "Transfer screening threshold", [("transfers", 1)]),
    ("C-09", "Statement printing contract", [("statements", 1), ("statements", 2)]),
    ("C-10", "Cheque desk procedure", [("cheques", 1)]),
    ("C-11", "Instant rail service level", [("instant", 1)]),
    ("C-12", "Complaints desk procedure", [("complaints", 1)]),
    ("C-13", "Fee publication process", [("agents", 2)]),
]


def controls_for(rb: Rulebook) -> dict:
    return {c: (name, {rb.pid(k, j) for k, j in refs}) for c, name, refs in CONTROL_SPECS}


def controls_gold(rb: Rulebook, labels: dict) -> set:
    """Generator truth: a control is due for review if its paragraph changed in substance, or a definition it relies on did."""
    changed = {p for p, l in labels.items() if l != "reworded"}
    defs = {p for p, l in labels.items() if l == "definition_changed"}
    out = set()
    for c, _, refs in CONTROL_SPECS:
        for k, j in refs:
            uses = {rb.pid(*u) for u in rb.articles[k].paras[j - 1].uses}
            if rb.pid(k, j) in changed or uses & defs:
                out.add(c)
    return out


def controls_flagged(rb: Rulebook, book: Book, labels: dict, after: date, method: str) -> dict:
    """{control: reason}. Methods: text diff; obligation diff; obligation diff plus the reference graph."""
    controls = controls_for(rb)
    if method == "text diff":
        direct = set(labels)
    else:
        direct = {p for p, l in labels.items() if l != "reworded"}
    via = {}
    if method == "obligations + references":
        view = book.snapshot(after)
        defs = {p for p, l in labels.items() if l == "definition_changed"}
        for v in view.values():
            for t in resolve_refs(book, v, view)[0]:
                if t.pid in defs:
                    via[v.pid] = t.pid
    out = {}
    for c, (_, pids) in controls.items():
        for p in sorted(pids):
            if p in direct:
                out[c] = f"{p}: {labels[p]}"
            elif p in via:
                out[c] = f"{p} relies on {via[p]}: {labels[via[p]]}"
    return out


# %% Verbatim citation check
@dataclass(frozen=True)
class Answer:
    name: str
    as_of: date
    cite: str | None
    quote: str | None
    expect: str


def squash(s: str) -> str:
    return " ".join(s.lower().split())


def check_citation(book: Book, a: Answer) -> str:
    """Does the quote appear, verbatim apart from case and whitespace, in the cited version in force on the as-of date?"""
    if not a.quote:
        return "no_quote"
    rows = book.versions.get(a.cite)
    if rows is None:
        return "unknown_provision"
    quote = squash(a.quote)
    current = book.snapshot(a.as_of).get(a.cite)
    if current and quote in squash(current.text):
        return "ok"
    for v in rows:
        if v.repeal or quote not in squash(v.text):
            continue
        if v.effective_from > a.as_of:
            return "quote_not_yet_in_force"
        return "quote_from_superseded" if current else "quote_from_repealed"
    if any(quote in squash(v.text) for v in book.in_force(a.as_of)):
        return "wrong_provision"
    return "quote_not_found"


def naive_any_version(book: Book, a: Answer) -> bool:
    """The check most pipelines start with: the quote is somewhere in the document we hold."""
    return bool(a.quote) and any(squash(a.quote) in squash(v.text) for v in book.versions.get(a.cite, []) if not v.repeal)


def naive_fuzzy(book: Book, a: Answer) -> bool:
    """The fuzzy quote match from 08-eval note 07, on the right version. Good for a help page, unsafe for a number in a rule."""
    current = book.snapshot(a.as_of).get(a.cite)
    if not a.quote or current is None:
        return False
    q, p = a.quote.lower(), current.text.lower()
    return SequenceMatcher(None, q, p).find_longest_match().size / len(q) >= FUZZY_THRESHOLD


def planted_answers(rb: Rulebook) -> list[Answer]:
    i = rb.instruments
    def text(key, j, s):  # the text of version s of a paragraph
        return rb.truth[rb.pid(key, j)][s].text
    p_notify, p_paper = rb.pid("incident", 1), rb.pid("statements", 1)
    p_records, p_mix = rb.pid("records", 1), rb.pid("safeguarding", 2)
    after_a24 = i["A24"].effective_from + timedelta(days=30)

    def clause(s):  # an answer usually quotes the clause it needs, so the number sits near the end of the quote
        return s[:s.index(" hours") + len(" hours")]

    changed_number = re.sub(r"within \d+", "within 99", clause(text("incident", 1, 1)))
    return [
        Answer("right version, today", TODAY, p_notify, clause(text("incident", 1, 1)), "ok"),
        Answer("old version, asked about the old date", i["BASE"].effective_from + timedelta(days=30), p_notify, text("incident", 1, 0), "ok"),
        Answer("old deadline, asked about today", TODAY, p_notify, clause(text("incident", 1, 0)), "quote_from_superseded"),
        Answer("PLANTED: quotes a repealed article", TODAY, p_paper, text("statements", 1, 0), "quote_from_repealed"),
        Answer("quotes the repealed article before repeal", after_a24, p_paper, text("statements", 1, 0), "ok"),
        Answer("quotes text published, not yet in force", TODAY, p_notify, clause(text("incident", 1, 2)), "quote_not_yet_in_force"),
        Answer("right article, invented number", TODAY, p_notify, changed_number, "quote_not_found"),
        Answer("real quote, wrong article", TODAY, p_records, text("safeguarding", 2, 0), "wrong_provision"),
        Answer("cites an article that doesn't exist", TODAY, "99(1)", text("safeguarding", 2, 0), "unknown_provision"),
        Answer("paraphrase, no quote", TODAY, p_mix, None, "no_quote"),
    ]


# %% Run it all
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--show-rulebook", action="store_true")
    args = ap.parse_args()
    k = args.k

    print(f"Fictional rulebook of the {AUTHORITY}, generated from seed {args.seed}. Not law. 'Today' is fixed at {TODAY}.\n")

    # --- 1. Parsing
    rb = Rulebook(args.seed)
    if args.show_rulebook:
        print(rb.raw)
    versions = parse(rb.raw)
    book = Book(versions)
    assert set(versions) == set(rb.truth), "parser lost or invented a provision"
    for pid, rows in rb.truth.items():
        assert [v.effective_from for v in versions[pid]] == [t.effective_from for t in rows], pid
        assert [v.effective_to for v in versions[pid]] == [t.effective_to for t in rows], pid
        assert [v.published_on for v in versions[pid]] == [t.published_on for t in rows], pid
        assert [v.text for v in versions[pid]] == [t.text for t in rows], pid
    probe = [rb.instruments[i].effective_from + timedelta(days=d) for i in rb.instruments for d in (-1, 0, 1)] + [TODAY]
    for d in probe:
        by_fields = {v.vid for v in book.live if v.in_force_on(d)}
        assert by_fields == {v.vid for v in book.in_force(d)}, f"two definitions of in force disagree on {d}"
        pids = [v.pid for v in book.in_force(d)]
        assert len(pids) == len(set(pids)), f"two versions of one provision in force on {d}"
    print("1. PARSING")
    print(f"   {len(rb.instruments)} instruments, {len(versions)} provisions, {len(book.live)} live versions, "
          f"{sum(v.repeal for v in book.by_vid.values())} repeals. The parsed timeline matches generator truth exactly.")
    amended = rb.pid("incident", 1)
    print("   Hierarchy:", versions[amended][0].path)
    for v in versions[amended]:
        print(f"   {v.vid:24} published {v.published_on}  effective to {v.effective_to or 'open'!s:<12} {v.instrument}")
    print(f"   Status of {amended} today:", book.status(amended, TODAY))
    print(f"   Status of {rb.pid('statements', 1)} today:", book.status(rb.pid("statements", 1), TODAY))
    print(f"   Status of {rb.pid('cheques', 1)} today:", book.status(rb.pid("cheques", 1), TODAY))
    print(f"   Status of {rb.pid('payee', 1)} today:", book.status(rb.pid("payee", 1), TODAY))
    # Effective and published are separate axes: a retroactive correction shows it.
    retro_pid, r25 = rb.pid("incident", 3), rb.instruments["R25"]
    d = r25.effective_from + timedelta(days=10)
    said_then = {v.pid: v for v in book.in_force(d, known_on=d)}[retro_pid]
    said_now = book.snapshot(d)[retro_pid]
    assert said_then.vid != said_now.vid
    print(f"   Retroactive {retro_pid}, on {d}: readable that day {said_then.vid}; the law as now known {said_now.vid}.")
    print("   Dangling references today: " + ", ".join(
        f"{v.pid} cites {x}" for v in book.in_force(TODAY) for x in resolve_refs(book, v, book.snapshot(TODAY))[1]))

    # --- 2. As-of retrieval
    ret = Retrievers(book)
    gold = build_gold(rb)
    table = score_retrieval(ret, gold, k)
    print(f"\n2. AS-OF RETRIEVAL ({len(gold)} generated questions, BM25 from ragkit, k={k})")
    print_retrieval(table, k)
    print("   wrong@k: a version of the asked-about provision that isn't in force on the as-of date reached the top k.")
    assert table["as-of"]["ALL"]["wrong_k"] == 0, "the as-of filter let a version through that is not in force"
    assert table["as-of"]["ALL"]["wrong_1"] == 0
    for naive in ("latest-only", "all-versions", "published-on filter"):
        assert table[naive]["ALL"]["wrong_k"] > 0, naive
    assert table["as-of"]["ALL"]["hit"] > table["latest-only"]["ALL"]["hit"]
    print("   The as-of zero is by construction: the filter can't return what it excludes, given correct dates. Its recall is")
    print("   what BM25 manages on these questions, and the all-versions column shows recall hiding the wrong text beside it.")

    # --- 3. Cross-reference expansion
    xrows = build_xref_gold(rb)
    xref = score_xref(ret, xrows, k)
    print(f"\n3. CROSS-REFERENCE EXPANSION ({len(xrows)} questions whose answer needs the operative paragraph and its definition, k={k})")
    print(f"   {'method':22}{'context complete':>18}{'not in force':>16}")
    for name, (full, wrong) in xref.items():
        print(f"   {name:22}{full:>18.2f}{wrong:>16.2f}")
    failing = None
    for question, d, g in xrows:
        hits = ret.run("as-of", question, d, k)
        if not g <= set(hits) and g <= set(with_expansion(book, hits, book.snapshot(d))):
            failing = (question, d, g, hits)
            break
    if failing:
        question, d, g, hits = failing
        print(f"   Example, as of {d}: {question!r}")
        print(f"     without expansion: {hits}")
        print(f"     missing:           {sorted(g - set(hits))}")
        for vid in sorted(g - set(hits)):
            print(f"     {book.by_vid[vid].text}")
    else:
        print(f"   At k={k} no question fails without expansion. On a rulebook this small, a large k pulls the definition in by luck.")
    if k <= K:
        assert failing, "expected a question that needs expansion"
        assert xref["expand as-of"][0] > xref["no expansion"][0]
    assert xref["expand as-of"][1] == 0, "as-of expansion pulled a version not in force"
    assert xref["expand to latest"][1] > 0, "version-blind expansion should pull a later definition"

    # --- 4. Obligation extraction
    gold_x = gold_extractor(rb)
    oracle = score_extraction(book, gold_x, gold_x)
    assert all(v == 1.0 for v in oracle["fields"].values()), "the harness fails an oracle: the scorer is broken"
    rules = score_extraction(book, gold_x, extract_rules)
    print(f"\n4. OBLIGATION EXTRACTION ({rules['n']} gold records across all versions)")
    print("   The extractor is a few regular expressions. A real system would use a model here. These scores measure the")
    print("   harness on sentences from one generator. They say nothing about how well any model or rule set reads real rules.")
    print(f"   {'field':16}{'rule-based':>12}{'oracle':>10}")
    for f in FIELDS:
        print(f"   {f:16}{rules['fields'][f]:>12.2f}{oracle['fields'][f]:>10.2f}")
    print(f"   {'records':16}  precision {rules['precision']:.2f}  recall {rules['recall']:.2f}")
    print("   source_article and version come from the parser, so they fall only when a record is missed.")
    print("   Errors, grouped:", dict(Counter(e[1] for e in rules["errors"])))
    for vid, f, detail in rules["errors"][:4]:
        print(f"     {vid:24} {f:16} {detail}")
    assert rules["fields"]["who"] < 1.0, "the stand-in should visibly miss passives"

    # --- 5. Change detection
    gold_labels = gold_changes(rb)
    print("\n5. CHANGE DETECTION (every instrument, compared the day before and the day it takes effect)")
    steps = [i for i in sorted(rb.instruments.values(), key=lambda i: i.effective_from) if i.key != "BASE"]
    correct = {"gold records": 0, "rule-based records": 0}
    total = 0
    confusion = Counter()
    review = {m: Counter() for m in ["text diff", "obligation diff", "obligations + references"]}
    for i in steps:
        a, b = i.effective_from - timedelta(days=1), i.effective_from
        truth = gold_labels[i.key]
        from_gold = diff_snapshots(book, a, b, gold_x)
        from_rules = diff_snapshots(book, a, b, extract_rules)
        assert set(from_gold) == set(truth), f"{i.key}: the diff disagrees with the generator on what changed"
        total += len(truth)
        for pid, label in truth.items():
            correct["gold records"] += from_gold[pid] == label
            correct["rule-based records"] += from_rules[pid] == label
            if from_rules[pid] != label:
                confusion[(label, from_rules[pid])] += 1
        want = controls_gold(rb, truth)
        for m, c in review.items():
            got = set(controls_flagged(rb, book, from_rules, b, m))
            c["tp"] += len(got & want)
            c["fp"] += len(got - want)
            c["fn"] += len(want - got)
    print(f"   {total} changed provisions. Label accuracy: gold records through the classifier "
          f"{correct['gold records'] / total:.2f}; rule-based records {correct['rule-based records'] / total:.2f}.")
    print("   The first number tests the classifier alone, the second adds extraction error on top.")
    print("   Rule-based mistakes (truth -> predicted):", {f"{a} -> {b}": n for (a, b), n in sorted(confusion.items())})
    assert correct["gold records"] == total, "the classifier mislabels a change even on perfect records"
    print("\n   Which customer controls need review, over all instruments:")
    print(f"   {'method':28}{'precision':>10}{'recall':>8}{'flagged':>9}")
    prf = {}
    for m, c in review.items():
        p, r = c["tp"] / max(c["tp"] + c["fp"], 1), c["tp"] / max(c["tp"] + c["fn"], 1)
        prf[m] = (p, r)
        print(f"   {m:28}{p:>10.2f}{r:>8.2f}{c['tp'] + c['fp']:>9}")
    assert prf["obligations + references"][1] > prf["obligation diff"][1], "the reference graph should find more"
    assert prf["obligation diff"][0] >= prf["text diff"][0]

    pending = rb.instruments["P27"]
    a, b = TODAY, pending.effective_from
    labels = diff_snapshots(book, a, b, extract_rules)
    print(f"\n   Published, not yet in force: {pending.name}, from {pending.effective_from}. Review queue today:")
    for pid, label in labels.items():
        print(f"     {pid:8} {label}")
    controls = controls_for(rb)
    for c, reason in sorted(controls_flagged(rb, book, labels, b, "obligations + references").items()):
        print(f"     {c}  {controls[c][0]:32} {reason}")

    # --- 6. Citation check
    answers = planted_answers(rb)
    print(f"\n6. VERBATIM CITATION CHECK ({len(answers)} planted answers)")
    print(f"   {'answer':44}{'as of':>12}{'any version':>13}{'fuzzy':>7}  verbatim, version in force")
    wrongly_accepted = Counter()
    for a in answers:
        label = check_citation(book, a)
        assert label == a.expect, f"{a.name}: got {label}, expected {a.expect}"
        any_v, fuzzy = naive_any_version(book, a), naive_fuzzy(book, a)
        wrongly_accepted["any version"] += any_v and a.expect != "ok"
        wrongly_accepted["fuzzy"] += fuzzy and a.expect != "ok"
        print(f"   {a.name:44}{a.as_of!s:>12}{'pass' if any_v else 'fail':>13}{'pass' if fuzzy else 'fail':>7}  {label}")
    bad = sum(a.expect != "ok" for a in answers)
    print(f"   Bad answers accepted, of {bad}: any version {wrongly_accepted['any version']}, "
          f"fuzzy at {FUZZY_THRESHOLD} {wrongly_accepted['fuzzy']}, verbatim 0.")
    assert wrongly_accepted["any version"] > 0
    if FUZZY_THRESHOLD <= 0.9:
        assert wrongly_accepted["fuzzy"] > 0, "the fuzzy check should let a changed number through"

    print("\nAll invariants held. Every number above describes this generated rulebook, not real regulation or any product.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
