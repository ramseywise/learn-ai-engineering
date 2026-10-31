#!/usr/bin/env python3
"""Citation graph of the papers the course cites: what they cite, which venue reviewed them,
and which of them we already hold as PDFs.

  fetch     resolve seeds (papers cited in a home's notes, every PDF in its folder, and ledger rows
            read there) in OpenAlex,
            then fetch every work they reference
  dblp      peer-review status from DBLP (SPARQL): published venue for arXiv preprints
  intents   Semantic Scholar per-citation intents (methodology / background / result) and
            isInfluential; slow without S2_API_KEY, resumable
  status    print review status of the seeds; --write puts venue, review_status, role and
            local_citations in the ledger
  roots     what our papers cite most (local in-degree), RPYS peak years, origin candidates
  acquire   peer-reviewed works our papers cite but we don't hold, and whether a legal free copy
            exists; --queue adds them to the ledger, --download fetches the free ones (needs --home)
  preprints for those (and primary sources) with no free copy, find an arXiv preprint by title (OpenAlex often has only
            the proceedings record)
  primary   primary sources (cited by >=3 of our papers, >=2 for the method) across the corpus:
            reports/primary.md lists what to fetch by hand; --download fetches the free ones
  ingest    file the PDFs put in downloads/ into the right home (needs pypdf)
  refs      "Where the ideas come from" block for each references.md; --write puts it there
  upgrade   arXiv citations in notes that have a peer-reviewed version to cite instead
  exposure  notes ranked by the share of their citations that are preprint-only
  report    status + roots + acquire + upgrade + exposure as markdown in scripts/papers/reports/;
            --all writes one report per home plus reports/README.md
  export    GraphML of the graph; --html writes interactive pages reports/graph-<home>.html
  bridges   reports/bridges.md: readings that discovery found for both a subject home and an AI
            home, and works cited from both sides; where data-analytics, data-science,
            data-engineering and programming meet ai-engineering and generative-ai

Every command takes --home <key> (rag, loop, ...; see potw.HOMES) to work on one home;
default is every home, --subject limits it to the five subject homes (analytics,
classical-ml, data-systems, ml-systems, programming).

The subject homes hold few papers, so their graph is thin if seeded only from what we have
read. `fetch --include-queued` also seeds from queued rows; reports for homes fetched that
way say so in a banner, since the graph then reflects what we plan to read.

Graph: scripts/papers/citations.db (SQLite, gitignored, rebuilt from the APIs). Nodes are
OpenAlex works; `in_repo` is the repo path of our PDF when we hold one. An arXiv preprint and
its proceedings version are often two OpenAlex works: `canon` points both at one node.

review_status, decided in this order:
  peer-reviewed  DBLP has a conference or journal record (not CoRR), or OpenAlex has a
                 published version in a journal or conference
  workshop       that record's venue is a workshop
  book           OpenAlex type book / book-chapter
  tech-report    title says technical report / system card / model card
  preprint       none of the above
Corrections go in review_overrides.jsonl next to this script: {"id": "W...", "review_status": ..., "venue": ...}.

Keys: OPENALEX_API_KEY (keyless shares a 1,000-request daily budget per IP), S2_API_KEY.
"""
import argparse
import json
import os
import re
import sqlite3
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potw  # noqa: E402  ledger load/save, HOMES, log

REPO = potw.REPO
HERE = Path(__file__).resolve().parent
DB = HERE / "citations.db"
OVERRIDES = HERE / "review_overrides.jsonl"
REPORTS = HERE / "reports"
log = potw.log

OA_WORKS = "https://api.openalex.org/works"
OA_SELECT = ("id,doi,title,publication_year,type,ids,primary_location,locations,best_oa_location,"
             "cited_by_count,authorships,referenced_works")
DBLP_SPARQL = "https://sparql.dblp.org/sparql"
S2_REFS = ("https://api.semanticscholar.org/graph/v1/paper/{pid}/references"
           "?fields=title,year,externalIds,intents,isInfluential&limit=1000")
SEED_STATUSES = ("integrated", "filed", "downloaded")
# Venues that count as top tier, by DBLP short name prefix ("EMNLP (Findings)" matches EMNLP).
TOP_VENUES = ("NeurIPS", "ICML", "ICLR", "ACL", "EMNLP", "NAACL", "EACL", "COLING", "Trans. Assoc. Comput. Linguistics",
              "J. Mach. Learn. Res.", "Trans. Mach. Learn. Res.", "AAAI", "IJCAI", "KDD", "SIGIR", "WWW", "CIKM",
              "WSDM", "CVPR", "ICCV", "ECCV", "COLM", "AISTATS", "UAI", "USENIX Security", "SP", "CCS", "NDSS",
              "Nat.", "Science", "Nat. Mach. Intell.", "OSDI", "SOSP", "MLSys", "ISCA", "SC", "FSE", "ICSE")
TECH_REPORT = re.compile(r"technical report|tech report|system card|model card", re.I)
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")
ACL_ID = re.compile(r"\b(\d{4})[.-]([a-z]+(?:-[a-z]+)*)[.-](\d+)\b")  # 2021.findings-emnlp.320
ACM_ID = re.compile(r"^(\d{7})\.(\d{7})$")  # 3626772.3657834 -> 10.1145/...


# --- small helpers ------------------------------------------------------------


def norm_title(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


SUBJECT_ONLY = False  # set by --subject


def homes(key):
    if key:
        if key not in potw.HOMES:
            sys.exit(f"unknown home {key!r}; one of: {', '.join(potw.HOMES)}")
        return {key: potw.HOMES[key][0]}
    keys = potw.SUBJECT_HOMES if SUBJECT_ONLY else potw.HOMES
    return {k: potw.HOMES[k][0] for k in keys}


def is_ai_home(key):
    return potw.HOMES[key][0].startswith(("ai-engineering/", "generative-ai/"))


def get_json(url, headers=None, tries=6, pause=0.0, data=None):
    hdrs = {"User-Agent": potw.USER_AGENT, **(headers or {})}
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdrs), timeout=90) as r:
                data = json.load(r)
            time.sleep(pause)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                wait = min(90, 5 * 2 ** i)
                log(f"{e.code} from {url.split('?')[0]}; retry in {wait}s")
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep(5 * 2 ** i)
                continue
            raise


def oa_url(params):
    key = os.environ.get("OPENALEX_API_KEY")
    if key:
        params = {**params, "api_key": key}
    return f"{OA_WORKS}?{urllib.parse.urlencode(params)}"


def short(wid):
    return wid.rsplit("/", 1)[-1] if wid else wid


# --- database -----------------------------------------------------------------


SCHEMA = """
CREATE TABLE IF NOT EXISTS work(
  id TEXT PRIMARY KEY, canon TEXT, title TEXT, norm_title TEXT, year INT, type TEXT,
  doi TEXT, arxiv TEXT, source_name TEXT, source_type TEXT, published_in TEXT,
  cited_by INT, oa_pdf TEXT, refs_fetched INT DEFAULT 0,
  dblp_checked INT DEFAULT 0, dblp_venue TEXT, dblp_year INT, dblp_key TEXT, dblp_type TEXT,
  review_status TEXT, venue TEXT, top_venue INT, in_repo TEXT, s2_done INT DEFAULT 0,
  arxiv_checked INT DEFAULT 0);
CREATE TABLE IF NOT EXISTS author(work TEXT, position INT, name TEXT, openalex_id TEXT,
  PRIMARY KEY(work, position));
CREATE TABLE IF NOT EXISTS cites(src TEXT, dst TEXT, influential INT, intents TEXT,
  PRIMARY KEY(src, dst));
CREATE TABLE IF NOT EXISTS seed(ref TEXT PRIMARY KEY, kind TEXT, home TEXT, work TEXT,
  ledger_key TEXT, title TEXT);
CREATE TABLE IF NOT EXISTS seed_home(work TEXT, home TEXT, PRIMARY KEY(work, home));
CREATE TABLE IF NOT EXISTS note_cites(note TEXT, home TEXT, ref TEXT, PRIMARY KEY(note, ref));
CREATE TABLE IF NOT EXISTS provisional(home TEXT PRIMARY KEY, fetched TEXT);
CREATE INDEX IF NOT EXISTS cites_dst ON cites(dst);
CREATE INDEX IF NOT EXISTS work_norm ON work(norm_title);
CREATE INDEX IF NOT EXISTS work_arxiv ON work(arxiv);
CREATE INDEX IF NOT EXISTS work_doi ON work(doi);
"""


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    if "arxiv_checked" not in {r[1] for r in db.execute("PRAGMA table_info(work)")}:
        db.execute("ALTER TABLE work ADD COLUMN arxiv_checked INT DEFAULT 0")
    return db


def arxiv_of(w):
    doi = (w.get("doi") or "").lower()
    if "10.48550/arxiv." in doi:
        return doi.split("arxiv.", 1)[1]
    for loc in w.get("locations") or []:
        m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", (loc.get("landing_page_url") or "") + " "
                      + (loc.get("pdf_url") or ""))
        if m:
            return m.group(1)
    return None


def published_location(w):
    """Name of a journal/conference that published this work (not a repository), if any."""
    for loc in w.get("locations") or []:
        src = loc.get("source") or {}
        if src.get("type") in ("journal", "conference") and (loc.get("is_published") or loc.get("version") == "publishedVersion"):
            name = src.get("display_name") or ""
            if "arxiv" not in name.lower():
                return name
    return None


