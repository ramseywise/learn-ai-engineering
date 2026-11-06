#!/usr/bin/env python3
"""Tests for the chapter checker, link checker, crosswalk and deck stamp: python3 scripts/test_check_chapters.py"""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "practice"))
sys.path.insert(0, str(HERE / "slides"))
import check_chapters as cc
import crosswalk as cw
import deck_stamp as ds

NOTE = Path(__file__)  # A note path whose folder exists; the source tests only resolve paths against it


def note_text(origin="synthesis", sources=("https://example.com/a",), body="Body text.\n"):
    listed = "".join(f"  - {s}\n" for s in sources)
    return f"---\ntitle: T\norigin: {origin}\nsources:\n{listed}---\n{body}"


def problems(**over):
    return cc.metadata_problems(note_text(**over), NOTE)


class Origin(unittest.TestCase):
    def test_each_legal_value_passes(self):
        for origin in cc.LEGAL_ORIGINS:
            self.assertEqual(problems(origin=origin), [], origin)

    def test_illegal_value_fails(self):
        self.assertRegex(problems(origin="notes")[0], "origin 'notes' is not one of")

    def test_missing_origin_fails(self):
        self.assertIn("no origin in frontmatter", cc.metadata_problems("---\ntitle: T\n---\nBody\n", NOTE))


class LanguageSubset(unittest.TestCase):
    FULL = "# T\n\nShort.\n\n## Pitfalls\n\n- x\n\n## Try it\n\n[lab](../practice/a.ts)\n\n## Next\n\n[n](02.md)\n"

    def write(self, rel, body):
        root = Path(tempfile.mkdtemp())
        path = root / rel
        path.parent.mkdir(parents=True)
        path.write_text(note_text(body=body), encoding="utf-8")
        return path

    def test_scope(self):
        self.assertTrue(cc.in_language_subset(Path("programming/typescript/notes/04-generics.md")))
        self.assertTrue(cc.in_language_subset(Path("programming/sql/notes/10-capstone-murder-mystery.md")))
        self.assertFalse(cc.in_language_subset(Path("programming/sql/notes/09-sql-from-python.md")))
        self.assertFalse(cc.in_language_subset(Path("programming/software-design/notes/01-readable-code.md")))

    def test_short_note_with_the_subset_passes(self):
        path = self.write("programming/typescript/notes/01-a.md", self.FULL)
        self.assertEqual(cc.check(path), [])

    def test_missing_sections_fail(self):
        path = self.write("programming/typescript/notes/01-a.md", "# T\n\nShort, see practice/a.ts.\n")
        self.assertEqual(cc.check(path), ["no 'Pitfalls' section", "no 'Try it' section", "no 'Next' section"])

    def test_try_it_needed_only_where_a_lab_exists(self):
        body = "# T\n\nShort.\n\n## Pitfalls\n\n- x\n\n## Next\n\n[n](02.md)\n"
        self.assertEqual(cc.check(self.write("programming/sql/notes/10-capstone.md", body)), [])

    def test_lab_named_only_in_code_fence_does_not_count(self):
        body = "# T\n\n```\npractice/a.ts\n```\n\n## Pitfalls\n\n- x\n\n## Next\n\n[n](02.md)\n"
        self.assertEqual(cc.check(self.write("programming/typescript/notes/02-a.md", body)), [])

    def test_order_is_enforced(self):
        body = "# T\n\nSee practice/a.ts.\n\n## Next\n\nx\n\n## Try it\n\ny\n\n## Pitfalls\n\nz\n"
        problems = cc.check(self.write("programming/typescript/notes/01-a.md", body))
        self.assertEqual(problems, ["Pitfalls, Try it, Next are out of order"])

    def test_next_in_another_heading_is_not_the_next_section(self):
        body = "# T\n\n## What to do next\n\nx\n\n## Pitfalls\n\ny\n\n## Next\n\nz\n"
        self.assertEqual(cc.check(self.write("programming/typescript/notes/09-a.md", body)), [])

    def test_other_programming_notes_keep_the_full_standard(self):
        path = self.write("programming/software-design/notes/01-a.md", self.FULL)
        self.assertTrue(any("under 1500" in p for p in cc.check(path)))


