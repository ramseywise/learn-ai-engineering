#!/usr/bin/env python3
"""Tests for the deck builder's level, beat and overview keys: make unit

The builder needs python-pptx and pyyaml, which the other script tests do not. Alone, this file runs with:
    uv run -q --with python-pptx --with pyyaml python -m unittest discover -s scripts -p test_build_deck.py
"""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import yaml
    from pptx import Presentation
except ImportError as missing:
    raise unittest.SkipTest(f"{missing}: make unit runs this file with the packages it needs")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "slides"))
import build_deck as bd
import deck_stamp as ds


def slide(title, **over):
    return {"layout": "statement", "title": title, "statement": title, **over}


def part(title, *slides, **over):
    return {"title": title, "summary": f"{title} summary", "slides": list(slides), **over}


def closing(*slides):
    return part("Wrap", *slides, agenda=False, divider=False)


def slide_text(s):
    return " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name) / "01-topic" / "slides"
        self.dir.mkdir(parents=True)
        self.spec = self.dir / "deck.yaml"
        bd.WARNINGS.clear()
        self.addCleanup(bd.WARNINGS.clear)

    def write(self, *parts, **deck):
        self.spec.write_text(yaml.safe_dump({"deck": {"title": "Topic", **deck}, "parts": list(parts)}), encoding="utf-8")

    def story(self, *parts):
        bd.check_story(list(parts), self.dir)
        return list(bd.WARNINGS)


class TestLevels(Base):
    def setUp(self):
        super().setUp()
        self.write(
            part("Mixed", slide("no level"), slide("is core", level="core"), slide("is practice", level="practice"),
                 slide("is deep", level="deep")),
            part("Advanced only", slide("advanced practice", level="practice"), slide("advanced deep", level="deep")),
            part("Third", slide("third core")),
            closing(slide("closing deep", level="deep")),
        )

    def texts(self, path):
        return [slide_text(s) for s in Presentation(path).slides]

    def has(self, texts, needle):
        return any(needle in t for t in texts)

    def test_core_keeps_core_and_absent_and_drops_the_rest(self):
        texts = self.texts(bd.build(self.spec, "core"))
        # Title; Mixed's divider and two slides; Third's divider and slide; the closing slide.
        self.assertEqual(len(texts), 7)
        for kept in ("no level", "is core", "third core"):
            self.assertTrue(self.has(texts, kept), kept)
        for dropped in ("is practice", "is deep", "advanced practice", "advanced deep"):
            self.assertFalse(self.has(texts, dropped), dropped)

    def test_closing_part_stays_whole_at_any_level(self):
        self.assertTrue(self.has(self.texts(bd.build(self.spec, "core")), "closing deep"))

    def test_practice_keeps_core_and_practice_only(self):
        texts = self.texts(bd.build(self.spec, "practice"))
        for kept in ("no level", "is practice", "advanced practice"):
            self.assertTrue(self.has(texts, kept), kept)
        for dropped in ("is deep", "advanced deep"):
            self.assertFalse(self.has(texts, dropped), dropped)

    def test_deep_keeps_everything(self):
        self.assertEqual(len(self.texts(bd.build(self.spec, "deep"))), len(self.texts(bd.build(self.spec))))

    def test_emptied_part_is_gone_from_agenda_and_dividers_and_the_rest_renumber(self):
        texts = self.texts(bd.build(self.spec, "core"))
        self.assertFalse(self.has(texts, "Advanced only"))
        self.assertIn("Part 2: Third", texts[0])
        self.assertTrue(self.has(texts, "PART 2 Third"))
        self.assertFalse(self.has(texts, "PART 3"))

    def test_divider_stays_and_lists_only_kept_slides(self):
        divider = self.texts(bd.build(self.spec, "core"))[1]
        self.assertIn("PART 1", divider)
        self.assertIn("no level", divider)
        self.assertNotIn("is deep", divider)

    def test_filtered_output_name_leaves_the_full_deck_alone(self):
        full = bd.build(self.spec)
        self.assertEqual(full.name, "01-topic.pptx")
        before = full.read_bytes()
        for level in bd.LEVELS:
            self.assertEqual(bd.build(self.spec, level).name, f"01-topic-{level}.pptx")
        self.assertEqual(full.read_bytes(), before)

    def test_filtered_output_name_follows_deck_output(self):
        self.write(part("P", slide("s")), output="my-deck.pptx")
        self.assertEqual(bd.build(self.spec, "core").name, "my-deck-core.pptx")

    def test_filtered_file_is_not_the_deck_to_deck_check(self):
        bd.build(self.spec, "core")
        self.assertEqual(ds.state(self.spec), "no pptx")
        bd.build(self.spec)
        self.assertEqual(ds.state(self.spec), "current")
        (self.dir / "01-topic-core.pptx").write_bytes(b"not a zip")  # never opened
        self.assertEqual(ds.state(self.spec), "current")

    def test_build_without_level_draws_every_part(self):
        self.write(part("Empty"), part("P", slide("s", level="deep")))
        texts = self.texts(bd.build(self.spec))
        self.assertIn("Part 1: Empty", texts[0])
        self.assertIn("Part 2: P", texts[0])


