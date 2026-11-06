#!/usr/bin/env python3
"""Tests for curriculum_map.py on a small invented repo: python3 scripts/test_curriculum_map.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import curriculum_map as cm


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


class CurriculumMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.addCleanup(self.tmp.cleanup)
        p = "data-science/01-a"
        write(self.root, f"{p}/README.md", "**Builds on**\n\n[one](notes/01-one.md) [two](notes/02-two.md)\n")
        write(self.root, f"{p}/notes/01-one.md", "---\nstatus: skeleton\n---\n# One\n\n## Attention\n\nbody\n\n## Next\n\n[wrong](03-four.md)\n")
        write(self.root, f"{p}/notes/02-two.md", "# Two\n\nSee [one](01-one.md).\n\n```\n[fenced](05-nope.md)\n```\n\n## Next\n\n[gone](09-gone.md)\n")
        write(self.root, f"{p}/notes/04-unlisted.md", "# Four\n\n[one](01-one.md)\n")
        write(self.root, f"{p}/slides/deck.yaml", "slides:\n  - source: notes/01-one.md\n  - source: notes/99-old.md\n")
        write(self.root, "data-science/01-a/practice/notes/ignored.md", "# Not a note\n")
        write(self.root, "programming/sql/notes/01-select.md", "# Select\n")
        write(self.root, "programming/sql/README.md", "[s](notes/01-select.md)\n")
        write(self.root, "data-science/02-b/README.md", "No tables here. [t](notes/01-t.md)\n")
        write(self.root, "data-science/02-b/notes/01-t.md", "# T\n")
        write(self.root, "scripts/papers/ledger.jsonl", json.dumps({"note": "data-science/01-a/notes/77-moved.md"}) + "\n" + json.dumps({"note": None}) + "\n")
        self.map = cm.build(self.root)

    def kinds(self, kind):
        return [i for i in self.map["issues"] if i["kind"] == kind]

    def test_finds_notes_and_skips_practice(self):
        self.assertEqual(len(self.map["notes"]), 5)
        self.assertNotIn("data-science/01-a/practice/notes/ignored.md", self.map["notes"])

    def test_front_matter_and_title(self):
        note = self.map["notes"]["data-science/01-a/notes/01-one.md"]
        self.assertEqual(note["status"], "skeleton")
        self.assertEqual(note["title"], "One")

    def test_inbound_ignores_code_fences(self):
        note = self.map["notes"]["data-science/01-a/notes/01-one.md"]
        self.assertEqual(note["inbound"], ["data-science/01-a/notes/02-two.md", "data-science/01-a/notes/04-unlisted.md"])
        self.assertNotIn("data-science/01-a/notes/05-nope.md", self.map["notes"]["data-science/01-a/notes/02-two.md"]["links"])

    def test_next_problems(self):
        self.assertEqual({i["path"] for i in self.kinds("next_out_of_order")},
                         {"data-science/01-a/notes/01-one.md", "data-science/01-a/notes/02-two.md"})
        self.assertEqual({i["path"] for i in self.kinds("missing_next_target")},
                         {"data-science/01-a/notes/01-one.md", "data-science/01-a/notes/02-two.md"})

    def test_next_may_follow_the_readme_order(self):
        p = "data-science/03-c"
        write(self.root, f"{p}/README.md", "[1](notes/01-a.md) [3](notes/03-c.md) [2](notes/02-b.md) [4](notes/04-d.md)\n"
                                           "Later mention: [1](notes/01-a.md)\n")
        write(self.root, f"{p}/notes/01-a.md", "# A\n\n## Next\n\n[c](03-c.md)\n")
        write(self.root, f"{p}/notes/02-b.md", "# B\n\n## Next\n\n[d](04-d.md)\n")
        write(self.root, f"{p}/notes/03-c.md", "# C\n\n## Next\n\n[out](../../04-d/README.md)\n")
        write(self.root, f"{p}/notes/04-d.md", "# D\n\n## Next\n\n[out](../../04-d/README.md)\n")
        write(self.root, f"{p}/notes/05-e.md", "# E\n")
        issues = [i["path"] for i in cm.build(self.root)["issues"] if i["kind"] == "next_out_of_order"]
        # 01 and 02 follow the README. 03 points out of the pillar but the README does not read it last.
        self.assertIn(f"{p}/notes/03-c.md", issues)
        self.assertNotIn(f"{p}/notes/01-a.md", issues)
        self.assertNotIn(f"{p}/notes/02-b.md", issues)
        # 04 is read last in the README, so it may close the pillar even with a note numbered after it.
        self.assertNotIn(f"{p}/notes/04-d.md", issues)

    def test_readme_gaps(self):
        self.assertEqual([i["path"] for i in self.kinds("not_in_readme")], ["data-science/01-a/notes/04-unlisted.md"])
        self.assertEqual([i["path"] for i in self.kinds("no_cross_links")], ["data-science/02-b/README.md"])

    def test_number_gap(self):
        self.assertEqual([i["detail"] for i in self.kinds("number_gap")], ["no note numbered 03"])

    def test_deck(self):
        self.assertEqual({i["path"] for i in self.kinds("deck_gap")},
                         {"data-science/01-a/notes/02-two.md", "data-science/01-a/notes/04-unlisted.md"})
        self.assertEqual(len(self.kinds("deck_stale_source")), 1)

    def test_ledger_stale(self):
        self.assertEqual([i["path"] for i in self.kinds("ledger_stale_note")], ["data-science/01-a/notes/77-moved.md"])

    def test_find_prefers_a_heading_match(self):
        rows = cm.find_topic(self.map, "attention", self.root)
        self.assertEqual(rows[0]["path"], "data-science/01-a/notes/01-one.md")
        self.assertEqual(rows[0]["headings"], ["Attention"])

    def test_regressions_from_the_real_repo(self):
        p = "ai-engineering/02-b"
        write(self.root, f"{p}/README.md", "**Feeds into**\n\n[a](notes/01-a.md) [b](notes/13-b.md) [c](notes/13b-c.md) [d](notes/99-d.md)\n")
        write(self.root, f"{p}/notes/01-a.md", "# A\n\nWe are interacting here.\n")
        write(self.root, f"{p}/notes/13-b.md", "# B\n\nPositional encoding here.\n")
        write(self.root, f"{p}/notes/13b-c.md", "# C\n\nEncoding only. Encoding again. Encoding.\n")
        write(self.root, f"{p}/notes/99-d.md", "# D\n")
        write(self.root, f"{p}/slides/deck.yaml", "slides:\n  - {layout: x, source: notes/01-a.md, title: y}\n  - source: \"notes/13-b.md\"\n  - source: notes/13b-c.md # c\n  - source: notes/99-d.md\n")
        found = cm.build(self.root)
        mine = [i for i in found["issues"] if i["pillar"] == p and i["kind"] != "no_inbound"]
        # A far-off 99 is one issue, 13b beside 13 is no duplicate, and an inline deck source parses.
        self.assertEqual([(i["kind"], i["detail"]) for i in mine],
                         [("number_gap", "no note numbered 02 to 12"), ("number_gap", "no note numbered 14 to 98")])
        # "act" does not match "interacting", and the exact phrase outranks repeating one of its words.
        self.assertEqual(cm.find_topic(found, "act", self.root), [])
        self.assertEqual(cm.find_topic(found, "positional encoding", self.root)[0]["path"], f"{p}/notes/13-b.md")

    def test_programming_module_uses_the_track_readme(self):
        write(self.root, "programming/python/README.md", "[x](01-m/notes/01-x.md)\n")
        write(self.root, "programming/python/01-m/notes/01-x.md", "# X\n")
        write(self.root, "programming/python/01-m/notes/02-y.md", "# Y\n")
        found = cm.build(self.root)
        mine = [(i["kind"], i["path"]) for i in found["issues"] if i["pillar"] == "programming/python/01-m" and i["kind"] != "no_inbound"]
        self.assertEqual(mine, [("not_in_readme", "programming/python/01-m/notes/02-y.md")])

    def test_strict_exit_codes(self):
        self.assertEqual(cm.main(["--root", str(self.root), "issues", "--strict"]), 1)
        self.assertEqual(cm.main(["--root", str(self.root), "issues", "--kind", "no_inbound", "--strict"]), 0)


class ConceptHomes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.addCleanup(self.tmp.cleanup)
        registry = {"concepts": {"softmax": {"pattern": "\\bsoftmax\\b",
                                             "homes": ["generative-ai/01-a/notes/01-home.md#softmax", "data-science/01-b/notes/09-deep.md"]}}}
        write(self.root, "scripts/concept_homes.json", json.dumps(registry))
        write(self.root, "generative-ai/01-a/notes/01-home.md", "# Home\n\n## Softmax\n\nSoftmax is taught here.\n")
        write(self.root, "generative-ai/01-a/notes/02-linked.md", "# L\n\nA [softmax](01-home.md#softmax) again.\n")
        write(self.root, "generative-ai/01-a/notes/03-unlinked.md", "---\nstatus: draft\n---\n# U\n\nintro\n\nThe Softmax of the scores.\n")
        write(self.root, "generative-ai/01-a/notes/04-fenced.md", "# F\n\n```\nsoftmax(x)\n```\n")
        write(self.root, "generative-ai/01-a/notes/05-deeper.md", "# D\n\nsoftmax, see [deep](../../../data-science/01-b/notes/09-deep.md).\n")
        write(self.root, "data-science/01-b/notes/09-deep.md", "# Deep\n\nsoftmax in depth\n")
        self.issues = [i for i in cm.build(self.root)["issues"] if i["kind"] == "concept_unlinked"]

    def test_only_the_unlinked_use_is_reported(self):
        self.assertEqual([i["path"] for i in self.issues], ["generative-ai/01-a/notes/03-unlinked.md"])

    def test_detail_names_the_line_and_the_canonical_home(self):
        detail = self.issues[0]["detail"]
        self.assertIn("line 8", detail)
        self.assertIn("generative-ai/01-a/notes/01-home.md#softmax", detail)

    def test_information_only(self):
        self.assertIn("concept_unlinked", cm.INFO_KINDS)
        self.assertEqual(cm.main(["--root", str(self.root), "issues", "--kind", "concept_unlinked", "--strict"]), 0)

    def test_no_registry_no_reports(self):
        (self.root / "scripts/concept_homes.json").unlink()
        self.assertEqual([i for i in cm.build(self.root)["issues"] if i["kind"] == "concept_unlinked"], [])

    def test_ignored_note_is_not_reported(self):
        registry = json.loads((self.root / "scripts/concept_homes.json").read_text())
        registry["concepts"]["softmax"]["ignore"] = {"generative-ai/01-a/notes/03-unlinked.md": "names something else"}
        write(self.root, "scripts/concept_homes.json", json.dumps(registry))
        self.assertEqual([i for i in cm.build(self.root)["issues"] if i["kind"] == "concept_unlinked"], [])


if __name__ == "__main__":
    unittest.main()
