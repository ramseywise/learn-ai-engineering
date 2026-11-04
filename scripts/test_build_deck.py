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


if __name__ == "__main__":
    unittest.main()