class TestFilterParts(unittest.TestCase):
    def test_does_not_change_the_parts_it_is_given(self):
        parts = [part("P", slide("a"), slide("b", level="deep"))]
        kept = bd.filter_parts(parts, "core")
        self.assertEqual([s["title"] for s in kept[0]["slides"]], ["a"])
        self.assertEqual(len(parts[0]["slides"]), 2)


class TestStoryAgainstFullDeck(Base):
    def test_filtering_adds_no_coverage_or_story_warnings(self):
        notes = self.dir.parent / "notes"
        notes.mkdir()
        (notes / "01-a.md").write_text("# a\n")
        (notes / "02-b.md").write_text("# b\n")
        self.write(part("P", slide("a", source="notes/01-a.md"), slide("b", source="notes/02-b.md", level="deep")))
        bd.build(self.spec)
        full = list(bd.WARNINGS)
        bd.WARNINGS.clear()
        bd.build(self.spec, "core")
        self.assertEqual(bd.WARNINGS, full)
        self.assertFalse([w for w in bd.WARNINGS if w.startswith("coverage")])


class TestUnknownValues(Base):
    def assert_stops(self, needle, level=None):
        with self.assertRaises(SystemExit) as stop:
            bd.build(self.spec, level)
        self.assertIn(needle, str(stop.exception))
        self.assertIn("the bad slide", str(stop.exception))
        self.assertFalse(list(self.dir.glob("*.pptx")))

    def test_unknown_level(self):
        self.write(part("P", slide("the bad slide", level="expert")))
        self.assert_stops("unknown level 'expert'")

    def test_unknown_beat(self):
        self.write(part("P", slide("the bad slide", beat="setup")))
        self.assert_stops("unknown beat 'setup'")

    def test_empty_level_is_not_absent(self):
        self.write(part("P", slide("the bad slide", level=None)))
        self.assert_stops("unknown level")

    def test_a_filtered_build_checks_slides_it_would_drop_and_closing_parts(self):
        self.write(part("P", slide("ok")), closing(slide("the bad slide", level="expert")))
        self.assert_stops("unknown level", level="core")

    def test_the_flag_rejects_an_unknown_level(self):
        self.write(part("P", slide("ok")))
        argv = ["build_deck.py", str(self.spec), "--level", "expert"]
        with self.assertRaises(SystemExit), mock.patch.object(sys, "argv", argv), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            bd.main()
        self.assertIn("invalid choice", err.getvalue())