def store_work(db, w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    oa = (w.get("best_oa_location") or {}).get("pdf_url")
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
    db.execute("""INSERT INTO work(id, canon, title, norm_title, year, type, doi, arxiv, source_name, source_type,
                    published_in, cited_by, oa_pdf) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                  ON CONFLICT(id) DO UPDATE SET title=excluded.title, norm_title=excluded.norm_title,
                    year=excluded.year, type=excluded.type, doi=excluded.doi, arxiv=excluded.arxiv,
                    source_name=excluded.source_name, source_type=excluded.source_type,
                    published_in=excluded.published_in, cited_by=excluded.cited_by, oa_pdf=excluded.oa_pdf""",
               (short(w["id"]), short(w["id"]), w.get("title"), norm_title(w.get("title")), w.get("publication_year"),
                w.get("type"), doi, arxiv_of(w), src.get("display_name"), src.get("type"), published_location(w),
                w.get("cited_by_count"), oa))
    db.execute("DELETE FROM author WHERE work=?", (short(w["id"]),))
    for i, a in enumerate((w.get("authorships") or [])[:20]):
        au = a.get("author") or {}
        db.execute("INSERT OR REPLACE INTO author VALUES (?,?,?,?)",
                   (short(w["id"]), i, au.get("display_name"), short(au.get("id"))))


def store_refs(db, w):
    for ref in w.get("referenced_works") or []:
        db.execute("INSERT OR IGNORE INTO cites(src, dst) VALUES (?,?)", (short(w["id"]), short(ref)))
    db.execute("UPDATE work SET refs_fetched=1 WHERE id=?", (short(w["id"]),))


# --- seeds ----------------------------------------------------------------------


def refs_in_text(text):
    """(kind, ref) for every arXiv id, DOI and ACL Anthology id linked in markdown."""
    out = set()
    for m in re.finditer(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", text):
        out.add(("arxiv", m.group(1)))
    for m in re.finditer(r"doi\.org/(10\.\d{4,9}/[^\s)\]>\"'`]+)", text):
        out.add(("doi", m.group(1).rstrip(".,;").lower()))
    for m in re.finditer(r"aclanthology\.org/([0-9A-Za-z][\w.\-]+?)(?:\.pdf)?/?[\s)\]>]", text):
        aid = m.group(1)
        if ACL_ID.fullmatch(aid) or re.fullmatch(r"[A-Z]\d{2}-\d{4}", aid):
            out.add(("doi", f"10.18653/v1/{aid}".lower()))
    return out


def ref_from_pdf(path):
    """arXiv id or DOI recoverable from a PDF's filename."""
    stem = Path(path).stem
    if m := re.fullmatch(r"(\d{4}\.\d{4,5})(v\d+)?", stem):
        return ("arxiv", m.group(1))
    if m := ACL_ID.fullmatch(stem):
        return ("doi", f"10.18653/v1/{m.group(1)}.{m.group(2)}.{m.group(3)}")
    if m := ACM_ID.fullmatch(stem):
        return ("doi", f"10.1145/{m.group(1)}.{m.group(2)}")
    return None


def collect_seeds(db, hs, rows, include_queued=False):
    """Fill seed + note_cites: papers linked from each home's markdown, plus ledger rows read there
    (and, with include_queued, rows queued for it)."""
    statuses = SEED_STATUSES + (("queued",) if include_queued else ())
    for key, folder in hs.items():
        sharers = {k for k, v in potw.HOMES.items() if v[0] == folder and k != key}
        for md in sorted((REPO / folder).rglob("*.md")):
            rel = md.relative_to(REPO).as_posix()
            if "/sources/" in rel or "/slides/" in rel:
                continue
            for kind, ref in refs_in_text(md.read_text(encoding="utf-8", errors="ignore")):
                db.execute("INSERT OR IGNORE INTO seed(ref, kind, home) VALUES (?,?,?)", (ref, kind, key))
                db.execute("INSERT OR IGNORE INTO note_cites VALUES (?,?,?)", (rel, key, ref))
        for r in rows:
            pdf = r.get("local_pdf") if isinstance(r.get("local_pdf"), str) else None
            in_folder = (bool(pdf) and pdf.startswith(folder + "/") and r["status"] != "skipped"
                         and r.get("pillar") not in sharers)  # data-engineering holds two homes
            if not in_folder and (r.get("pillar") != key or r["status"] not in statuses):
                continue
            got = (("arxiv", r["arxiv"]) if r.get("arxiv") else ("doi", r["doi"].lower()) if r.get("doi")
                   else ref_from_pdf(pdf) if pdf else None)
            if got:
                db.execute("INSERT OR IGNORE INTO seed(ref, kind, home) VALUES (?,?,?)", (got[1], got[0], key))
                db.execute("UPDATE seed SET ledger_key=? WHERE ref=?", (r["key"], got[1]))
            elif pdf and Path(pdf).parent.name == "sources" and good_title(r.get("title")):
                # a paper with no id in its name: look it up by title (book chapters live in subfolders)
                db.execute("INSERT OR IGNORE INTO seed(ref, kind, home, ledger_key, title) VALUES (?,?,?,?,?)",
                           (f"title:{norm_title(r['title'])}", "title", key, r["key"], r["title"]))
    db.commit()


def good_title(t):
    return bool(t) and len(t.split()) >= 4 and not re.search(r"\d{4}\.\d{4,5}|ebook|edited|^chapter", t, re.I)


# --- fetch ----------------------------------------------------------------------


def oa_batch(field, values):
    out = []
    for i in range(0, len(values), 50):
        chunk = values[i:i + 50]
        data = get_json(oa_url({"filter": f"{field}:{'|'.join(chunk)}", "select": OA_SELECT, "per-page": 100}),
                        pause=0.2)
        out.extend((data or {}).get("results") or [])
    return out


def resolve_seeds(db):
    todo = db.execute("SELECT ref, kind, title FROM seed WHERE work IS NULL").fetchall()
    arx = [r["ref"] for r in todo if r["kind"] == "arxiv"]
    dois = [r["ref"] for r in todo if r["kind"] == "doi"]
    log(f"resolve: {len(arx)} arXiv ids, {len(dois)} DOIs, {len(todo) - len(arx) - len(dois)} titles")
    for w in oa_batch("doi", [f"10.48550/arxiv.{a}" for a in arx] + dois):
        store_work(db, w)
        store_refs(db, w)
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        ref = doi.split("arxiv.", 1)[1] if "10.48550/arxiv." in doi else doi
        db.execute("UPDATE seed SET work=? WHERE ref=?", (short(w["id"]), ref))
        if a := arxiv_of(w):  # an arXiv DOI that OpenAlex merged into the published work
            db.execute("UPDATE seed SET work=? WHERE ref=? AND work IS NULL", (short(w["id"]), a))
    db.commit()
    # leftovers (OpenAlex filed the arXiv version under the published DOI, or no id): search by title
    left = db.execute("SELECT ref, kind, title FROM seed WHERE work IS NULL").fetchall()
    titles = {r["ref"]: r["title"] for r in left if r["title"]}
    if arx_left := [r["ref"] for r in left if r["kind"] == "arxiv"]:
        for aid, meta in potw.arxiv_batch_meta(arx_left).items():
            titles[aid] = meta[0]
    for ref, title in titles.items():
        if not title:
            continue
        data = get_json(oa_url({"search": title[:200], "select": OA_SELECT, "per-page": 5}), pause=0.2) or {}
        hit = next((w for w in data.get("results") or [] if norm_title(w.get("title")) == norm_title(title)), None)
        if hit:
            store_work(db, hit)
            store_refs(db, hit)
            db.execute("UPDATE seed SET work=? WHERE ref=?", (short(hit["id"]), ref))
    db.commit()
    miss = db.execute("SELECT ref FROM seed WHERE work IS NULL").fetchall()
    if miss:
        log(f"resolve: {len(miss)} seeds not in OpenAlex: {', '.join(r['ref'] for r in miss[:15])}")
    db.execute("INSERT OR IGNORE INTO seed_home SELECT work, home FROM seed WHERE work IS NOT NULL")
    db.commit()


def fetch_refs(db):
    # works referenced by seeds that we don't have metadata for yet
    missing = [r[0] for r in db.execute(
        "SELECT DISTINCT dst FROM cites WHERE dst NOT IN (SELECT id FROM work)").fetchall()]
    log(f"fetch: metadata for {len(missing)} referenced works")
    for i in range(0, len(missing), 50):
        for w in oa_batch("openalex", missing[i:i + 50]):
            store_work(db, w)
        db.commit()
        if i and i % 1000 == 0:
            log(f"fetch: {i}/{len(missing)}")


def link_canon(db):
    """Point preprint and published copies of one paper (same title, years within 2) at one node,
    preferring the copy that has a published venue, then the one with references."""
    db.execute("UPDATE work SET canon=id")
    groups = defaultdict(list)
    for r in db.execute("SELECT id, norm_title, year, published_in, refs_fetched, cited_by FROM work "
                        "WHERE length(norm_title) > 25"):
        groups[r["norm_title"]].append(r)
    for rs in groups.values():
        if len(rs) < 2:
            continue
        best = max(rs, key=lambda r: (bool(r["published_in"]), r["refs_fetched"], r["cited_by"] or 0))
        for r in rs:
            if r["id"] != best["id"] and abs((r["year"] or 0) - (best["year"] or 0)) <= 2:
                db.execute("UPDATE work SET canon=? WHERE id=?", (best["id"], r["id"]))
    db.commit()


def repo_index(rows):
    """Lookups from arXiv id / DOI / title to the repo path of a PDF we hold."""
    by = {"arxiv": {}, "doi": {}, "title": {}}
    for r in rows:
        paths = [p for p in ([r.get("local_pdf")] + list(r.get("copies") or [])) if isinstance(p, str)]
        paths = [p for p in paths if (REPO / p).exists()]
        if not paths:
            continue
        p = paths[0]
        if r.get("arxiv"):
            by["arxiv"].setdefault(r["arxiv"], p)
        for q in paths:
            if got := ref_from_pdf(q):
                by[got[0]].setdefault(got[1], p)
        for t in (r.get("arxiv_title"), r.get("title")):
            if good_title(t):
                by["title"].setdefault(norm_title(t), p)
    return by


def mark_in_repo(db, rows):
    idx = repo_index(rows)
    db.execute("UPDATE work SET in_repo=NULL")
    n = 0
    for w in db.execute("SELECT id, arxiv, doi, norm_title FROM work").fetchall():
        p = (idx["arxiv"].get(w["arxiv"]) or idx["doi"].get(w["doi"] or "")
             or (idx["title"].get(w["norm_title"]) if len(w["norm_title"] or "") > 25 else None))
        if p:
            db.execute("UPDATE work SET in_repo=? WHERE id=?", (p, w["id"]))
            n += 1
    # a PDF of either copy counts for the canonical node
    db.execute("""UPDATE work SET in_repo=(SELECT o.in_repo FROM work o WHERE o.canon=work.id AND o.in_repo IS NOT NULL)
                  WHERE in_repo IS NULL AND id IN (SELECT canon FROM work WHERE in_repo IS NOT NULL)""")
    db.commit()
    log(f"in_repo: {n} works matched to a PDF in the repo")


def cmd_fetch(args):
    db = connect()
    rows = potw.load_ledger()
    hs = homes(args.home)
    collect_seeds(db, hs, rows, args.include_queued)
    for key in hs:
        if args.include_queued:
            db.execute("INSERT OR REPLACE INTO provisional VALUES (?,?)", (key, time.strftime("%Y-%m-%d")))
        else:
            db.execute("DELETE FROM provisional WHERE home=?", (key,))
    db.commit()
    resolve_seeds(db)
    fetch_refs(db)
    link_canon(db)
    mark_in_repo(db, rows)
    classify(db)
    n = db.execute("SELECT count(*) FROM seed_home").fetchone()[0]
    e = db.execute("SELECT count(*) FROM cites").fetchone()[0]
    log(f"fetch: {n} seed works, {e} citation edges, "
        f"{db.execute('SELECT count(*) FROM work').fetchone()[0]} works")


# --- review status ------------------------------------------------------------


def sparql_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dblp_query(items):
    """items: (work id, doi or None, title). Returns {work id: [(key, venue, year, type)]}."""
    dois, titles = [], []
    for wid, doi, title in items:
        if doi and not re.search(r'[\s<>"{}|\\^`]', doi):  # skip DOIs that aren't valid IRIs
            for d in {doi, doi.upper(), doi.lower()}:
                dois.append(f"({sparql_str(wid)} <https://doi.org/{d}>)")
        if title:
            t = " ".join(title.split()).rstrip(".")  # newlines and tabs break the SPARQL literal
            titles += [f"({sparql_str(wid)} {sparql_str(t + '.')})", f"({sparql_str(wid)} {sparql_str(t)})"]
    q = f"""PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?wid ?pub ?venue ?year ?type WHERE {{
  {{ VALUES (?wid ?doi) {{ {' '.join(dois) or '("x" <https://doi.org/x>)'} }}
     ?c dblp:doi ?doi ; dblp:title ?t . ?pub dblp:title ?t . }}
  UNION
  {{ VALUES (?wid ?t) {{ {' '.join(titles)} }} ?pub dblp:title ?t . }}
  ?pub dblp:yearOfPublication ?year ; a ?type .
  OPTIONAL {{ ?pub dblp:publishedIn ?venue }}
  FILTER(?type IN (dblp:Inproceedings, dblp:Article, dblp:Book, dblp:Incollection))
}}"""
    return dblp_post(q)


def dblp_fuzzy(items):
    """Second pass: titles compared lowercased with punctuation removed, which catches casing
    ("Attention is All you Need") and hyphen differences, plus the title without a "Name:"
    prefix (REALM's ICML title drops it). Scans every DBLP title, so ~30s a query."""
    pairs = []
    for wid, title in items:
        for t in {title, title.split(":", 1)[1] if ":" in title else ""}:
            nt = re.sub(r"[^a-z0-9]", "", norm_title(t))
            if len(nt) >= 20:
                pairs.append(f"({sparql_str(wid)} {sparql_str(nt)})")
    if not pairs:
        return {}
    q = f"""PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?wid ?pub ?venue ?year ?type WHERE {{
  {{ ?pub dblp:title ?t . BIND(REPLACE(LCASE(?t), "[^a-z0-9]", "") AS ?nt) }}
  VALUES (?wid ?nt) {{ {' '.join(pairs)} }}
  ?pub dblp:yearOfPublication ?year ; a ?type .
  OPTIONAL {{ ?pub dblp:publishedIn ?venue }}
  FILTER(?type IN (dblp:Inproceedings, dblp:Article, dblp:Book, dblp:Incollection))
}}"""
    return dblp_post(q)


def dblp_safe(fn, items, key):
    """Run a DBLP batch; if the endpoint rejects it (400), retry paper by paper and skip the one
    it rejects, so one odd title doesn't stop the run."""
    try:
        return fn(items)
    except urllib.error.HTTPError as exc:
        if exc.code != 400:
            raise
    hits = defaultdict(list)
    groups = defaultdict(list)
    for it in items:
        groups[key(it)].append(it)
    for wid, its in groups.items():
        try:
            for k, v in fn(its).items():
                hits[k] += v
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                raise
            log(f"dblp: {wid} rejected by DBLP (400); skipped")
    return hits


def dblp_post(q):
    # POST: a batch of titles is too long for a GET URL
    data = get_json(DBLP_SPARQL, headers={"Accept": "application/sparql-results+json",
                                          "Content-Type": "application/x-www-form-urlencoded"},
                    pause=1.0, data=urllib.parse.urlencode({"query": q}).encode()) or {}
    out = defaultdict(list)
    for b in data.get("results", {}).get("bindings", []):
        v = {k: x["value"] for k, x in b.items()}
        if (v.get("venue") or "") == "CoRR":
            continue
        out[v["wid"]].append((v["pub"].replace("https://dblp.org/rec/", ""), v.get("venue"),
                              int(v["year"]), v["type"].rsplit("#", 1)[-1]))
    return out


def pick_dblp(recs, year):
    """Best DBLP record for a work: a conference or journal paper published from a year before
    to three years after the work's own year (the same title years apart is another paper)."""
    recs = [r for r in recs if not year or year - 1 <= r[2] <= year + 3]
    recs.sort(key=lambda r: (r[3] not in ("Inproceedings", "Article"), r[2]))
    return recs[0] if recs else None


def save_dblp(db, wid, rec, checked):
    rec = rec or (None, None, None, None)
    db.execute("UPDATE work SET dblp_checked=?, dblp_key=?, dblp_venue=?, dblp_year=?, dblp_type=? WHERE id=?",
               (checked, rec[0], rec[1], rec[2], rec[3], wid))


def cmd_dblp(args):
    db = connect()
    scope = ""
    if args.home:
        # the home's seeds and everything they cite
        scope = """ AND id IN (SELECT work FROM seed_home WHERE home=:h
                      UNION SELECT w.canon FROM cites c JOIN work w ON w.id=c.dst
                      WHERE c.src IN (SELECT work FROM seed_home WHERE home=:h))"""
    base = "id=canon AND title IS NOT NULL" + scope
    todo = db.execute(f"SELECT id, title, year FROM work WHERE dblp_checked=0 AND {base}", {"h": args.home}).fetchall()
    log(f"dblp: {len(todo)} works to check by DOI and exact title")
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        items = []
        for w in chunk:
            # every DOI we know for the paper, from its preprint and published copies
            for d in db.execute("SELECT doi, arxiv FROM work WHERE canon=?", (w["id"],)).fetchall():
                items.append((w["id"], d["doi"] or (f"10.48550/arxiv.{d['arxiv']}" if d["arxiv"] else None), None))
            items.append((w["id"], None, w["title"]))
        hits = dblp_safe(dblp_query, items, key=lambda it: it[0])
        for w in chunk:
            save_dblp(db, w["id"], pick_dblp(hits.get(w["id"], []), w["year"]), 1)
        db.commit()
        if i % 400 == 0:
            log(f"dblp: {i + len(chunk)}/{len(todo)}")
    # second pass for works no exact match placed at a venue
    todo = db.execute(f"SELECT id, title, year FROM work WHERE dblp_checked=1 AND dblp_key IS NULL AND {base}",
                      {"h": args.home}).fetchall()
    log(f"dblp: {len(todo)} works to retry with loose title matching (~30s per 100)")
    for i in range(0, len(todo), 100):
        chunk = todo[i:i + 100]
        hits = dblp_safe(dblp_fuzzy, [(w["id"], " ".join(w["title"].split())) for w in chunk], key=lambda it: it[0])
        for w in chunk:
            save_dblp(db, w["id"], pick_dblp(hits.get(w["id"], []), w["year"]), 2)
        db.commit()
        log(f"dblp: loose {i + len(chunk)}/{len(todo)}")
    classify(db)


def classify(db):
    overrides = {o["id"]: o for o in potw.read_jsonl(OVERRIDES)}
    rows = db.execute("SELECT * FROM work WHERE id=canon").fetchall()
    for w in rows:
        # published copies of the same paper count too
        pub = db.execute("SELECT published_in FROM work WHERE canon=? AND published_in IS NOT NULL", (w["id"],)).fetchone()
        venue, status = None, "preprint"
        if w["dblp_venue"] and w["dblp_type"] in ("Inproceedings", "Article", "Incollection"):
            venue, status = f"{w['dblp_venue']} {w['dblp_year']}", "peer-reviewed"
            if re.search(r"workshop|@", w["dblp_venue"], re.I):
                status = "workshop"
        elif pub:
            venue, status = pub[0], "peer-reviewed"
            if re.search(r"workshop", pub[0], re.I):
                status = "workshop"
        elif w["type"] in ("book", "book-chapter") or w["dblp_type"] == "Book":
            status = "book"
        elif TECH_REPORT.search(w["title"] or ""):
            status = "tech-report"
        if o := overrides.get(w["id"]):
            status, venue = o.get("review_status", status), o.get("venue", venue)
        top = int(bool(venue) and status == "peer-reviewed" and venue.startswith(TOP_VENUES))
        db.execute("UPDATE work SET review_status=?, venue=?, top_venue=? WHERE canon=?", (status, venue, top, w["id"]))
    db.commit()


# --- Semantic Scholar intents -------------------------------------------------


def cmd_intents(args):
    db = connect()
    key = os.environ.get("S2_API_KEY")
    hdr = {"x-api-key": key} if key else {}
    q = "SELECT w.id, w.arxiv, w.doi FROM work w JOIN seed_home s ON s.work=w.id WHERE w.s2_done=0"
    todo = db.execute(q + (" AND s.home=?" if args.home else ""), (args.home,) if args.home else ()).fetchall()
    log(f"intents: {len(todo)} seeds{'' if key else ' (no S2_API_KEY: slow, 429s expected)'}")
    by_arxiv = {r["arxiv"]: r["canon"] for r in db.execute("SELECT arxiv, canon FROM work WHERE arxiv IS NOT NULL")}
    by_doi = {r["doi"]: r["canon"] for r in db.execute("SELECT doi, canon FROM work WHERE doi IS NOT NULL")}
    by_title = {r["norm_title"]: r["canon"] for r in db.execute("SELECT norm_title, canon FROM work WHERE length(norm_title) > 25")}
    for n, w in enumerate(todo, 1):
        pid = f"arXiv:{w['arxiv']}" if w["arxiv"] else f"DOI:{w['doi']}" if w["doi"] else None
        if not pid:
            continue
        try:
            data = get_json(S2_REFS.format(pid=pid), headers=hdr, tries=8, pause=0.0 if key else 1.5)
        except urllib.error.HTTPError as e:
            log(f"intents: {pid} gave {e.code}; stopping, rerun to resume")
            break
        matched = 0
        for item in (data or {}).get("data") or []:
            p = item.get("citedPaper") or {}
            ext = p.get("externalIds") or {}
            dst = (by_arxiv.get(ext.get("ArXiv")) or by_doi.get((ext.get("DOI") or "").lower())
                   or by_title.get(norm_title(p.get("title"))))
            if not dst:
                continue
            matched += 1
            # the edge may point at either copy of the cited paper
            ids = [r[0] for r in db.execute("SELECT id FROM work WHERE canon=?", (dst,))]
            hit = db.execute(f"UPDATE cites SET influential=?, intents=? WHERE src=? AND dst IN ({','.join('?' * len(ids))})",
                             (int(bool(item.get("isInfluential"))), ",".join(item.get("intents") or []), w["id"], *ids))
            if hit.rowcount == 0:  # S2 knows a reference OpenAlex missed
                db.execute("INSERT OR IGNORE INTO cites VALUES (?,?,?,?)",
                           (w["id"], dst, int(bool(item.get("isInfluential"))), ",".join(item.get("intents") or [])))
        db.execute("UPDATE work SET s2_done=1 WHERE id=?", (w["id"],))
        db.commit()
        if n % 10 == 0:
            log(f"intents: {n}/{len(todo)} (last {pid}: {matched} references matched)")


# --- analysis -------------------------------------------------------------------


def seed_ids(db, home):
    q = "SELECT DISTINCT w.canon FROM seed_home s JOIN work w ON w.id=s.work"
    return {r[0] for r in db.execute(q + (" WHERE s.home=?" if home else ""), (home,) if home else ())}


def in_degree(db, seeds):
    """canon id -> (seeds citing it, seeds citing it for methodology, seeds citing it influentially)."""
    src_canon = {r[0]: r[1] for r in db.execute("SELECT id, canon FROM work")}
    deg, meth, infl = defaultdict(set), defaultdict(set), defaultdict(set)
    for c in db.execute("SELECT c.src, w.canon, c.intents, c.influential FROM cites c JOIN work w ON w.id=c.dst"):
        s = src_canon.get(c[0], c[0])
        if s not in seeds or s == c[1]:
            continue
        deg[c[1]].add(s)
        if c[2] and "methodology" in c[2]:
            meth[c[1]].add(s)
        if c[3]:
            infl[c[1]].add(s)
    return deg, meth, infl


def works(db, ids):
    if not ids:
        return {}
    ids = list(ids)
    out = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        for r in db.execute(f"SELECT * FROM work WHERE id IN ({','.join('?' * len(chunk))})", chunk):
            out[r["id"]] = r
    return out


def first_author(db, wid):
    r = db.execute("SELECT a.name FROM author a JOIN work w ON w.id=a.work WHERE w.canon=? ORDER BY a.position LIMIT 1",
                   (wid,)).fetchone()
    if not r or not r[0]:
        return "?"
    name = r[0].strip()
    return name.split(",")[0].strip() if "," in name else name.split()[-1]  # "Wei, Jason" or "Jason Wei"


def cite_label(db, w):
    return f"{first_author(db, w['id'])} {w['year'] or '?'}, {(w['title'] or '')[:70]}"


def link(w):
    if w["arxiv"]:
        return f"https://arxiv.org/abs/{w['arxiv']}"
    if w["doi"]:
        return f"https://doi.org/{w['doi']}"
    return f"https://openalex.org/{w['id']}"


def flag(w):
    return f"✓ `{w['in_repo']}`" if w["in_repo"] else "—"


def rpys(db, deg):
    """Reference Publication Year Spectroscopy: years where cited references spike above the
    5-year median of their neighbours (Marx et al., 2014). Weighted by local in-degree."""
    ws = works(db, deg)
    by_year = Counter()
    for wid, s in deg.items():
        if ws.get(wid) and ws[wid]["year"]:
            by_year[ws[wid]["year"]] += len(s)
    if not by_year:
        return []
    peaks = []
    for y in range(min(by_year), max(by_year) + 1):
        window = [by_year.get(x, 0) for x in range(y - 2, y + 3)]
        dev = by_year.get(y, 0) - statistics.median(window)
        if dev > 0 and y < max(by_year) - 2:  # the last years always look like peaks
            top = max((w for w in deg if ws.get(w) and ws[w]["year"] == y), key=lambda w: len(deg[w]))
            peaks.append((y, dev, top))
    return sorted(peaks, key=lambda p: -p[1])[:8]


def roots_md(db, home, n):
    seeds = seed_ids(db, home)
    deg, meth, infl = in_degree(db, seeds)
    ws = works(db, deg)
    has_intents = any(meth.values())
    rows = sorted(deg, key=lambda w: (-len(deg[w]), -len(meth.get(w, ())), ws[w]["year"] or 9999))[:n]
    out = [f"### Most cited by our {len(seeds)} papers\n",
           "Local = how many of our papers cite it. "
           + ("Meth. = cited for methodology (Semantic Scholar intents). " if has_intents else
              "Run `citegraph.py intents` to add methodology counts. ")
           + "In repo = our PDF.\n",
           "| Local | " + ("Meth. | " if has_intents else "") + "Paper | Status | Venue | Global cites | In repo |",
           "|---|" + ("---|" if has_intents else "") + "---|---|---|---|---|"]
    for w in rows:
        x = ws[w]
        out.append(f"| {len(deg[w])} | " + (f"{len(meth.get(w, ()))} | " if has_intents else "")
                   + f"[{cite_label(db, x)}]({link(x)}) | {x['review_status']} | {x['venue'] or ''} | "
                   f"{x['cited_by'] or ''} | {flag(x)} |")
    peaks = rpys(db, deg)
    if peaks:
        out += ["\n### Historical roots (RPYS peak years)\n",
                "Years whose cited references spike above their neighbours; the most cited paper of each.\n",
                "| Year | Excess | Paper | Status | In repo |", "|---|---|---|---|---|"]
        pw = works(db, [p[2] for p in peaks])
        for y, dev, top in sorted(peaks):
            x = pw[top]
            out.append(f"| {y} | +{dev:g} | [{cite_label(db, x)}]({link(x)}) | {x['review_status']} | {flag(x)} |")
    # origin candidates: early, widely cited inside the corpus, peer-reviewed or classic
    cutoff = statistics.median([ws[w]["year"] for w in deg if ws[w]["year"]] or [0])
    cand = [w for w in deg if len(deg[w]) >= 3 and (ws[w]["year"] or 9999) < cutoff]
    cand.sort(key=lambda w: (-(len(meth.get(w, ())) if has_intents else len(deg[w])), ws[w]["year"] or 9999))
    if cand:
        out += [f"\n### Origin candidates\n",
                f"Cited by ≥3 of our papers and older than the median cited year ({cutoff:g}). "
                "The metric proposes; reading confirms.\n",
                "| Local | " + ("Meth. | " if has_intents else "") + "Paper | Status | Venue | In repo |",
                "|---|" + ("---|" if has_intents else "") + "---|---|---|---|"]
        for w in cand[:20]:
            x = ws[w]
            out.append(f"| {len(deg[w])} | " + (f"{len(meth.get(w, ()))} | " if has_intents else "")
                       + f"[{cite_label(db, x)}]({link(x)}) | {x['review_status']} | {x['venue'] or ''} | {flag(x)} |")
    return "\n".join(out)


def acquire_list(db, home, min_deg):
    seeds = seed_ids(db, home)
    deg, meth, _ = in_degree(db, seeds)
    ws = works(db, deg)
    picks = [w for w in deg if len(deg[w]) >= min_deg and ws[w]["review_status"] == "peer-reviewed"
             and not ws[w]["in_repo"] and w not in seeds]
    picks.sort(key=lambda w: (-len(deg[w]), -(ws[w]["cited_by"] or 0)))
    return [(ws[w], len(deg[w])) for w in picks]


OA_HOSTS = (("aclanthology.org", "ACL Anthology"), ("aclweb.org", "ACL Anthology"), ("mlr.press", "PMLR"),
            ("neurips.cc", "NeurIPS proceedings"), ("nips.cc", "NeurIPS proceedings"), ("openreview.net", "OpenReview"),
            ("jmlr.org", "JMLR"), ("direct.mit.edu", "MIT Press (open access)"), ("arxiv.org", "arXiv"),
            ("aaai.org", "AAAI (open access)"), ("ijcai.org", "IJCAI (open access)"), ("thecvf.com", "CVF open access"),
            ("usenix.org", "USENIX (open access)"), ("dl.acm.org", "ACM (open access)"))


def availability(w):
    """(how to get it, PDF URL or None). A free published copy beats the arXiv preprint; a
    paywalled paper with an arXiv version is still free to read (cite the venue)."""
    if w["oa_pdf"]:
        host = urllib.parse.urlparse(w["oa_pdf"]).netloc
        label = next((name for h, name in OA_HOSTS if h in host), f"free ({host})")
        if label == "arXiv" or label.startswith("free"):
            label = label if label == "arXiv" else f"free copy ({host})"
        return f"✓ {label}", w["oa_pdf"]
    doi = (w["doi"] or "").lower()
    if doi.startswith("10.18653/v1/"):  # every ACL Anthology paper is open access
        return "✓ ACL Anthology", f"https://aclanthology.org/{doi.split('/', 2)[2]}.pdf"
    if w["arxiv"]:
        return "✓ arXiv preprint", f"https://arxiv.org/pdf/{w['arxiv']}"
    if doi.startswith("10.1162/tacl"):  # TACL is open access; the DOI lands on the free MIT Press page
        return "✓ TACL (open access)", f"https://doi.org/{doi}"
    if w["doi"]:
        return "✗ no free copy found (paywalled: library, author page or request)", None
    return "✗ no free copy found", None


ARXIV_SEARCH = "https://export.arxiv.org/api/query?search_query={q}&max_results=5"
ATOM = "{http://www.w3.org/2005/Atom}"


def cmd_preprints(args):
    """OpenAlex often holds only the proceedings record of a paper that also has an arXiv preprint
    (MMLU, SuperGLUE). For papers on a reading list with no free copy, search arXiv by title and
    store the id, so availability() can point at the free preprint."""
    import xml.etree.ElementTree as ET
    db = connect()
    todo = {}
    for key in homes(args.home):
        for w, _ in acquire_list(db, key, args.min):
            if not w["arxiv_checked"] and availability(w)[0].startswith("✗"):
                todo[w["id"]] = w
    for w, _, _, _ in ([] if args.home else primary_list(db)):
        if not w["arxiv_checked"] and not w["in_repo"] and availability(w)[0].startswith("✗"):
            todo[w["id"]] = w
    log(f"preprints: {len(todo)} reading-list papers with no free copy; searching arXiv by title")
    found = 0
    for w in todo.values():
        words = " ".join(norm_title(w["title"]).split()[:12])
        url = ARXIV_SEARCH.format(q=urllib.parse.quote(f'ti:"{words}"'))
        try:
            feed = ET.fromstring(potw.http_get(url, timeout=60))
        except Exception as exc:
            log(f"preprints: {w['id']} failed: {exc}")
            continue
        hit = None
        for e in feed.iter(f"{ATOM}entry"):
            year = int(e.findtext(f"{ATOM}published", "0000")[:4])
            if norm_title(e.findtext(f"{ATOM}title", "")) == w["norm_title"] and \
                    (not w["year"] or w["year"] - 3 <= year <= w["year"] + 1):
                hit = re.sub(r"v\d+$", "", e.findtext(f"{ATOM}id", "").rsplit("/abs/", 1)[-1])
                break
        db.execute("UPDATE work SET arxiv=COALESCE(arxiv, ?), arxiv_checked=1 WHERE id=?", (hit, w["id"]))
        db.commit()
        found += bool(hit)
        log(f"preprints: {w['title'][:60]} -> {hit or 'none'}")
        time.sleep(3)  # arXiv asks for one request every 3 seconds
    log(f"preprints: {found} of {len(todo)} have an arXiv copy")


def acquire_md(db, home, min_deg):
    picks = acquire_list(db, home, min_deg)
    out = [f"### Peer-reviewed papers to acquire ({len(picks)})\n",
           f"Peer-reviewed, cited by ≥{min_deg} of our papers, no PDF in the repo. "
           "**Get it** says whether a legal free copy exists (OpenAlex/Unpaywall open-access data, "
           "then arXiv). `acquire --download` fetches the free ones into this home's sources/; "
           "`acquire --queue` only adds them to the ledger.\n"]
    got = Counter(availability(w)[0].startswith("✓") for w, _ in picks)
    out.append(f"{got[True]} can be fetched free, {got[False]} have no free copy.\n")
    out += ["| Local | Paper | Venue | Get it |", "|---|---|---|---|"]
    for w, d in picks:
        how, url = availability(w)
        out.append(f"| {d} | [{cite_label(db, w)}]({link(w)}) | {w['venue']} | "
                   + (f"[{how}]({url})" if url else how) + " |")
    return "\n".join(out)


def upgrade_md(db, home):
    q = """SELECT n.note, n.ref, w.canon FROM note_cites n JOIN seed s ON s.ref=n.ref
           JOIN work w ON w.id=s.work WHERE s.kind='arxiv'""" + (" AND n.home=?" if home else "")
    hits = db.execute(q, (home,) if home else ()).fetchall()
    ws = works(db, {h["canon"] for h in hits})
    rows = [(h["note"], h["ref"], ws[h["canon"]]) for h in hits if ws[h["canon"]]["review_status"] == "peer-reviewed"]
    out = [f"### arXiv citations with a peer-reviewed version ({len({r[1] for r in rows})} papers)\n",
           "Cite these as the venue version, e.g. *(Lewis et al., NeurIPS 2020)*.\n",
           "| Note | arXiv | Paper | Venue |", "|---|---|---|---|"]
    for note, ref, w in sorted(rows, key=lambda r: (r[0], r[1])):
        out.append(f"| [{note.split('/', 2)[-1]}](../../../{note}) | {ref} | {cite_label(db, w)} | {w['venue']} |")
    return "\n".join(out)


def exposure_rows(db, home):
    q = """SELECT n.note, w.canon FROM note_cites n JOIN seed s ON s.ref=n.ref JOIN work w ON w.id=s.work"""
    hits = db.execute(q + (" WHERE n.home=?" if home else ""), (home,) if home else ()).fetchall()
    ws = works(db, {h["canon"] for h in hits})
    per = defaultdict(Counter)
    for h in hits:
        per[h["note"]][ws[h["canon"]]["review_status"]] += 1
    return sorted(per.items(), key=lambda kv: -(kv[1]["preprint"] / sum(kv[1].values())))


def exposure_md(db, home):
    out = ["### Preprint exposure by note\n",
           "Share of each note's resolved citations that are preprint-only.\n",
           "| Note | Cited | Peer-reviewed | Preprint | Other | Preprint share |", "|---|---|---|---|---|---|"]
    for note, c in exposure_rows(db, home):
        tot = sum(c.values())
        other = tot - c["peer-reviewed"] - c["preprint"]
        out.append(f"| [{note.split('/', 2)[-1]}](../../../{note}) | {tot} | {c['peer-reviewed']} | {c['preprint']} | "
                   f"{other} | {c['preprint'] / tot:.0%} |")
    return "\n".join(out)


def status_md(db, home):
    seeds = works(db, seed_ids(db, home))
    c = Counter(w["review_status"] for w in seeds.values())
    held = sum(1 for w in seeds.values() if w["in_repo"])
    out = [f"### Our papers by review status ({len(seeds)}; {held} with a PDF in the repo)\n",
           " · ".join(f"{k}: {v}" for k, v in c.most_common()) + "\n",
           "In notes = linked from a note or references.md; a PDF we hold that no note links is unread or uncited.\n",
           "| Paper | Status | Venue | In notes | In repo |", "|---|---|---|---|---|"]
    q = "SELECT DISTINCT w.canon FROM note_cites n JOIN seed s ON s.ref=n.ref JOIN work w ON w.id=s.work"
    noted = {r[0] for r in db.execute(q + (" WHERE n.home=?" if home else ""), (home,) if home else ())}
    for w in sorted(seeds.values(), key=lambda w: (w["review_status"], -(w["year"] or 0))):
        out.append(f"| [{cite_label(db, w)}]({link(w)}) | {w['review_status']} | {w['venue'] or ''} | "
                   f"{'✓' if w['id'] in noted else '—'} | {flag(w)} |")
    miss = db.execute("SELECT ref FROM seed WHERE work IS NULL" + (" AND home=?" if home else ""),
                      (home,) if home else ()).fetchall()
    if miss:
        out.append(f"\nNot found in OpenAlex: {', '.join(r[0] for r in miss)}")
    return "\n".join(out)


def cmd_status(args):
    db = connect()
    print(status_md(db, args.home))
    if args.write:
        rows = potw.load_ledger()
        by_ledger = {r["ledger_key"]: r["work"] for r in db.execute("SELECT ledger_key, work FROM seed WHERE ledger_key IS NOT NULL AND work IS NOT NULL")}
        by_arxiv = {r["ref"]: r["work"] for r in db.execute("SELECT ref, work FROM seed WHERE kind='arxiv' AND work IS NOT NULL")}
        deg, meth, _ = in_degree(db, seed_ids(db, None))  # counted across the whole corpus
        n = 0
        for r in rows:
            wid = by_ledger.get(r["key"]) or by_arxiv.get(r.get("arxiv"))
            if not wid:
                continue
            w = db.execute("SELECT * FROM work WHERE id=(SELECT canon FROM work WHERE id=?)", (wid,)).fetchone()
            d, m = len(deg.get(w["id"], ())), len(meth.get(w["id"], ()))
            r.update(review_status=w["review_status"], venue=w["venue"], role=role_of(w, d, m), local_citations=d)
            n += 1
        potw.save_ledger(rows)
        log(f"status: wrote review_status, venue, role and local_citations to {n} ledger rows")


def cmd_roots(args):
    print(roots_md(connect(), args.home, args.n))


def cmd_acquire(args):
    db = connect()
    print(acquire_md(db, args.home, args.min))
    if args.download:
        download(db, args)
    elif args.queue:
        rows = potw.load_ledger()
        have = {r["key"] for r in rows} | {r.get("arxiv") for r in rows if r.get("arxiv")}
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        added = 0
        for w, d in acquire_list(db, args.home, args.min):
            key = w["arxiv"] or link(w)
            if key in have:
                continue
            rows.append({"key": key, "title": w["title"], "status": "queued", "source": "citegraph",
                         "arxiv": w["arxiv"], "url": link(w), "pillar": args.home, "topic": args.home,
                         "added_at": now, "venue": w["venue"], "review_status": w["review_status"],
                         "local_citations": d, "citations": w["cited_by"], "year": w["year"],
                         "first_author": first_author(db, w["id"]), "oa_pdf": w["oa_pdf"],
                         "reason": f"Peer-reviewed ({w['venue']}); cited by {d} of our papers."})
            added += 1
        potw.save_ledger(rows)
        log(f"acquire: queued {added} papers in the ledger")


def download(db, args):
    """acquire --download: the free copies of one home's reading list."""
    if not args.home:
        sys.exit("acquire --download needs --home: PDFs go into that home's sources/")
    done, failed = fetch_free(db, [(w, args.home, d) for w, d in acquire_list(db, args.home, args.min)])
    log(f"download: {done} PDFs saved, {len(failed)} failed")


def get_pdf(url, w):
    """The PDF at url; if that page isn't a PDF (a publisher landing page), the arXiv copy."""
    urls = [url] + ([f"https://arxiv.org/pdf/{w['arxiv']}"] if w["arxiv"] and "arxiv.org" not in url else [])
    for u in urls:
        try:
            pdf = potw.http_get(u, timeout=120)
        except Exception as exc:
            log(f"download: {u} failed: {exc}")
            continue
        if pdf.startswith(b"%PDF"):
            return pdf
        log(f"download: {u} is not a PDF")
    return None


def place_pdf(db, w, home, pdf):
    """Write pdf into the home's sources/ as <author>-<year>-<title-slug>.pdf and mark the work held."""
    dest = REPO / potw.HOMES[home][0] / "sources" / \
        f"{potw.make_slug(w['title'], first_author(db, w['id']), str(w['year']))}.pdf"
    if dest.exists():
        log(f"download: {dest.relative_to(REPO)} already exists; skipped")
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)  # programming has no sources/ yet
    dest.write_bytes(pdf)
    rel = dest.relative_to(REPO).as_posix()
    db.execute("UPDATE work SET in_repo=? WHERE canon=?", (rel, w["id"]))
    db.commit()
    return rel


def upsert_row(db, rows, w, home, d, rel, how):
    """Add a `downloaded` ledger row for a PDF we just got, or fill in the row already queued for it."""
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    key = w["arxiv"] or link(w)
    m = len(in_degree(db, seed_ids(db, None))[1].get(w["id"], ()))
    new = {"status": "downloaded", "have_pdf": True, "local_pdf": rel, "downloaded_at": now,
           "venue": w["venue"], "review_status": w["review_status"], "role": role_of(w, d, m),
           "local_citations": d}
    for r in rows:
        if r["key"] == key or (w["arxiv"] and r.get("arxiv") == w["arxiv"]):
            r.update(new)
            return
    rows.append({"key": key, "title": w["title"], "source": "citegraph", "arxiv": w["arxiv"], "url": link(w),
                 "pillar": home, "topic": home, "added_at": now, "citations": w["cited_by"], "year": w["year"],
                 "first_author": first_author(db, w["id"]), **new,
                 "reason": f"{w['review_status']} ({w['venue'] or 'no venue'}); cited by {d} of our papers. {how}"})


def fetch_free(db, items):
    """items: (work, home, local citations). Save each legal free copy and add a `downloaded` ledger
    row so /papers picks it up. Returns (saved, [(work, home, d) that failed])."""
    rows = potw.load_ledger()
    held = {r["key"] for r in rows if r.get("have_pdf")} | {r.get("arxiv") for r in rows if r.get("have_pdf") and r.get("arxiv")}
    done, failed = 0, []
    for w, home, d in items:
        how, url = availability(w)
        if not url or (w["arxiv"] or link(w)) in held or w["arxiv"] in held:
            continue
        pdf = get_pdf(url, w)
        rel = pdf and place_pdf(db, w, home, pdf)
        if not rel:
            if not pdf:
                failed.append((w, home, d))
            continue
        upsert_row(db, rows, w, home, d, rel, f"Got it from {how[2:]}.")
        potw.save_ledger(rows)
        done += 1
        log(f"download: {cite_label(db, w)[:60]} -> {rel}")
        time.sleep(3)
    return done, failed


# --- roles and primary sources ------------------------------------------------

SURVEY_RE = re.compile(r"\b(survey|review|overview|tutorial|primer)\b", re.I)
BENCH_RE = re.compile(r"\b(benchmark|dataset|corpus|leaderboard|test suite)\b|^measuring\b", re.I)
PRIMARY_MIN, PRIMARY_METH = 3, 2  # cited by ≥3 of our papers, ≥2 of them for the method


def role_of(w, d, m):
    """primary: several of our papers cite it for its method, so an idea likely starts there.
    survey / benchmark: by title; they collect citations without being an idea's source.
    new: too recent for our corpus to have cited it. secondary: everything else."""
    t = w["title"] or ""
    if SURVEY_RE.search(t):
        return "survey"
    if BENCH_RE.search(t):
        return "benchmark"
    if d >= PRIMARY_MIN and m >= PRIMARY_METH:
        return "primary"
    if d < PRIMARY_MIN and (w["year"] or 0) >= int(time.strftime("%Y")) - 1:
        return "new"
    return "secondary"


def primary_list(db):
    """Every primary work across the corpus: (work, home whose papers cite it most, cited by, for method)."""
    deg, meth, _ = in_degree(db, seed_ids(db, None))
    ws = works(db, [w for w in deg if len(deg[w]) >= PRIMARY_MIN])
    prim = {wid: w for wid, w in ws.items() if role_of(w, len(deg[wid]), len(meth.get(wid, ()))) == "primary"}
    best = {}
    for key in homes(None):
        hdeg = in_degree(db, seed_ids(db, key))[0]
        for wid in prim:
            n = len(hdeg.get(wid, ()))
            if n > best.get(wid, ("", 0))[1]:
                best[wid] = (key, n)
    out = [(w, best[wid][0], len(deg[wid]), len(meth.get(wid, ()))) for wid, w in prim.items() if wid in best]
    out.sort(key=lambda x: (-x[2], -x[3]))
    return out


def primary_md(db, failed=()):
    items = primary_list(db)
    held = [x for x in items if x[0]["in_repo"]]
    free = [x for x in items if not x[0]["in_repo"] and availability(x[0])[1]]
    paywalled = [x for x in items if not x[0]["in_repo"] and not availability(x[0])[1]]
    failed_ids = {w["id"] for w, _, _ in failed}
    by_hand = paywalled + [x for x in free if x[0]["id"] in failed_ids]
    free = [x for x in free if x[0]["id"] not in failed_ids]
    head = "| Cited by | For method | Paper | Venue | Home |"
    row = lambda w, h, d, m, extra: (f"| {d} | {m} | [{cite_label(db, w)}]({link(w)}) | "
                                     f"{w['venue'] or w['review_status']} | {h} |{extra}")
    out = ["# Primary sources\n",
           f"Generated by `citegraph.py primary` on {time.strftime('%Y-%m-%d')}. A work is **primary** when at "
           f"least {PRIMARY_MIN} of our papers cite it and at least {PRIMARY_METH} of them cite it for its method "
           "(Semantic Scholar citation intents), so an idea most likely starts there. Surveys and benchmarks are "
           "left out even when heavily cited. **Home** is the pillar whose papers cite it most; that is where "
           "the PDF goes.\n",
           f"{len(items)} primary works: {len(held)} in the repo, {len(free)} free to download, "
           f"{len(by_hand)} to fetch by hand.\n",
           f"## Fetch these by hand ({len(by_hand)})\n",
           "No free copy found, or the free link didn't serve a PDF. Put the PDF in `downloads/` (any file "
           "name) and run `uv run --with pypdf python scripts/papers/citegraph.py ingest`: it matches each "
           "PDF to its paper by title and files it in the right home.\n",
           head + " Link |", "|---|---|---|---|---|---|"]
    out += [row(w, h, d, m, f" {link(w)} |") for w, h, d, m in by_hand]
    if free:
        out += [f"\n## Free, not downloaded yet ({len(free)})\n",
                "`citegraph.py primary --download` fetches these.\n", head + " Get it |", "|---|---|---|---|---|---|"]
        out += [row(w, h, d, m, f" [{availability(w)[0]}]({availability(w)[1]}) |") for w, h, d, m in free]
    out += [f"\n## In the repo ({len(held)})\n", head + " PDF |", "|---|---|---|---|---|---|"]
    out += [row(w, h, d, m, f" `{w['in_repo']}` |") for w, h, d, m in held]
    return "\n".join(out)


def cmd_primary(args):
    db = connect()
    failed = []
    if args.download:
        todo = [(w, h, d) for w, h, d, m in primary_list(db) if not w["in_repo"]]
        done, failed = fetch_free(db, todo)
        log(f"primary: {done} PDFs saved, {len(failed)} free links failed")
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "primary.md").write_text(primary_md(db, failed) + "\n", encoding="utf-8")
    log(f"primary: {(REPORTS / 'primary.md').relative_to(REPO)}")