class Sources(unittest.TestCase):
    def test_url_doi_and_layout_citation_pass(self):
        for entry in ("https://arxiv.org/abs/2401.00001", "10.1016/0196-8858(85)90002-8",
                      "Huyen, AI Engineering (O'Reilly, 2025), ch. 6"):
            self.assertIsNone(cc.source_problem(entry, NOTE), entry)

    def test_repo_path_passes_only_if_it_exists(self):
        self.assertIsNone(cc.source_problem("scripts/check_chapters.py", NOTE))
        self.assertRegex(cc.source_problem("scripts/not_there.py", NOTE), "does not exist")

    def test_local_pdf_fails_even_when_the_file_is_named_with_a_year(self):
        self.assertRegex(cc.source_problem("sources/huyen-2025.pdf", NOTE), "local PDF")

    def test_a_url_ending_in_pdf_is_a_url(self):
        self.assertIsNone(cc.source_problem("https://example.com/paper.pdf", NOTE))

    def test_bare_words_fail(self):
        self.assertRegex(cc.source_problem("my own notes", NOTE), "not a URL, DOI")

    def test_undated_citation_fails(self):
        self.assertRegex(cc.source_problem("Huyen, AI Engineering", NOTE), "not a URL, DOI")

    def test_unquoted_colon_is_not_a_plain_string(self):
        self.assertRegex(cc.source_problem("Huyen: AI Engineering (2025), ch. 6", NOTE), "quote it")

    def test_quoted_colon_passes(self):
        self.assertIsNone(cc.source_problem('"Huyen: AI Engineering, 2025"', NOTE))

    def test_comment_lines_are_not_entries(self):
        text = "---\norigin: synthesis\nsources:\n  # my own work note\n  - https://example.com/a\n---\nBody\n"
        self.assertEqual(cc.metadata_problems(text, NOTE), [])

    def test_a_bad_entry_fails_the_note(self):
        self.assertTrue(any("local PDF" in p for p in problems(sources=("sources/a.pdf",))))


class PersonalPaths(unittest.TestCase):
    def test_home_paths_fail_in_prose(self):
        for path in ("~/.claude/skills", "~/workspace/x", "/Users/someone/x"):
            found = problems(body=f"See {path}.\n")
            self.assertTrue(any("personal path" in p for p in found), path)

    def test_code_fences_are_no_shelter(self):
        found = problems(body="```bash\ncat ~/.claude/x\n```\n")
        self.assertTrue(any("personal path" in p for p in found))

    def test_frontmatter_is_no_shelter(self):
        found = problems(sources=("/Users/someone/paper",))
        self.assertTrue(any("personal path" in p for p in found))


class Headings(unittest.TestCase):
    def test_exact_heading_passes(self):
        self.assertEqual(problems(body="## Interview checklist\n"), [])

    def test_variants_fail(self):
        for heading in ("## Interview questions", "## Interview Checklist", "### Interview prep"):
            found = problems(body=f"{heading}\n")
            self.assertTrue(any("must be '## Interview checklist'" in p for p in found), heading)

    def test_right_words_at_the_wrong_level_fail(self):
        self.assertTrue(any("must be an H2" in p for p in problems(body="### Interview checklist\n")))

    def test_a_heading_inside_a_fence_is_ignored(self):
        self.assertEqual(problems(body="```md\n## Interview questions\n```\n"), [])


class BodyCitations(unittest.TestCase):
    def test_arxiv_link_missing_from_sources_fails(self):
        found = problems(body="See [p](https://arxiv.org/abs/2401.00001).\n")
        self.assertTrue(any("2401.00001" in p and "not in frontmatter" in p for p in found))

    def test_doi_with_parentheses_missing_from_sources_fails(self):
        found = problems(body="See https://doi.org/10.1016/0196-8858(85)90002-8 for it.\n")
        self.assertTrue(any("10.1016/0196-8858(85)90002-8" in p for p in found), found)

    def test_listed_paper_passes_in_another_url_form(self):
        found = problems(sources=("https://arxiv.org/abs/2401.00001",),
                         body="See [p](https://arxiv.org/pdf/2401.00001).\n")
        self.assertEqual(found, [])

    def test_a_paper_only_in_a_code_fence_is_not_a_citation(self):
        self.assertEqual(problems(body="```\nhttps://arxiv.org/abs/2401.00001\n```\n"), [])