class TestBeats(Base):
    @staticmethod
    def beats(title="Part", **over):
        return part(title, slide("f", beat="fundamentals"), slide("pr", beat="practice"), slide("pi", beat="pitfalls"), **over)

    @staticmethod
    def beat_warnings(warnings):
        return [w for w in warnings if "beat" in w or "overview" in w]

    def test_deck_with_no_beat_gets_no_new_warnings(self):
        warnings = self.story(part("Thin", slide("a")), part("Other", slide("b")), closing(slide("c")))
        self.assertEqual(self.beat_warnings(warnings), [])

    def test_complete_deck_is_clean(self):
        warnings = self.story(self.beats("Intro", overview=True), self.beats())
        self.assertEqual(self.beat_warnings(warnings), [])

    def test_part_missing_beats_warns_and_names_them(self):
        warnings = self.story(self.beats("Intro", overview=True), part("Thin", slide("a", beat="fundamentals")))
        self.assertEqual(self.beat_warnings(warnings), ["part 'Thin': no slide with beat: practice, pitfalls"])

    def test_other_beats_do_not_count(self):
        warnings = self.story(self.beats("Intro", overview=True), part("Thin", slide("a", beat="problem"), slide("b", beat="wrap")))
        self.assertEqual(self.beat_warnings(warnings), ["part 'Thin': no slide with beat: fundamentals, practice, pitfalls"])

    def test_one_slide_with_beat_turns_the_check_on_even_in_a_closing_part(self):
        warnings = self.story(part("Thin", slide("a")), closing(slide("c", beat="wrap")))
        self.assertIn("part 'Thin': no slide with beat: fundamentals, practice, pitfalls", warnings)

    def test_closing_part_is_not_checked(self):
        warnings = self.story(self.beats("Intro", overview=True), closing(slide("c", beat="wrap")))
        self.assertEqual(self.beat_warnings(warnings), [])

    def test_first_agenda_part_must_be_overview(self):
        warnings = self.story(self.beats("Intro"), self.beats())
        self.assertEqual(self.beat_warnings(warnings), ["part 'Intro': the first agenda part should be marked overview: true"])

    def test_closing_part_first_does_not_count_as_first_agenda_part(self):
        warnings = self.story(closing(slide("c", beat="wrap")), self.beats("Intro", overview=True))
        self.assertEqual(self.beat_warnings(warnings), [])

    def test_overview_part_owes_no_code_but_other_parts_do(self):
        warnings = self.story(part("Intro", slide("a"), overview=True), part("Body", slide("b")))
        code = [w for w in warnings if "no code" in w]
        self.assertEqual(len(code), 1)
        self.assertIn("Body", code[0])

    def test_overview_part_is_exempt_from_beats(self):
        warnings = self.story(part("Intro", slide("a", beat="problem"), overview=True), self.beats())
        self.assertEqual(self.beat_warnings(warnings), [])

    def test_overview_on_a_later_part_exempts_it_but_the_first_still_warns(self):
        warnings = self.story(self.beats("Intro"), part("Later", slide("a", beat="problem"), overview=True))
        self.assertEqual(self.beat_warnings(warnings), ["part 'Intro': the first agenda part should be marked overview: true"])

    def test_overview_without_beat_in_the_deck_is_silent(self):
        self.assertEqual(self.beat_warnings(self.story(part("Intro", slide("a"), overview=True))), [])

    def test_overview_part_is_numbered_with_a_divider(self):
        self.write(part("Intro", slide("a"), overview=True), part("Next", slide("b")))
        slides = [slide_text(s) for s in Presentation(bd.build(self.spec)).slides]
        self.assertIn("Part 1: Intro", slides[0])
        self.assertIn("PART 1", slides[1])
        self.assertTrue(any("PART 2" in t for t in slides))


class TestMakeLevel(unittest.TestCase):
    def test_make_passes_level_through(self):
        out = subprocess.run(["make", "-n", "slides", "PILLAR=a/b", "LEVEL=core"], cwd=HERE.parent, capture_output=True, text=True)
        self.assertIn("--level core", out.stdout)
        out = subprocess.run(["make", "-n", "slides", "PILLAR=a/b"], cwd=HERE.parent, capture_output=True, text=True)
        self.assertNotIn("--level", out.stdout)