DOWNLOADS = REPO / "downloads"


def cmd_ingest(args):
    """File the PDFs dropped in downloads/: match each to a wanted paper (primary sources and every
    home's reading list) by arXiv id or DOI in the file name, else by its title on the first two
    pages, then move it to that home's sources/ and add a ledger row."""
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("ingest needs pypdf: uv run --with pypdf python scripts/papers/citegraph.py ingest")
    import logging
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    db = connect()
    wanted = {w["id"]: (w, h, d) for w, h, d, m in primary_list(db) if not w["in_repo"]}
    for key in homes(None):
        for w, d in acquire_list(db, key, args.min):
            if w["id"] not in wanted or d > wanted[w["id"]][2]:
                wanted[w["id"]] = (w, key, d)
    squash = lambda t: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", t or "").lower())
    rows = potw.load_ledger()
    moved = 0
    for pdf in sorted(DOWNLOADS.glob("*.pdf")):
        hit, ref = None, ref_from_pdf(pdf)
        if ref:
            hit = next((c for c in wanted.values()
                        if (c[0]["arxiv"] if ref[0] == "arxiv" else (c[0]["doi"] or "").lower()) == ref[1].lower()), None)
        if not hit:
            try:
                text = squash(" ".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages[:2]))
            except Exception as exc:
                log(f"ingest: {pdf.name}: can't read it ({exc}); left in downloads/")
                continue
            hits = [c for c in wanted.values() if len(squash(c[0]["title"])) >= 15 and squash(c[0]["title"]) in text]
            hit = max(hits, key=lambda c: len(c[0]["title"])) if hits else None
        if not hit:
            log(f"ingest: {pdf.name}: matches none of the {len(wanted)} wanted papers; left in downloads/")
            continue
        w, home, d = hit
        rel = place_pdf(db, w, home, pdf.read_bytes())
        if not rel:
            continue
        pdf.unlink()
        upsert_row(db, rows, w, home, d, rel, f"Fetched by hand into downloads/ as {pdf.name}.")
        potw.save_ledger(rows)
        moved += 1
        log(f"ingest: {pdf.name} -> {rel} ({cite_label(db, w)[:60]})")
    log(f"ingest: {moved} PDFs filed")


