#!/usr/bin/env python3
"""Tests for the ledger check and the potw.py commands that use it: python3 scripts/test_check_ledger.py"""
import argparse
import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent / "papers"))
import check_ledger
import potw

RAG = "generative-ai/02-rag-retrieval"
ORIGINS = "<!-- citegraph:origins start -->\n{}\n<!-- citegraph:origins end -->\n"


def row(key, **fields):
    return {"key": key, "title": key, "status": "integrated", "pillar": "rag", **fields}


class TempRepo(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        patches = [mock.patch.object(potw, "REPO", self.repo),
                   mock.patch.object(potw, "PILLARS", {"rag": RAG, "programming": "programming"})]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def write(self, path, text=""):
        full = self.repo / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(text, encoding="utf-8")
        return path

    def cited(self, r, home=None):
        return check_ledger.Corpus().citing_files(r, home=home)


class Citations(TempRepo):
    def test_finds_arxiv_id_doi_url_and_pdf_name(self):
        note = self.write(f"{RAG}/notes/01-a.md", "See [x](https://arxiv.org/abs/2301.12345v2), doi 10.1234/ABC.\n"
                                                  "[y](https://example.org/post/) and sources/smith-2020.pdf\n")
        self.assertEqual(self.cited(row("2301.12345")), [note])
        self.assertEqual(self.cited(row("doi:10.1234/abc")), [note])
        self.assertEqual(self.cited(row("u", url="http://www.example.org/post")), [note])
        self.assertEqual(self.cited(row("s", local_pdf=f"{RAG}/sources/smith-2020.pdf")), [note])

    def test_title_needs_length_or_an_author_beside_it(self):
        note = self.write(f"{RAG}/notes/01-a.md", "Attention Is All You Need changed this.\n"
                                                  "Like MemGPT (Packer et al.), it pages.\nAnd Orbit helps.\n")
        self.assertEqual(self.cited(row("t", title="Attention Is All You Need")), [note])
        self.assertEqual(self.cited(row("m", title="MemGPT: Towards LLMs", first_author="Packer")), [note])
        self.assertEqual(self.cited(row("o", title="Orbit: A Thing", first_author="Nobody")), [])

    def test_a_generated_reading_list_is_not_a_citation(self):
        self.write(f"{RAG}/references.md", ORIGINS.format("| [Paper](https://arxiv.org/abs/2301.12345) |"))
        self.assertEqual(self.cited(row("2301.12345")), [])

    def test_book_chapter_maps_to_its_note_through_the_books_row(self):
        note = self.write(f"{RAG}/notes/02-b.md")
        refs = self.write(f"{RAG}/references.md", "| Author, *Book* [sources/my-book/](sources/my-book/). Folded in as: "
                                                  "ch. 1–3 and appendix A → [01](notes/01-a.md); ch. 5 why → [02](notes/02-b.md) |\n")
        r = row("c", title="5. Why | Book", local_pdf=f"{RAG}/sources/my-book/ch05-why.pdf")
        self.assertEqual(self.cited(r), [note, refs])
        r = row("c", title="4. Gap | Book", local_pdf=f"{RAG}/sources/my-book/ch04-gap.pdf")
        self.assertEqual(self.cited(r), [])

    def test_home_limits_the_search_and_prefers_notes(self):
        self.write("programming/notes/01.md", "arXiv 2301.12345\n")
        self.assertEqual(self.cited(row("2301.12345"), home="rag"), [])
        self.assertEqual(self.cited(row("2301.12345")), ["programming/notes/01.md"])
        note = self.write(f"{RAG}/notes/01.md", "arXiv 2301.12345\n")
        refs = self.write(f"{RAG}/references.md", "arXiv 2301.12345\n")
        self.assertEqual(self.cited(row("2301.12345"), home="rag"), [note, refs])


class Checks(TempRepo):
    def findings(self, rows):
        return check_ledger.check(rows)

    def test_flags_note_path_home_and_unledgered_pdf(self):
        self.write(f"{RAG}/sources/lost.pdf")
        self.write(f"{RAG}/sources/held.pdf")
        got = self.findings([row("a", status="queued", note="gone.md", pillar="nowhere", local_pdf=f"{RAG}/sources/held.pdf")])
        self.assertEqual(len(got["note-path"]), 1)
        self.assertEqual(len(got["home"]), 1)
        self.assertEqual(len(got["pdf-row"]), 1)
        self.assertIn("lost.pdf", got["pdf-row"][0])

    def test_a_copy_counts_as_having_a_row(self):
        path = self.write(f"{RAG}/sources/copy.pdf")
        self.assertEqual(self.findings([row("a", status="queued", copies=[path])])["pdf-row"], [])

    def test_uncited_integrated_row_unless_exempted(self):
        self.assertEqual(len(self.findings([row("a b c")])["no-citation"]), 1)
        self.assertEqual(self.findings([row("a b c", no_citation="a talk, no text")])["no-citation"], [])
        self.assertEqual(self.findings([row("a b c", status="queued")])["no-citation"], [])

    def test_cited_but_no_references_row(self):
        self.write(f"{RAG}/notes/01.md", "2301.12345\n")
        self.assertEqual(len(self.findings([row("2301.12345")])["no-references"]), 1)
        self.write(f"{RAG}/references.md", "2301.12345\n")
        self.assertEqual(self.findings([row("2301.12345")])["no-references"], [])

    def test_note_that_does_not_cite_its_row(self):
        note = self.write(f"{RAG}/notes/02.md")
        self.write(f"{RAG}/notes/01.md", "2301.12345\n")
        self.assertEqual(len(self.findings([row("2301.12345", note=note)])["note-no-cite"]), 1)

    def test_duplicates_leave_out_merged_rows(self):
        rows = [row("Same Title", status="queued"), row("x", title="same title!", status="queued"),
                row("doi:10.1/a", status="queued"), row("y", doi="10.1/A", status="queued")]
        got = self.findings(rows)
        self.assertEqual(len(got["dup-title"]), 1)
        self.assertEqual(len(got["dup-id"]), 1)
        rows[1]["merged_into"] = "Same Title"
        rows[3]["merged_into"] = "doi:10.1/a"
        got = self.findings(rows)
        self.assertEqual((got["dup-title"], got["dup-id"]), ([], []))


class Mark(TempRepo):
    def mark(self, rows, *keys, **kw):
        args = argparse.Namespace(**{"status": "integrated", "keys": list(keys), "home": None, "note": None,
                                     "why": None, "no_citation": None, **kw})
        with mock.patch.object(potw, "load_ledger", return_value=rows), mock.patch.object(potw, "save_ledger") as save, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            try:
                potw.cmd_mark(args)
                code = 0
            except SystemExit as e:
                code = e.code
        return code, save, err.getvalue()

    def test_sets_note_to_the_citing_file(self):
        note = self.write(f"{RAG}/notes/01.md", "2301.12345\n")
        r = row("2301.12345", status="downloaded")
        self.assertEqual(self.mark([r], "2301.12345")[0], 0)
        self.assertEqual((r["status"], r["note"]), ("integrated", note))

    def test_refuses_an_uncited_key_but_marks_the_cited_one(self):
        self.write(f"{RAG}/notes/01.md", "2301.12345\n")
        good, bad = row("2301.12345", status="downloaded"), row("2301.99999", status="downloaded")
        code, save, err = self.mark([good, bad], "2301.12345", "2301.99999")
        self.assertEqual(code, 1)
        self.assertEqual((good["status"], bad["status"]), ("integrated", "downloaded"))
        self.assertIn("2301.99999", err)
        save.assert_called_once()

    def test_a_citation_in_another_home_does_not_count(self):
        self.write("programming/notes/01.md", "2301.12345\n")
        r = row("2301.12345", status="downloaded")
        self.assertEqual(self.mark([r], "2301.12345")[0], 1)
        self.assertEqual(r["status"], "downloaded")

    def test_override_records_its_reason(self):
        r = row("2301.99999", status="downloaded")
        self.assertEqual(self.mark([r], "2301.99999", no_citation="a talk with no text")[0], 0)
        self.assertEqual((r["status"], r["no_citation"]), ("integrated", "a talk with no text"))

    def test_other_statuses_need_no_citation(self):
        r = row("2301.99999", status="downloaded")
        args = argparse.Namespace(status="skipped", keys=[r["key"]], home=None, note=None, why=None, no_citation=None)
        with mock.patch.object(potw, "load_ledger", return_value=[r]), mock.patch.object(potw, "save_ledger"), \
                contextlib.redirect_stdout(io.StringIO()):
            potw.cmd_mark(args)
        self.assertEqual(r["status"], "skipped")


class Scan(TempRepo):
    def scan(self, rows, **kw):
        args = argparse.Namespace(deep=False, offline=True, **kw)
        with mock.patch.object(potw, "load_ledger", return_value=rows), mock.patch.object(potw, "save_ledger"), \
                mock.patch.object(potw, "log"), mock.patch.object(potw, "arxiv_batch_meta") as meta:
            potw.cmd_scan(args)
        return meta

    def test_a_recorded_pdf_is_not_a_new_row(self):
        path = self.write(f"{RAG}/sources/smith-2020-title.pdf", "a")
        r = row("doi:10.1/a", local_pdf=path, have_pdf=True)
        rows = [r]
        self.scan(rows)
        self.assertEqual([x["key"] for x in rows], ["doi:10.1/a"])
        self.assertEqual(r["local_pdf"], path)
        self.assertTrue(r["sha1"])

    def test_a_recorded_copy_survives(self):
        a = self.write(f"{RAG}/sources/a.pdf", "a")
        b = self.write(f"{RAG}/sources/b.pdf", "b")
        r = row("doi:10.1/a", local_pdf=a, copies=[b], have_pdf=True)
        rows = [r]
        self.scan(rows)
        self.assertEqual((len(rows), r["copies"]), (1, [b]))

    def test_a_new_pdf_in_sources_is_filed_and_offline_stays_offline(self):
        path = self.write(f"{RAG}/sources/2301.12345v1.pdf", "a")
        rows = []
        meta = self.scan(rows)
        meta.assert_not_called()
        self.assertEqual((rows[0]["key"], rows[0]["status"], rows[0]["local_pdf"]), ("2301.12345", "filed", path))

    def test_same_bytes_elsewhere_become_a_copy(self):
        a = self.write(f"{RAG}/sources/a.pdf", "same")
        b = self.write(f"{RAG}/sources/b.pdf", "same")
        rows = []
        self.scan(rows)
        self.assertEqual(len(rows), 1)
        self.assertEqual({rows[0]["local_pdf"], *rows[0]["copies"]}, {a, b})

    def test_a_moved_file_stays_with_its_row(self):
        sha = hashlib.sha1(b"a").hexdigest()
        new = self.write(f"{RAG}/sources/moved.pdf", "a")
        r = row("doi:10.1/a", local_pdf=f"{RAG}/sources/gone.pdf", sha1=sha)
        rows = [r]
        self.scan(rows)
        self.assertEqual(len(rows), 1)
        self.assertEqual(r["local_pdf"], new)


class ChapterTier(unittest.TestCase):
    PDF = "ai-engineering/x/sources/{}/ch{:02d}-t.pdf"

    def chapter(self, book, n, status="queued"):
        return {"key": f"{book}{n}", "status": status, "pillar": "rag", "have_pdf": True, "local_pdf": self.PDF.format(book, n)}

    def test_book_in_progress_then_filed_then_new(self):
        rows = [self.chapter("a", 1, "integrated"), self.chapter("a", 2), self.chapter("b", 1, "filed"), self.chapter("c", 1)]
        self.assertEqual(potw.chapter_tiers(rows), {"a2": 1, "b1": 2, "c1": 3})

    def test_next_chapter_takes_the_lowest_tier_and_chapter(self):
        rows = [self.chapter("c", 1), self.chapter("a", 1, "integrated"), self.chapter("a", 3), self.chapter("a", 2)]
        self.assertEqual(potw.next_chapter(rows), ("a", "ch02", "a2"))
        self.assertEqual(potw.next_chapter(rows, exclude={"a2", "a3"}), ("c", "ch01", "c1"))
        self.assertIsNone(potw.next_chapter([]))

    def test_a_chapter_is_not_a_paper_and_the_inbox_waits(self):
        r = self.chapter("a", 1)
        self.assertTrue(potw.ready_for_chapter(r))
        self.assertFalse(potw.ready_for_papers(r))
        self.assertFalse(potw.ready_for_chapter({**r, "local_pdf": "scripts/papers/inbox/a/ch01-t.pdf"}))
        self.assertTrue(potw.ready_for_chapter({**r, "local_pdf": "x/sources/a/appendix-a-t.pdf"}))
        self.assertFalse(potw.ready_for_chapter({**r, "local_pdf": "x/sources/paper.pdf"}))


if __name__ == "__main__":
    unittest.main()
