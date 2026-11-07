#!/usr/bin/env python3
"""Check the reading ledger against the repo.

Gated (fail `make test`), because they pass today and must keep passing:
  note-path      a row's `note` is a file that exists
  home           a row's `pillar` is a home in potw.py
  pdf-row        every PDF under a sources/ folder is on a row (local_pdf or copies)
  no-citation    integrated, but nothing in the repo cites it (`mark --no-citation` records an exception)
  dup-id         rows sharing a DOI or arXiv id (`merged_into` rows are out of it)

Report only, because each has a backlog a person has to rule on:
  no-references  integrated and cited, but no references.md lists it
  outside-home   integrated and cited, but only outside the row's home
  note-no-cite   `note` is set, but that file does not cite the row (mostly triage's guess at a note)
  dup-title      rows with one title: see DISTINCT_TITLES for those checked and kept apart
  no-extraction  integrated with a PDF, but no full (schema 1) extraction in extractions/; /extract fills it

A citation is the row's arXiv id, DOI, URL or PDF name, its title, its short name with the author or
year on the same line, or for a book chapter a references.md row mapping that chapter. citegraph's
generated reading lists never count: listing a work there does not mean anyone read it.

  python3 scripts/papers/check_ledger.py                 # summary; exit 1 if a gated check fails
  python3 scripts/papers/check_ledger.py --list no-citation
  python3 scripts/papers/check_ledger.py --write-report  # writes scripts/papers/reports/ledger-check.md
  python3 scripts/papers/check_ledger.py --backfill-notes --dry-run
"""
import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import potw

GATED = ("note-path", "home", "pdf-row", "no-citation", "dup-id")
REPORT_ONLY = ("no-references", "outside-home", "note-no-cite", "dup-title", "no-extraction")
REPORT = "scripts/papers/reports/ledger-check.md"
ORIGINS = re.compile(r"<!-- citegraph:origins start -->.*?<!-- citegraph:origins end -->", re.S)
ARXIV = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(?:v\d+)?(?!\d)")
ARXIV_URL = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", re.I)
DOI = re.compile(r"10\.\d{4,9}/[^\s)\]>\"'|]+")
URL = re.compile(r"https?://[^\s)\]>\"'|]+")
PDF_NAME = re.compile(r"[\w.%-]+\.pdf\b", re.I)
# sources/<book>/chNN-*.pdf, sources/<book>/appendix-*.pdf or a flat sources/<book>-chNN-*.pdf
CHAPTER = re.compile(r"(?:/sources/([^/]+)/|/sources/([^/]+?)-)(?:ch(\d\d)|appendix(?:-[a-z](?=-))?)-[^/]*\.pdf$")
CHAPTERS = re.compile(r"\bch(?:apters?|s)?\.?\s*(\d+(?:\s*(?:[-–—,&]|and)\s*\d+)*)", re.I)
NOTE_LINK = re.compile(r"\]\((?:\./)?(notes/[^)#\s]+\.md)")
SKIP_DIRS = potw.PDF_SKIP_DIRS | {"sources"}
# Rows with one title that a reader compared and found to be different works.
DISTINCT_TITLES = {
    "chain of agents": "different papers",
    "deciphering data architectures choosi z library": "three chapters; the PDF metadata names the book",
    "efficient agents": "different papers",
    "emergent misalignment": "different papers on one theme",
    "python for data analysis": "two editions, each with its own PDF",
    "self evolving agents": "different papers",
    "sophia": "different papers",
}


def names_chapter(text, number):
    """Does this text name chapter `number`? `ch. 1–3`, `Ch 7, 9`, `chapters 2 and 4`.
    A number of None asks about an appendix."""
    if number is None:
        return bool(re.search(r"\bappendi(x|ces)\b", text, re.I))
    for spec in CHAPTERS.findall(text):
        for a, b in re.findall(r"(\d+)(?:\s*[-–—]\s*(\d+))?", spec):
            if int(a) <= number <= int(b or a):
                return True
    return False