class Scope(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.note = Path(tmp.name) / "note.md"

    def test_skeleton_is_still_metadata_checked(self):
        self.note.write_text("---\nstatus: skeleton\norigin: notes\n---\nBody\n", encoding="utf-8")
        found = cc.check(self.note)
        self.assertIn("skeleton (status: skeleton)", found)
        self.assertTrue(any("origin 'notes'" in p for p in found))

    def test_metadata_only_skips_the_chapter_shape(self):
        self.note.write_text(note_text(), encoding="utf-8")
        self.assertEqual(cc.check(self.note, metadata_only=True), [])
        self.assertTrue(any("under" in p for p in cc.check(self.note)))

    def test_metadata_only_still_fails_bad_metadata(self):
        self.note.write_text(note_text(origin="notes"), encoding="utf-8")
        self.assertTrue(cc.check(self.note, metadata_only=True))


class Advisories(unittest.TestCase):
    def test_row_floor_is_reported_and_not_a_shortfall(self):
        body = "## Interview checklist\n\n| Q | A |\n|---|---|\n| a | b |\n\n" + "word " * 1600
        text = note_text(body=body)
        self.assertTrue(any(a.startswith("checklist floor: 1 rows") for a in cc.advisories(text)))
        self.assertEqual(cc.metadata_problems(text, NOTE), [])

    def test_row_count_ignores_header_and_separator(self):
        self.assertEqual(cc.checklist_rows("## Interview checklist\n\n| Q | A |\n|---|---|\n| a | b |\n| c | d |\n"), 2)

    def test_uncited_source_and_unlisted_link_are_reported(self):
        found = cc.advisories(note_text(body="See https://example.com/b.\n"))
        self.assertIn("body link not in sources: https://example.com/b", found)
        self.assertIn("source never cited in the body: https://example.com/a", found)


class LinkCheck(unittest.TestCase):
    """link_check.py runs on import against the current directory, so it is run as a process in a temp git repo."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.dir, check=True)
        (self.dir / "there.md").write_text("# There\n", encoding="utf-8")

    def run_check(self, text, name="note.md"):
        (self.dir / name).write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(HERE / "link_check.py")], cwd=self.dir,
                              capture_output=True, text=True)

    def test_good_link_passes(self):
        out = self.run_check("[a](there.md)\n")
        self.assertEqual((out.returncode, out.stdout.strip()), (0, "All links OK"))

    def test_broken_link_fails_and_names_the_file(self):
        out = self.run_check("[a](gone.md)\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("BROKEN: ./note.md -> gone.md", out.stdout)

    def test_anchor_checks_the_file(self):
        self.assertEqual(self.run_check("[a](there.md#there)\n").returncode, 0)
        out = self.run_check("[a](there.md#section)\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("BROKEN ANCHOR: ./note.md -> there.md#section", out.stdout)
        self.assertEqual(self.run_check("[a](gone.md#section)\n").returncode, 1)

    def test_fenced_and_external_links_are_skipped(self):
        out = self.run_check("[a](https://example.com/x)\n\n```\n[b](gone.md)\n```\n")
        self.assertEqual(out.returncode, 0)

    def test_escaped_path_is_decoded(self):
        (self.dir / "two words.md").write_text("x\n", encoding="utf-8")
        self.assertEqual(self.run_check("[a](two%20words.md)\n").returncode, 0)

    def test_ignored_file_with_a_broken_link_is_not_read(self):
        (self.dir / ".gitignore").write_text("private.md\n", encoding="utf-8")
        self.assertEqual(self.run_check("[a](gone.md)\n", name="private.md").returncode, 0)


class Crosswalk(unittest.TestCase):
    def test_units_inline_and_block(self):
        self.assertEqual(cw.units_of("---\nunits: [a/b, c/d.md]\n---\nx\n"), ["a/b", "c/d.md"])
        self.assertEqual(cw.units_of("---\nunits:\n  - a/b\n  - c/d.md\n---\nx\n"), ["a/b", "c/d.md"])

    def test_no_frontmatter_no_units(self):
        self.assertEqual(cw.units_of("units: [a/b]\n"), [])

    def test_link_targets_skip_fences_external_and_anchors(self):
        text = "[a](x.md#s) [b](https://e.com) [c](#top) [d](two%20w.md)\n```\n[e](fenced.md)\n```\n"
        self.assertEqual(cw.link_targets(text), ["x.md", "two w.md"])

    def test_label_names_the_round(self):
        self.assertEqual(cw.label("practice/interviewing/rounds/case-study/README.md"), "case-study")
        self.assertEqual(cw.label("practice/interviewing/rounds/case-study/examples/aie-track/x.md"), "case-study/x")
        self.assertEqual(cw.label("programming/drills/python/x.md"), "x")

    def test_validate_missing_unit(self):
        found, units = cw.validate({"practice/g.md": "---\nunits: [no/such/unit]\n---\n"}, {"practice/g.md"})
        self.assertEqual(found, ["practice/g.md: unit does not exist: no/such/unit"])
        self.assertEqual(units, {"practice/g.md": ["no/such/unit"]})

    def test_validate_unit_that_exists(self):
        found, _ = cw.validate({"practice/g.md": "---\nunits: [scripts/]\n---\n"}, {"practice/g.md"})
        self.assertEqual(found, [])

    def test_validate_broken_and_leaving_links(self):
        found, _ = cw.validate({"practice/g.md": "[a](../scripts/nope.py)\n[b](../../../outside.md)\n"}, {"practice/g.md"})
        self.assertIn("practice/g.md: broken link: ../scripts/nope.py", found)
        self.assertIn("practice/g.md: link leaves the repo: ../../../outside.md", found)

    def test_validate_link_to_unpublished_practice_file(self):
        found, _ = cw.validate({"practice/g.md": "[a](private.md)\n"}, {"practice/g.md"})
        self.assertEqual(found, ["practice/g.md: link to unpublished or missing file: private.md"])

    def test_validate_skips_links_in_upstream_material_but_not_its_units(self):
        rel = cw.SKIP_LINKS + "x.md"
        found, _ = cw.validate({rel: "---\nunits: [no/such]\n---\n[a](gone.md)\n"}, {rel})
        self.assertEqual(found, [f"{rel}: unit does not exist: no/such"])


class DeckStamp(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.spec = Path(tmp.name) / "01-topic" / "slides" / "deck.yaml"
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text("deck:\n  title: T\nparts: []\n", encoding="utf-8")
        self.pptx = self.spec.parent / "01-topic.pptx"

    def build(self, keywords):
        core = f"<cp:coreProperties><cp:keywords>{keywords}</cp:keywords></cp:coreProperties>"
        with zipfile.ZipFile(self.pptx, "w") as archive:
            archive.writestr("docProps/core.xml", core)

    def test_no_pptx(self):
        self.assertEqual(ds.state(self.spec), "no pptx")

    def test_stamped_with_this_yaml_is_current(self):
        self.build(ds.stamp_value(self.spec))
        self.assertEqual(ds.state(self.spec), "current")

    def test_changed_yaml_is_stale_and_fails(self):
        self.build(ds.stamp_value(self.spec))
        self.spec.write_text("deck:\n  title: Changed\nparts: []\n", encoding="utf-8")
        self.assertEqual(ds.state(self.spec), "stale")
        with mock.patch("builtins.print"):
            self.assertEqual(ds.check([self.spec]), 1)

    def test_touching_the_yaml_is_not_stale(self):
        self.build(ds.stamp_value(self.spec))
        self.spec.write_bytes(self.spec.read_bytes())
        self.assertEqual(ds.state(self.spec), "current")

    def test_pptx_from_before_stamping_is_reported_and_not_failed(self):
        self.build("")
        self.assertEqual(ds.state(self.spec), "unstamped")
        with mock.patch("builtins.print"):
            self.assertEqual(ds.check([self.spec]), 0)

    def test_deck_output_is_honoured(self):
        self.spec.write_text("deck:\n  title: T\n  output: other.pptx\nparts: []\n", encoding="utf-8")
        self.assertEqual(ds.pptx_for(self.spec).name, "other.pptx")


if __name__ == "__main__":
    unittest.main()