# --- references.md: where the ideas come from ---------------------------------

ORIGINS_START, ORIGINS_END = "<!-- citegraph:origins start -->", "<!-- citegraph:origins end -->"
ORIGINS_BEFORE = re.compile(r"^## (AI Papers of the Week|Source quality|Secondary|About the upstream|Deliberately)", re.M)


def origins_md(db, home, folder, n=25):
    seeds = seed_ids(db, home)
    deg, meth, _ = in_degree(db, seeds)
    ws = works(db, [w for w in deg if len(deg[w]) >= PRIMARY_MIN])
    picks = [(w, len(deg[wid]), len(meth.get(wid, ()))) for wid, w in ws.items()
             if role_of(w, len(deg[wid]), len(meth.get(wid, ()))) == "primary"]
    if not picks:
        return None
    picks.sort(key=lambda x: (-x[1], -x[2]))
    out = ["## Where the ideas come from\n",
           f"Generated by `citegraph.py refs --write` on {time.strftime('%Y-%m-%d')}; rerun it instead of "
           f"editing between the markers. These works are cited by at least {PRIMARY_MIN} of this pillar's "
           f"papers, at least {PRIMARY_METH} of them for the method, so an idea most likely starts there. "
           "When a note states one of these ideas, cite the origin as well as the recent paper. "
           "**Cited by** counts this pillar's papers; **For method** counts those citing it for its method. "
           "⚑ = not peer-reviewed. Fetch the missing ones with `citegraph.py primary --download`.\n",
           "| Paper | Venue | Cited by | For method | We hold |", "|---|---|---|---|---|"]
    for w, d, m in picks[:n]:
        venue = (w["venue"] or "") + (" ⚑" if w["review_status"] != "peer-reviewed" else "")
        if w["in_repo"]:
            held = f"[✓ PDF]({os.path.relpath(REPO / w['in_repo'], REPO / folder)})"
        else:
            how, url = availability(w)
            held = f"— ([{how[2:]}]({url}))" if url else "— (no free copy)"
        out.append(f"| [{cite_label(db, w)}]({link(w)}) | {venue.strip() or w['review_status']} | {d} | {m} | {held} |")
    if len(picks) > n:
        out.append(f"\n{len(picks) - n} more in [the citation report](../../scripts/papers/reports/citegraph-{home}.md).")
    return "\n".join(out)