def norm(text):
    """Lower-case words joined by one space, with accents and punctuation gone."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def clean_url(url):
    url = re.sub(r"^https?://(www\.)?", "", (url or "").strip().lower())
    return url.rstrip("/.,;:*_`")


def clean_doi(doi):
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", (doi or "").strip().lower()).rstrip(".,;:*_`")


def row_arxiv(r):
    for v in (r.get("arxiv"), r.get("key")):
        if isinstance(v, str) and re.fullmatch(r"\d{4}\.\d{4,5}", v):
            return v
    m = ARXIV_URL.search(r.get("url") or "")
    return m.group(1) if m else None


def row_doi(r):
    for v in (r.get("doi"), r.get("key"), r.get("url")):
        if isinstance(v, str) and (v.startswith("doi:") or "doi.org/10." in v or v.startswith("10.")):
            return clean_doi(v)
    return None


def row_pdfs(r):
    copies = r.get("copies") if isinstance(r.get("copies"), list) else []
    return [p for p in [r.get("local_pdf"), *copies] if isinstance(p, str)]


def corpus_files():
    """Every note and references.md the ledger can be cited from, one entry each."""
    seen = {}
    for folder in sorted(set(potw.PILLARS.values())):
        base = potw.REPO / folder
        if not base.is_dir():
            continue
        refs = [p for p in base.rglob("references.md") if not set(p.relative_to(base).parts) & SKIP_DIRS]
        for path in [*potw.home_notes(folder), *refs]:
            seen[path.relative_to(potw.REPO).as_posix()] = path
    return seen


class Corpus:
    """What the notes and references.md cite, indexed so a whole-ledger pass takes seconds."""

    def __init__(self):
        self.files = {}  # path -> (raw lower text, normalised text)
        self.ids = defaultdict(set)  # "arxiv:<id>", "doi:<doi>", "url:<url>", "pdf:<name>" -> paths
        self.words = defaultdict(set)  # word -> paths
        for rel, path in corpus_files().items():
            text = ORIGINS.sub("", path.read_text(encoding="utf-8", errors="replace"))
            low = text.lower()
            flat = norm(text)
            self.files[rel] = (low, f" {flat} ")
            for m in ARXIV.finditer(low):
                self.ids[f"arxiv:{m.group(1)}"].add(rel)
            for m in DOI.finditer(low):
                self.ids[f"doi:{clean_doi(m.group())}"].add(rel)
            for m in URL.finditer(low):
                self.ids[f"url:{clean_url(m.group())}"].add(rel)
            for m in PDF_NAME.finditer(low):
                self.ids[f"pdf:{m.group()}"].add(rel)
            for word in set(flat.split()):
                self.words[word].add(rel)

    def _with_words(self, phrase):
        sets = [self.words.get(w, set()) for w in phrase.split()]
        return set.intersection(*sets) if sets else set()

    def _by_title(self, r):
        title = r.get("title") or ""
        whole = norm(title)
        hits = set()
        if len(whole.split()) >= 4 and len(whole) >= 20:
            hits |= {f for f in self._with_words(whole) if f" {whole} " in self.files[f][1]}
        short = norm(title.split(":")[0]) if ":" in title else whole
        if short and len(short) >= 4 and short != whole or short and len(whole.split()) < 4:
            hits |= self._named_on_a_line(r, short)
        return hits

    def _named_on_a_line(self, r, name):
        """A short name counts only beside its author or year: `MemGPT (Packer et al., 2023)`."""
        marks = [norm(r.get("first_author") or "").split()[-1:], [str(r.get("year"))] if r.get("year") else []]
        marks = [m[0] for m in marks if m]
        hits = set()
        if not marks:
            return hits
        for f in self._with_words(name):
            for line in self.files[f][0].splitlines():
                flat = f" {norm(line)} "
                if f" {name} " in flat and any(f" {m} " in flat for m in marks):
                    hits.add(f)
                    break
        return hits

    def _chapter_citations(self, r):
        """Files citing a book chapter: the note a references.md maps it to, that references.md,
        and any note citing `*Book*, ch. N` on one line."""
        pdf = next((p for p in row_pdfs(r) if CHAPTER.search(p)), None)
        if not pdf:
            return []
        m = CHAPTER.search(pdf)
        number = int(m.group(3)) if m.group(3) else None  # None: an appendix
        slug = m.group(1)  # flat names have no folder a references row could link
        book = norm((r.get("title") or "").split(" | ")[-1]) if " | " in (r.get("title") or "") else None
        files = set()
        if book:
            files |= self._with_words(book)
        if slug:
            files |= {f for f, (low, _) in self.files.items() if f"{slug.lower()}/" in low}
        mapped = []
        for f in sorted(files):
            for line in self.files[f][0].splitlines():
                if not ((slug and f"{slug.lower()}/" in line) or (book and f" {book} " in f" {norm(line)} ")):
                    continue
                for segment in line.split(";") if "folded in" in line else [line]:
                    if not names_chapter(segment, number):
                        continue
                    if f.endswith("references.md"):
                        notes = [(Path(f).parent / t).as_posix() for t in NOTE_LINK.findall(segment)]
                        mapped += [n for n in notes if n in self.files]
                    mapped.append(f)
        return list(dict.fromkeys(mapped))

    def citing_files(self, r, home=None):
        """Paths citing the row, best first. With a home, only files inside that home's folder."""
        chapter_first = self._chapter_citations(r)
        hits = set(chapter_first)
        arxiv, doi = row_arxiv(r), row_doi(r)
        if arxiv:
            hits |= self.ids.get(f"arxiv:{arxiv}", set())
        if doi:
            hits |= self.ids.get(f"doi:{doi}", set())
        for url in (r.get("url"), r.get("oa_pdf_url")):
            if isinstance(url, str) and url:
                hits |= self.ids.get(f"url:{clean_url(url)}", set())
        for pdf in row_pdfs(r):
            if not (m := CHAPTER.search(pdf)) or m.group(2):  # chapter files repeat names across books
                hits |= self.ids.get(f"pdf:{Path(pdf).name.lower()}", set())
        if not any(CHAPTER.search(p) for p in row_pdfs(r)):
            hits |= self._by_title(r)
        folder = potw.PILLARS.get(home or r.get("pillar") or r.get("topic") or "")
        inside = lambda f: bool(folder) and (f == folder or f.startswith(f"{folder}/"))
        if home:
            hits = {f for f in hits if inside(f)}
        rank = lambda f: (f not in chapter_first, not inside(f), f.endswith("references.md"), f)
        return sorted(hits, key=rank)


