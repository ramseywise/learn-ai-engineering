#!/usr/bin/env python3
"""Find the well-cited readings a home is missing, by topic, before the citation graph can.

The citation graph grows outward from papers we already hold, so a home that holds few
(data-analytics, data-engineering, programming) gets almost nothing from it. This script
searches by topic instead and adds what it finds to the ledger as `new` rows, so the usual
`potw.py triage` scores them. Plan: subject-areas-plan.md.

  queries   one Haiku call per home turns each note's headings into 2-4 search queries:
            discover/queries-<home>.json. Review and edit that file before `search`.
  search    run each query through OpenAlex semantic search, keep works cited at least
            --min-cites times, drop what the ledger already has, add the rest
            (source "openalex", discovered_for <home>, discovered_note <note>)
  curated   resolve discover/curated.jsonl (hand-picked readings) by title in OpenAlex and
            add them (source "curated"); prints the ones it can't find
  review    write discover/review-<home>.md: one table per note for a keep/drop pass;
            --apply reads your marks back into the ledger

Every OpenAlex response is cached in discover/cache/ (gitignored), so a re-run costs nothing.
Semantic search is limited to 1 request a second; without OPENALEX_API_KEY all requests from
this IP share a free budget of about 100 semantic searches a day. When it runs out, `search`
stops and the next run resumes from the cache.

  python3 scripts/papers/discover.py queries --home analytics
  python3 scripts/papers/discover.py search --home analytics
  python3 scripts/papers/discover.py curated
  python3 scripts/papers/potw.py triage --home analytics
  python3 scripts/papers/discover.py review --home analytics
  python3 scripts/papers/discover.py review --home analytics --apply
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potw  # noqa: E402
import citegraph as cg  # noqa: E402

HERE = Path(__file__).resolve().parent
DISCOVER = HERE / "discover"
CACHE = DISCOVER / "cache"
CURATED = DISCOVER / "curated.jsonl"
REPO = potw.REPO
log = potw.log

OA_FIELDS = ("id,doi,title,publication_year,type,ids,locations,best_oa_location,primary_location,"
             "cited_by_count,authorships,abstract_inverted_index")
# Work types worth reading; datasets, errata, paratext and theses are not.
KEEP_TYPES = {"article", "conference-paper", "book", "book-chapter", "review", "preprint", "report", "proceedings-article"}
SEMANTIC_PAUSE = 1.1  # the semantic endpoint allows one request a second
# Programming searches only the notes where a primary paper exists: SQL, types, concurrency, design.
NOTE_FILTER = {"programming": re.compile(r"sql/notes/|typescript/notes/0[2-6]|python/03-[^/]+/notes/0[1567]")}

QUERIES_PROMPT = """You are writing search queries to find the best-known readings behind a course's notes.
The home is `{home}`: {scope}
The reader is {audience}.

For each note below, write 2 to 4 queries for a semantic search engine over scholarly works
(OpenAlex). Write each query the way the title or first sentence of the source paper or book
would read: name the method, system or result, not the note's teaching angle. Aim at the
landmark papers and standard textbooks a note on this topic should cite: the paper that
introduced the idea, the main survey or textbook. Skip notes that are pure tooling or
syntax walkthroughs (give them an empty list).{shared}

Notes (path, then its headings):
{notes}