class LectureBase(unittest.TestCase):
    """A one-pillar curriculum in a temp folder, with deck_graph pointed at it."""

    PILLAR = "data-science/01-topic"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        patcher = mock.patch.object(bd.deck_graph, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        bd.WARNINGS.clear()
        self.addCleanup(bd.WARNINGS.clear)
        self.pillar = self.root / self.PILLAR
        (self.pillar / "notes").mkdir(parents=True)
        (self.pillar / "slides" / "lectures").mkdir(parents=True)
        self.note("01-a", "# 01 — First note\n\n## Alpha\n\n## Beta\n\n```python\n## not a heading\n```\n\n## Practice\n\n## Next\n")
        self.note("02-b", "# 02 — Second note\n\n## Gamma\n")
        (self.pillar / "README.md").write_text(
            "# Topic\n\n## Syllabus\n\n[two](notes/02-b.md) then [one](notes/01-a.md)\n\n## Later\n", encoding="utf-8")

    def note(self, stem, text):
        (self.pillar / "notes" / f"{stem}.md").write_text(text, encoding="utf-8")

    def path(self, stem):
        return f"{self.PILLAR}/notes/{stem}.md"

    def lecture(self, stem="01-a", **block):
        spec = self.pillar / "slides" / "lectures" / f"{stem}.yaml"
        data = {"deck": {"title": stem}, "lecture": {"covers": [self.path(stem)], **block}}
        return bd.deck_graph.lecture_from(spec, data, self.root)

    def warnings(self, slides, lecture):
        bd.check_lecture([part("Only", *slides)], lecture, self.root)
        return " | ".join(bd.WARNINGS)

    def full(self, *sections):
        return [slide(f"s{i}", section=s) for i, s in enumerate(sections)]


class LectureSizeTest(LectureBase):
    def test_a_thin_lecture_is_too_condensed(self):
        self.assertIn("too condensed: 20 is the least", self.warnings(self.full("Alpha", "Beta"), self.lecture()))

    def test_a_long_note_owes_more_slides(self):
        self.note("01-a", "# Note\n\n## Alpha\n\n" + "word " * 6000)
        self.assertIn("40 is the least", self.warnings(self.full("Alpha"), self.lecture()))

    def test_the_floor_stops_at_the_maximum(self):
        self.note("01-a", "# Note\n\n## Alpha\n\n" + "word " * 20000)
        self.assertIn("60 is the least", self.warnings(self.full("Alpha"), self.lecture()))

    def test_an_overview_owes_fewer_slides_and_no_code_or_beats(self):
        spec = self.lecture(overview=True, covers=[f"{self.PILLAR}/README.md"])
        found = self.warnings([slide("s")], spec)
        self.assertIn("15 is the least", found)
        self.assertNotIn("no code", found)
        self.assertNotIn("no slide with beat", found)

    def test_enough_slides_pass_the_floor(self):
        slides = self.full(*(["Alpha"] * 10 + ["Beta"] * 10))
        self.assertNotIn("too condensed", self.warnings(slides, self.lecture()))


class LectureSectionTest(LectureBase):
    def test_a_section_with_no_slide_is_named(self):
        self.assertIn("note section 'Beta' has no slide", self.warnings(self.full("Alpha"), self.lecture()))

    def test_omits_excuses_a_section(self):
        self.assertNotIn("'Beta'", self.warnings(self.full("Alpha"), self.lecture(omits=["Beta"])))

    def test_back_matter_and_fenced_comments_are_not_owed(self):
        found = self.warnings(self.full("Alpha", "Beta"), self.lecture())
        for section in ("Practice", "Next", "not a heading"):
            self.assertNotIn(f"'{section}'", found)

    def test_a_section_the_note_lacks_is_named(self):
        self.assertIn("section 'Delta' is not a heading", self.warnings(self.full("Alpha", "Beta", "Delta"), self.lecture()))

    def test_an_omit_the_note_lacks_is_named(self):
        self.assertIn("omits 'Delta'", self.warnings(self.full("Alpha", "Beta"), self.lecture(omits=["Delta"])))

    def test_sections_against_the_note_order_warn(self):
        self.assertIn("'Alpha' comes after 'Beta'", self.warnings(self.full("Beta", "Alpha"), self.lecture()))


class LectureSpineTest(LectureBase):
    def test_the_spine_is_checked_across_the_lecture_not_each_part(self):
        parts = [part("One", slide("s1", beat="fundamentals", section="Alpha")),
                 part("Two", {"layout": "flow", "title": "s2", "steps": ["a"], "code": "x", "beat": "practice", "section": "Beta"}),
                 part("Three", slide("s3", beat="pitfalls", section="Beta"))]
        bd.check_lecture(parts, self.lecture(), self.root)
        found = " | ".join(bd.WARNINGS)
        for absent in ("no slide with beat", "no image or flow", "no code", "should open"):
            self.assertNotIn(absent, found)

    def test_a_missing_beat_is_named(self):
        self.assertIn("no slide with beat: practice, pitfalls",
                      self.warnings([slide("s", beat="fundamentals", section="Alpha")], self.lecture()))

    def test_a_lecture_must_open_on_a_problem(self):
        self.assertIn("should open", self.warnings([{"layout": "bullets", "title": "t", "bullets": ["b"]}], self.lecture()))


class LectureBuildTest(LectureBase):
    def spec(self, stem="01-a", deck=None, **block):
        spec = self.pillar / "slides" / "lectures" / f"{stem}.yaml"
        spec.write_text(yaml.safe_dump({
            "deck": {"title": stem, "subtitle": "What this teaches", **(deck or {})},
            "lecture": {"covers": [self.path(stem)], **block},
            "parts": [part("Only", slide("Hello", section="Alpha"))],
        }), encoding="utf-8")
        return spec

    def build(self, spec):
        with contextlib.redirect_stdout(io.StringIO()):
            return bd.build(spec)

    def test_output_defaults_to_the_spec_stem_and_the_stamp_finds_it(self):
        spec = self.spec()
        out = self.build(spec)
        self.assertEqual(out, spec.parent / "01-a.pptx")
        self.assertEqual(ds.pptx_for(spec), out)
        self.assertEqual(ds.state(spec), "current")

    def test_framing_slides_come_first_and_last_and_follow_the_syllabus(self):
        slides = list(Presentation(self.build(self.spec(requires=[self.path("02-b")]))).slides)
        opening, closing_slide = slide_text(slides[1]), slide_text(slides[-1])
        self.assertIn("Where this lecture sits", opening)
        self.assertIn("Lecture 3 of 3", opening)   # the README reads 02 first, and the overview is lecture 1
        self.assertIn("Where this leads", closing_slide)

    def test_an_edge_names_the_lecture_once_it_exists_and_the_note_until_then(self):
        target = self.path("02-b")
        before = slide_text(list(Presentation(self.build(self.spec(next=[target]))).slides)[-1])
        self.assertIn("Second note", before)
        self.assertNotIn("notes only", before)
        self.spec("02-b", deck={"title": "Second lecture"})
        after = slide_text(list(Presentation(self.build(self.spec(next=[target]))).slides)[-1])
        self.assertIn("Second lecture", after)

    def test_the_framing_slides_are_not_judged_by_the_story(self):
        self.build(self.spec())
        self.assertNotIn("Where this", " | ".join(bd.WARNINGS))


class DeckGraphTest(LectureBase):
    def problems(self, *lectures):
        return " | ".join(bd.deck_graph.problems(list(lectures), self.root))

    def test_a_clean_graph_has_no_problems(self):
        self.assertEqual(self.problems(self.lecture(next=[self.path("02-b")])), "")

    def test_an_edge_to_a_note_with_no_lecture_is_fine(self):
        self.assertEqual(self.problems(self.lecture(requires=[self.path("02-b")])), "")

    def test_a_broken_edge_is_named(self):
        self.assertIn("next data-science/01-topic/notes/99.md", self.problems(self.lecture(next=[self.path("99")])))

    def test_covering_a_missing_note_is_named(self):
        self.assertIn("which does not exist", self.problems(self.lecture("99")))

    def test_a_note_claimed_twice_is_named(self):
        self.assertIn("already covered", self.problems(self.lecture(), self.lecture("01-a-again", covers=[self.path("01-a")])))

    def test_a_requires_cycle_is_named(self):
        one = self.lecture(requires=[self.path("02-b")])
        two = self.lecture("02-b", requires=[self.path("01-a")])
        self.assertIn("requires cycle", self.problems(one, two))

    def test_syllabus_order_follows_the_readme_not_the_file_names(self):
        self.assertEqual(bd.deck_graph.syllabus_order(self.PILLAR, self.root), [self.path("02-b"), self.path("01-a")])


if __name__ == "__main__":
    unittest.main()