def best_note(r, found):
    """The file to record as `note`: the current one if it cites the row, else the best found."""
    return r["note"] if r.get("note") in found else found[0] if found else None


def source_pdfs():
    """Every PDF filed in a sources/ folder of a course area, ignoring local-only and vendored trees."""
    areas = sorted({f.split("/")[0] for f in potw.PILLARS.values()})
    found = []
    for area in areas:
        base = potw.REPO / area
        if base.is_dir():
            for p in base.rglob("*.pdf"):
                parts = p.relative_to(potw.REPO).parts
                if "sources" in parts and not set(parts) & potw.PDF_SKIP_DIRS:
                    found.append(p.relative_to(potw.REPO).as_posix())
    return sorted(found)


def check(rows, corpus=None):
    """{check name: [one line per finding]}."""
    corpus = corpus or Corpus()
    out = {name: [] for name in (*GATED, *REPORT_ONLY)}
    live = [r for r in rows if not r.get("merged_into")]
    for r in live:
        note = r.get("note")
        if note and not (potw.REPO / note).is_file():
            out["note-path"].append(f"{r['key']}: {note}")
        if r.get("pillar") and r["pillar"] not in potw.HOMES:
            out["home"].append(f"{r['key']}: {r['pillar']}")
    held = {p for r in rows for p in row_pdfs(r)}
    out["pdf-row"] = [f"{p}: run `potw.py scan --offline`" for p in source_pdfs() if p not in held]

    for r in live:
        if r.get("status") != "integrated" or r.get("no_citation"):
            continue
        found = corpus.citing_files(r)
        where = f"({r.get('pillar') or 'no home'}) {r.get('title') or ''}".strip()
        if not found:
            out["no-citation"].append(f"{r['key']} {where}")
        elif not any(f.endswith("references.md") for f in found):
            out["no-references"].append(f"{r['key']} {where}: cited in {found[0]}")
        elif not corpus.citing_files(r, home=r.get("pillar") or r.get("topic") or "none"):
            out["outside-home"].append(f"{r['key']} {where}: cited in {found[0]}")
        if found and r.get("note") and r["note"] not in found:
            out["note-no-cite"].append(f"{r['key']}: {r['note']}")

    by_title, by_id = defaultdict(list), defaultdict(list)
    for r in live:
        title = norm(r.get("title"))
        if title:
            by_title[title].append(r["key"])
        for ident in (row_arxiv(r), row_doi(r)):
            if ident:
                by_id[ident].append(r["key"])
    out["dup-title"] = [f"{t}: {', '.join(keys)}" + (f" (kept apart: {DISTINCT_TITLES[t]})" if t in DISTINCT_TITLES else "")
                        for t, keys in sorted(by_title.items()) if len(keys) > 1]
    out["dup-id"] = [f"{i}: {', '.join(keys)}" for i, keys in sorted(by_id.items()) if len(set(keys)) > 1]

    import extract  # here, not at the top: extract imports potw, which imports this module lazily
    for r in live:
        if r.get("status") == "integrated" and r.get("local_pdf") and (potw.REPO / r["local_pdf"]).is_file():
            x = extract.load(r["key"])
            if not x or x.get("schema") != extract.SCHEMA:
                out["no-extraction"].append(f"{r['key']} ({r.get('pillar') or 'no home'}): "
                                            + ("salvaged report only" if x else "none"))
    return out