def export_html(args):
    """One self-contained page (d3 from a CDN) per home, or for the whole corpus."""
    db = connect()
    for key in ([args.home] if args.home else [None, *homes(None)]):
        seeds = seed_ids(db, key)
        if not seeds:
            continue
        deg, meth, _ = in_degree(db, seeds)
        floor = 2 if key else 3
        keep = seeds | {w for w in deg if len(deg[w]) >= floor}
        ws = works(db, keep)
        notes = defaultdict(set)
        q = "SELECT w.canon, n.note FROM note_cites n JOIN seed s ON s.ref=n.ref JOIN work w ON w.id=s.work"
        for r in db.execute(q + (" WHERE n.home=?" if key else ""), (key,) if key else ()):
            notes[r[0]].add(r[1])
        nodes = []
        for wid, w in ws.items():
            d, m = len(deg.get(wid, ())), len(meth.get(wid, ()))
            how, url = availability(w)
            nodes.append({"id": wid, "t": w["title"], "a": first_author(db, wid), "yr": w["year"], "v": w["venue"],
                          "s": w["review_status"], "r": role_of(w, d, m), "d": d, "m": m, "h": w["in_repo"],
                          "u": link(w), "g": None if w["in_repo"] else [how, url], "seed": wid in seeds,
                          "notes": sorted(notes.get(wid, ()))})
        canon = {r[0]: r[1] for r in db.execute("SELECT id, canon FROM work")}
        links = {}
        for c in db.execute("SELECT src, dst, intents FROM cites"):
            s_, d_ = canon.get(c[0], c[0]), canon.get(c[1], c[1])
            if s_ in ws and d_ in ws and s_ != d_:
                links[(s_, d_)] = links.get((s_, d_), 0) or int(bool(c[2] and "methodology" in c[2]))
        data = {"nodes": nodes, "links": [{"s": a, "t": b, "m": m} for (a, b), m in links.items()]}
        title = f"Citation graph: {key or 'all pillars'}"
        page = (HERE / "citegraph_view.html.tmpl").read_text(encoding="utf-8")
        page = page.replace("__TITLE__", title).replace("__MIN__", str(floor)).replace(
            "__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
        out = REPORTS / f"graph-{key or 'all'}.html"
        REPORTS.mkdir(exist_ok=True)
        out.write_text(page, encoding="utf-8")
        log(f"export: {out.relative_to(REPO)} ({len(nodes)} nodes, {len(links)} edges)")


def cmd_refs(args):
    db = connect()
    for key, folder in homes(args.home).items():
        block = origins_md(db, key, folder)
        path = REPO / folder / "references.md"
        if not block:
            log(f"refs: {key}: no primary sources yet")
            continue
        if not args.write:
            print(f"\n=== {path.relative_to(REPO)}\n{block}")
            continue
        if not path.exists():
            log(f"refs: {key}: no references.md; skipped")
            continue
        text = path.read_text(encoding="utf-8")
        blk = f"{ORIGINS_START}\n{block}\n{ORIGINS_END}"
        if ORIGINS_START in text:
            text = re.sub(re.escape(ORIGINS_START) + ".*?" + re.escape(ORIGINS_END), lambda _: blk, text, flags=re.S)
        elif m := ORIGINS_BEFORE.search(text):
            text = text[:m.start()] + blk + "\n\n" + text[m.start():]
        else:
            text = text.rstrip() + "\n\n" + blk + "\n"
        path.write_text(text, encoding="utf-8")
        log(f"refs: {path.relative_to(REPO)}")


def cmd_upgrade(args):
    print(upgrade_md(connect(), args.home))


def cmd_exposure(args):
    print(exposure_md(connect(), args.home))


def cmd_report(args):
    if args.all:
        index = ["# Citation graph reports\n",
                 "One report per home: our papers and their review status, what they cite most, where the "
                 "ideas come from, and peer-reviewed papers we lack (with whether a free copy exists). "
                 "Regenerate with `python3 scripts/papers/citegraph.py report --all`.\n",
                 "| Home | Our papers | Peer-reviewed | With PDF | To acquire | Free |", "|---|---|---|---|---|---|"]
        db = connect()
        for key in homes(None):
            seeds = works(db, seed_ids(db, key))
            if not seeds:
                continue
            args.home = key
            write_report(args)
            picks = acquire_list(db, key, args.min)
            free = sum(availability(w)[0].startswith("✓") for w, _ in picks)
            index.append(f"| [{key}](citegraph-{key}.md) | {len(seeds)} | "
                         f"{sum(w['review_status'] == 'peer-reviewed' for w in seeds.values())} | "
                         f"{sum(bool(w['in_repo']) for w in seeds.values())} | {len(picks)} | {free} |")
        (REPORTS / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
        log(f"report: {REPORTS.relative_to(REPO)}/README.md")
        return
    write_report(args)


def write_report(args):
    db = connect()
    name = args.home or "all"
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"citegraph-{name}.md"
    body = [f"# Citation graph — {name}\n",
            f"> Generated by `scripts/papers/citegraph.py report{' --home ' + args.home if args.home else ''}` "
            f"on {time.strftime('%Y-%m-%d')}. Sources: OpenAlex (references, venues, open-access PDFs), "
            "DBLP (peer-reviewed venue), Semantic Scholar (citation intents, when fetched). "
            "Counts are lower bounds: reference lists in these APIs are incomplete.\n",
            provisional_md(db, args.home),
            status_md(db, args.home), roots_md(db, args.home, args.n), acquire_md(db, args.home, args.min),
            upgrade_md(db, args.home), exposure_md(db, args.home), role_check_md(args.home)]
    body = [b for b in body if b]
    path.write_text("\n\n".join(body) + "\n", encoding="utf-8")
    log(f"report: {path.relative_to(REPO)}")


def provisional_md(db, home):
    q = "SELECT home, fetched FROM provisional" + (" WHERE home=?" if home else "")
    got = db.execute(q, (home,) if home else ()).fetchall()
    if not got:
        return ""
    which = ", ".join(f"`{r[0]}` ({r[1]})" for r in got)
    return (f"> **Provisional.** Seeded from queued readings as well as read ones: {which}. The graph shows "
            "what the queue cites, not what the notes rest on; re-fetch without `--include-queued` once "
            "the readings are integrated.\n")


def role_check_md(home):
    """Where triage (source_role), the curated list or a manual edit disagrees with the graph's role."""
    rows = [r for r in potw.load_ledger() if (not home or r.get("pillar") == home) and r.get("role")
            and r["status"] != "skipped"]
    out = []
    for r in rows:
        said = r.get("role_manual") or r.get("source_role") or r.get("curated_role")
        graph = r["role"] if r["role"] in ("primary", "secondary") else None
        if said in ("primary", "secondary") and graph and said != graph:
            out.append(f"| {(r.get('title') or r['key'])[:80]} | {said} | {graph} | {r.get('local_citations') or 0} | "
                       f"{r['status']} | `{r['key']}` |")
    if not out:
        return ""
    return "\n".join([f"### Role check ({len(out)} disagreements)\n",
                      "Triage or the curated list called these one thing; the citation graph (cited by "
                      f">= {PRIMARY_MIN} of our papers, >= {PRIMARY_METH} for the method, means primary) says another. "
                      "Settle them in `discover.py review`: a role edit there wins over both.\n",
                      "| Reading | Said | Graph | Local cites | Status | Key |", "|---|---|---|---|---|---|", *out])


def cmd_bridges(args):
    """Readings that sit between a subject home and an AI home."""
    rows = potw.load_ledger()
    found = []
    for r in rows:
        mine = r.get("discovered_for") or r.get("pillar")
        also = r.get("also_found_for") or []
        if not mine or mine not in potw.HOMES or r["status"] == "skipped":
            continue
        sides = {mine, *[a for a in also if a in potw.HOMES]}
        if any(is_ai_home(h) for h in sides) and any(not is_ai_home(h) for h in sides):
            found.append((r, sorted(sides)))
    db = connect()
    subject = [k for k in potw.HOMES if not is_ai_home(k)]
    ai = [k for k in potw.HOMES if is_ai_home(k)]
    seeds_s = {w for k in subject for w in seed_ids(db, k)}
    seeds_a = {w for k in ai for w in seed_ids(db, k)}
    deg_s, _, _ = in_degree(db, seeds_s)
    deg_a, _, _ = in_degree(db, seeds_a)
    both = sorted((w for w in deg_s if w in deg_a), key=lambda w: -min(len(deg_s[w]), len(deg_a[w])))[: args.n]
    ws = works(db, both)
    out = ["# Bridges between the subject homes and the AI homes\n",
           f"> Generated by `scripts/papers/citegraph.py bridges` on {time.strftime('%Y-%m-%d')}. A bridge is a "
           "reading that discovery found for a subject home (analytics, classical-ml, data-systems, ml-systems, "
           "programming) and an AI home, or a work cited from both sides. Good candidates for a "
           "cross-link between notes.\n",
           f"## Found for both sides ({len(found)})\n",
           "| Reading | Year | Homes | Status | Note |", "|---|---|---|---|---|"]
    for r, sides in sorted(found, key=lambda x: -(x[0].get("citations") or 0)):
        out.append(f"| {(r.get('title') or r['key'])[:90]} | {r.get('year') or ''} | {', '.join(sides)} | "
                   f"{r['status']} | {r.get('note') or r.get('discovered_note') or ''} |")
    out += [f"\n## Cited from both sides (top {len(both)})\n",
            "Subject / AI = how many of each side's papers cite it.\n",
            "| Work | Subject | AI | In repo |", "|---|---|---|---|"]
    for w in both:
        if w in ws:
            out.append(f"| [{cite_label(db, ws[w])}]({link(ws[w])}) | {len(deg_s[w])} | {len(deg_a[w])} | {flag(ws[w])} |")
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / "bridges.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    log(f"bridges: {len(found)} found for both sides, {len(both)} cited from both -> {path.relative_to(REPO)}")


def cmd_export(args):
    if args.html:
        return export_html(args)
    db = connect()
    seeds = seed_ids(db, args.home)
    deg, _, _ = in_degree(db, seeds)
    keep = seeds | {w for w in deg if len(deg[w]) >= 2}
    ws = works(db, keep)
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">']
    for k, t in (("title", "string"), ("year", "int"), ("status", "string"), ("venue", "string"),
                 ("seed", "boolean"), ("in_repo", "boolean"), ("local", "int")):
        lines.append(f'<key id="{k}" for="node" attr.name="{k}" attr.type="{t}"/>')
    lines.append('<key id="intents" for="edge" attr.name="intents" attr.type="string"/>')
    lines.append('<graph edgedefault="directed">')
    for w in ws.values():
        lines.append(f'<node id="{w["id"]}"><data key="title">{esc(w["title"])}</data><data key="year">{w["year"] or 0}</data>'
                     f'<data key="status">{w["review_status"]}</data><data key="venue">{esc(w["venue"])}</data>'
                     f'<data key="seed">{str(w["id"] in seeds).lower()}</data>'
                     f'<data key="in_repo">{str(bool(w["in_repo"])).lower()}</data>'
                     f'<data key="local">{len(deg.get(w["id"], ()))}</data></node>')
    canon = {r[0]: r[1] for r in db.execute("SELECT id, canon FROM work")}
    seen = set()
    for c in db.execute("SELECT src, dst, intents FROM cites"):
        s, d = canon.get(c[0], c[0]), canon.get(c[1], c[1])
        if s in ws and d in ws and s != d and (s, d) not in seen:
            seen.add((s, d))
            lines.append(f'<edge source="{s}" target="{d}"><data key="intents">{esc(c[2])}</data></edge>')
    lines += ["</graph>", "</graphml>"]
    out = REPORTS / f"citegraph-{args.home or 'all'}.graphml"
    REPORTS.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"export: {len(ws)} nodes, {len(seen)} edges -> {out.relative_to(REPO)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(required=True)
    for name, fn in (("fetch", cmd_fetch), ("dblp", cmd_dblp), ("intents", cmd_intents), ("status", cmd_status),
                     ("roots", cmd_roots), ("acquire", cmd_acquire), ("preprints", cmd_preprints),
                     ("primary", cmd_primary), ("ingest", cmd_ingest), ("refs", cmd_refs),
                     ("upgrade", cmd_upgrade),
                     ("exposure", cmd_exposure), ("report", cmd_report), ("export", cmd_export),
                     ("bridges", cmd_bridges)):
        p = sub.add_parser(name)
        p.add_argument("--home", help="one home key (rag, loop, analytics, ...); default every home")
        p.add_argument("--subject", action="store_true",
                       help="only the subject homes (analytics, classical-ml, data-systems, ml-systems, programming)")
        p.add_argument("--n", type=int, default=40, help="rows in the most-cited table")
        p.add_argument("--min", type=int, default=3, help="acquire: minimum local in-degree")
        if name == "status":
            p.add_argument("--write", action="store_true", help="write review_status and venue to the ledger")
        if name == "acquire":
            p.add_argument("--queue", action="store_true", help="append the list to the ledger as queued rows")
            p.add_argument("--download", action="store_true",
                           help="fetch the legal free copies into the home's sources/ and add downloaded ledger rows")
        if name == "primary":
            p.add_argument("--download", action="store_true",
                           help="fetch the legal free copies into the citing home's sources/")
        if name == "refs":
            p.add_argument("--write", action="store_true",
                           help="write the block into each references.md (default: print it)")
        if name == "export":
            p.add_argument("--html", action="store_true", help="interactive pages reports/graph-<home>.html")
        if name == "report":
            p.add_argument("--all", action="store_true", help="one report per home, plus reports/README.md")
        if name == "fetch":
            p.add_argument("--include-queued", action="store_true",
                           help="also seed from queued rows (thin homes); their reports get a provisional banner")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    global SUBJECT_ONLY
    SUBJECT_ONLY = args.subject
    args.fn(args)


if __name__ == "__main__":
    main()