Reply with ONLY a JSON object mapping each note path to its list of queries, no prose:
{{"data-analytics/notes/01-example.md": ["...", "..."]}}
"""


# --- OpenAlex -------------------------------------------------------------------


class BudgetSpent(Exception):
    """OpenAlex refused with 429 for the day (or longer than we wait)."""


def cached_get(params, semantic=False):
    """GET an OpenAlex works query through the on-disk cache."""
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    try:
        data = cg.get_json(cg.oa_url(params), tries=3 if semantic else 6)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise BudgetSpent(e.read()[:300].decode(errors="ignore")) from e
        raise
    if semantic:
        time.sleep(SEMANTIC_PAUSE)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {i: word for word, idxs in inv.items() for i in idxs}
    return " ".join(pos[i] for i in sorted(pos))


def row_from_work(w, home, source, note=None, query=None):
    aid = cg.arxiv_of(w)
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
    oa = w.get("best_oa_location") or {}
    prim = w.get("primary_location") or {}
    auth = (w.get("authorships") or [{}])[0].get("author") or {}
    key = aid or (f"doi:{doi}" if doi else f"openalex:{cg.short(w['id'])}")
    return {
        "key": key, "arxiv": aid, "doi": doi, "openalex": cg.short(w["id"]),
        "title": w.get("title") or "", "blurb": abstract(w)[:2000],
        "year": str(w.get("publication_year") or ""), "first_author": auth.get("display_name"),
        "venue": (prim.get("source") or {}).get("display_name"),
        "url": f"https://doi.org/{doi}" if doi else (prim.get("landing_page_url") or w["id"]),
        "oa_pdf_url": oa.get("pdf_url"), "citations": w.get("cited_by_count"),
        "status": "new", "source": source, "area": potw.PILLARS[home].split("/")[0],
        "added_at": dt.datetime.now().isoformat(timespec="seconds"),
        "discovered_for": home, "discovered_note": note, "discovered_by": query,
    }


class LedgerIndex:
    """Find a ledger row by arXiv id, DOI or normalised title."""

    def __init__(self, rows):
        self.by = {}
        for r in rows:
            for k in self.keys(r):
                self.by.setdefault(k, r)

    @staticmethod
    def keys(r):
        out = [r["key"]]
        if r.get("arxiv"):
            out.append(f"arxiv:{re.sub(r'v\d+$', '', r['arxiv'])}")
        if r.get("doi"):
            out.append(f"doi:{r['doi'].lower()}")
        for t in (r.get("title"), r.get("arxiv_title")):
            if t and len(cg.norm_title(t).split()) >= 3:
                out.append(f"title:{cg.norm_title(t)}")
        return out

    def find(self, r):
        return next((self.by[k] for k in self.keys(r) if k in self.by), None)

    def add(self, r):
        for k in self.keys(r):
            self.by.setdefault(k, r)


def note_also(existing, home, note):
    """Record on an existing row that discovery for another home found it too (bridges)."""
    if existing.get("discovered_for") == home or existing.get("pillar") == home:
        return
    also = list(existing.get("also_found_for") or [])
    if home not in also:
        existing["also_found_for"] = also + [home]


# --- queries --------------------------------------------------------------------


def notes_for(home):
    folder = potw.PILLARS[home]
    notes = potw.home_notes(folder)
    rx = NOTE_FILTER.get(home)
    return [p for p in notes if not rx or rx.search(p.relative_to(REPO).as_posix())]


def headings(p):
    lines = p.read_text(encoding="utf-8").splitlines()
    out, fence = [], False
    for l in lines:
        if l.startswith("```"):
            fence = not fence
        elif not fence and re.match(r"#{1,3} ", l):
            out.append(l.strip())
    return out[:25]


def cmd_queries(args):
    claude = potw.find_claude()
    for home in args.home:
        path = DISCOVER / f"queries-{home}.json"
        if path.exists() and not args.force:
            log(f"queries: {path.relative_to(REPO)} exists; edit it, or pass --force to regenerate")
            continue
        notes = notes_for(home)
        sharers = [k for k, f in potw.PILLARS.items() if f == potw.PILLARS[home] and k != home]
        shared = (f"\nThis folder's notes are shared with `{', '.join(sharers)}`: write queries only for the "
                  f"parts of each note that fall in `{home}`'s scope, and an empty list for notes outside it.") if sharers else ""
        block = "\n\n".join(f"{p.relative_to(REPO)}\n" + "\n".join(f"  {h}" for h in headings(p)) for p in notes)
        prompt = QUERIES_PROMPT.format(home=home, scope=potw.HOMES[home][1], notes=block, shared=shared,
                                       audience=potw.AUDIENCE.get(home, potw.DEFAULT_AUDIENCE))
        out = subprocess.run([claude, "-p", "--model", potw.TRIAGE_MODEL], input=prompt,
                             capture_output=True, text=True, timeout=600, check=True).stdout
        m = re.search(r"\{.*\}", out, re.DOTALL)
        if not m:
            sys.exit(f"queries: no JSON object in the reply for {home}: {out[:300]!r}")
        got = json.loads(m.group(0))
        valid = {p.relative_to(REPO).as_posix() for p in notes}
        queries = {n: [q for q in qs if isinstance(q, str) and q.strip()] for n, qs in got.items() if n in valid}
        DISCOVER.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"home": home, "made": dt.date.today().isoformat(),
                                    "queries": queries}, indent=2, ensure_ascii=False) + "\n")
        log(f"queries: {sum(map(len, queries.values()))} queries for {len(queries)} notes -> {path.relative_to(REPO)}")


# --- search ---------------------------------------------------------------------


def cmd_search(args):
    rows = potw.load_ledger()
    index = LedgerIndex(rows)
    for home in args.home:
        path = DISCOVER / f"queries-{home}.json"
        if not path.exists():
            sys.exit(f"search: no {path.relative_to(REPO)}; run `discover.py queries --home {home}` first")
        queries = json.loads(path.read_text())["queries"]
        added = seen = 0
        try:
            for note, qs in queries.items():
                for q in qs:
                    data = cached_get({"search.semantic": q, "per-page": args.per_query * 3, "select": OA_FIELDS},
                                      semantic=True) or {}
                    kept = [w for w in data.get("results") or []
                            if w.get("title") and w.get("type") in KEEP_TYPES
                            and (w.get("cited_by_count") or 0) >= args.min_cites][: args.per_query]
                    for w in kept:
                        r = row_from_work(w, home, "openalex", note, q)
                        old = index.find(r)
                        if old:
                            seen += 1
                            note_also(old, home, note)
                            continue
                        rows.append(r)
                        index.add(r)
                        added += 1
        except BudgetSpent as e:
            log(f"search: OpenAlex budget spent ({e}); saved what was found, re-run later to resume")
            potw.save_ledger(rows)
            return
        potw.save_ledger(rows)
        log(f"search: {home}: {added} new rows, {seen} already in the ledger")


# --- curated --------------------------------------------------------------------


def resolve_title(title, year=None):
    """Best OpenAlex match for a title: exact normalised title first, else the most cited
    result whose title is a near match (see `near`). Tries a plain search within a year
    of `year`, then without the year (reprints such as MapReduce in CACM 2008), then a
    semantic search, which finds titles the keyword index splits badly."""
    want = cg.norm_title(title)

    def near(got):  # "XGBoost" for "XGBoost: A Scalable..."; never an empty or one-word fragment
        return got and (want in got or want.startswith(got + " ") or (got in want and len(got.split()) >= 2))

    def best(res):
        exact = [w for w in res if cg.norm_title(w.get("title")) == want]
        pool = exact or [w for w in res if near(cg.norm_title(w.get("title")))]
        return max(pool, key=lambda w: w.get("cited_by_count") or 0) if pool else None

    tries = [({"search": title, "per-page": 10, "select": OA_FIELDS}, False)]
    if year:
        tries[0][0]["filter"] = f"publication_year:{int(year) - 1}-{int(year) + 1}"
        tries.append(({"search": title, "per-page": 10, "select": OA_FIELDS}, False))
    tries.append(({"search.semantic": title, "per-page": 10, "select": OA_FIELDS}, True))
    for params, semantic in tries:
        w = best((cached_get(params, semantic=semantic) or {}).get("results") or [])
        if w:
            return w
    return None


def cmd_curated(args):
    rows = potw.load_ledger()
    index = LedgerIndex(rows)
    items = potw.read_jsonl(CURATED)
    added, missing = 0, []
    for it in items:
        if args.home and it["home"] not in args.home:
            continue
        try:
            w = resolve_title(it["title"], it.get("year"))
        except BudgetSpent as e:
            log(f"curated: OpenAlex budget spent ({e}); saved what was resolved, re-run later to resume")
            break
        if not w:
            missing.append(it)
            continue
        r = row_from_work(w, it["home"], "curated", it.get("note"))
        r["curated_role"] = it.get("role")
        old = index.find(r)
        if old:
            if not old.get("curated_role"):
                old["curated_role"] = it.get("role")
            note_also(old, it["home"], it.get("note"))
            continue
        rows.append(r)
        index.add(r)
        added += 1
    potw.save_ledger(rows)
    log(f"curated: {added} new rows, {len(items) - added - len(missing)} already in the ledger, {len(missing)} not found")
    for it in missing:
        print(f"  not found: [{it['home']}] {it['title']} ({it.get('year')})")


# --- review ---------------------------------------------------------------------


REVIEW_HEAD = ("| keep | role | title | year | cites | triage | graph | rel/int | key |\n"
               "|---|---|---|---|---|---|---|---|---|")


def cmd_review(args):
    if args.apply:
        return review_apply(args)
    rows = potw.load_ledger()
    for home in args.home:
        mine = [r for r in rows if r.get("pillar") == home and r["status"] in ("queued", "parked", "filed", "downloaded")
                and (r.get("discovered_for") or r["source"] in ("curated", "repo") or r["status"] == "filed")]
        by_note = {}
        for r in mine:
            by_note.setdefault(r.get("note") or "(no note yet)", []).append(r)
        out = [f"# Review — {home}", "",
               f"Generated {dt.date.today().isoformat()} by `discover.py review`. Mark **keep** `y` or `n` "
               "(blank leaves the row as it is) and correct **role** (`primary`, `secondary`, `docs`), then run "
               f"`python3 scripts/papers/discover.py review --home {home} --apply`. `n` marks the row skipped.",
               "", "**triage** is Haiku's guess, **graph** is the citation graph's role (blank until citegraph runs).", ""]
        for note in sorted(by_note):
            out += [f"## {note}", "", REVIEW_HEAD]
            for r in sorted(by_note[note], key=lambda r: (-(r.get("relevance") or 0), -(r.get("citations") or 0))):
                role = r.get("role_manual") or r.get("source_role") or r.get("curated_role") or ""
                title = (r.get("title") or "").replace("|", "/")
                out.append(f"|  | {role} | [{title}]({r.get('url') or ''}) | {r.get('year') or ''} | {r.get('citations') or ''} | "
                           f"{r.get('source_role') or ''} | {r.get('role') or ''} | {r.get('relevance')}/{r.get('interest')} | `{r['key']}` |")
            out.append("")
        path = DISCOVER / f"review-{home}.md"
        DISCOVER.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(out))
        log(f"review: {len(mine)} rows in {len(by_note)} notes -> {path.relative_to(REPO)}")


def review_apply(args):
    rows = potw.load_ledger()
    by_key = {r["key"]: r for r in rows}
    kept = dropped = roles = 0
    for home in args.home:
        path = DISCOVER / f"review-{home}.md"
        for line in path.read_text().splitlines():
            m = re.match(r"\|\s*([yYnN]?)\s*\|\s*(\w*)\s*\|.*\|\s*`([^`]+)`\s*\|$", line)
            if not m or m.group(3) not in by_key:
                continue
            mark, role, r = m.group(1).lower(), m.group(2), by_key[m.group(3)]
            if role in ("primary", "secondary", "docs") and role != (r.get("source_role") or r.get("curated_role")):
                r["role_manual"] = role
                roles += 1
            if mark == "n" and r["status"] not in potw.HELD_STATUSES:
                r.update(status="skipped", reason=f"dropped in review {dt.date.today().isoformat()}")
                dropped += 1
            elif mark == "y":
                r["reviewed_at"] = dt.date.today().isoformat()
                kept += 1
    potw.save_ledger(rows)
    log(f"review: {kept} kept, {dropped} dropped, {roles} roles corrected")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    homes = dict(nargs="+", choices=list(potw.HOMES), default=list(potw.SUBJECT_HOMES),
                 help="home keys (default: the subject homes)")
    p = sub.add_parser("queries")
    p.add_argument("--home", **homes)
    p.add_argument("--force", action="store_true", help="overwrite an existing queries file")
    p.set_defaults(fn=cmd_queries)
    p = sub.add_parser("search")
    p.add_argument("--home", **homes)
    p.add_argument("--per-query", type=int, default=6, help="works kept per query (default 6)")
    p.add_argument("--min-cites", type=int, default=25, help="drop works cited fewer times (default 25)")
    p.set_defaults(fn=cmd_search)
    p = sub.add_parser("curated")
    p.add_argument("--home", nargs="+", choices=list(potw.HOMES))
    p.set_defaults(fn=cmd_curated)
    p = sub.add_parser("review")
    p.add_argument("--home", **homes)
    p.add_argument("--apply", action="store_true", help="read keep/role marks back into the ledger")
    p.set_defaults(fn=cmd_review)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