def write_report(result):
    lines = ["# Ledger check", "",
             "Generated by `make ledger-report`. Do not edit. Report-only checks have a backlog for a person to rule on.", ""]
    for name in (*GATED, *REPORT_ONLY):
        gate = "gated" if name in GATED else "report only"
        lines += [f"## {name} ({gate}): {len(result[name])}", ""]
        lines += [f"- {line}" for line in result[name]] or ["None."]
        lines.append("")
    path = potw.REPO / REPORT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def backfill_notes(dry_run=False):
    """Set `note` on integrated rows with none, from the citations found. Leaves the rest blank."""
    corpus = Corpus()
    rows = potw.load_ledger()
    filled = missed = 0
    for r in rows:
        if r["status"] == "integrated" and not r.get("note"):
            found = corpus.citing_files(r)
            if found:
                r["note"] = best_note(r, found)
                filled += 1
            else:
                missed += 1
    if not dry_run:
        potw.save_ledger(rows)
    print(f"{'would fill' if dry_run else 'filled'} {filled} notes; {missed} integrated rows have no citation to point at")


def main():
    ap = argparse.ArgumentParser(description="Check the reading ledger against the repo.")
    ap.add_argument("--list", choices=(*GATED, *REPORT_ONLY), help="print every finding of one check")
    ap.add_argument("--write-report", action="store_true", help=f"write {REPORT}")
    ap.add_argument("--backfill-notes", action="store_true", help="fill `note` on integrated rows from citations")
    ap.add_argument("--dry-run", action="store_true", help="with --backfill-notes, change nothing")
    args = ap.parse_args()
    if args.backfill_notes:
        return backfill_notes(args.dry_run)
    result = check(potw.read_jsonl(potw.LEDGER))
    if args.list:
        print("\n".join(result[args.list]))
        return None
    for name in (*GATED, *REPORT_ONLY):
        print(f"{'FAIL' if name in GATED and result[name] else 'ok  ' if name in GATED else 'info'} {name:<14} {len(result[name])}")
    if args.write_report:
        print(f"wrote {write_report(result).relative_to(potw.REPO)}")
    failed = [n for n in GATED if result[n]]
    for name in failed:
        print(f"\n{name}:", *result[name][:20], sep="\n  ")
    if failed:
        sys.exit(1)
    return None


if __name__ == "__main__":
    main()
