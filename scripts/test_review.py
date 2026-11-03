#!/usr/bin/env python3
"""Tests for the findings log, drill checks, eval scorer and signals report: python3 scripts/test_review.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "review"))
sys.path.insert(0, str(Path(__file__).parent / "practice"))
import check_drills as cd
import findings as fl
import score_eval as se
import signals as sg


def finding(**over):
    row = {"run": "r1", "reviewer": "drill-reviewer", "target": "a.md", "kind": "wrong-answer",
           "decision": "applied", "summary": "bad row"}
    return json.dumps({**row, **over})


class FindingsLog(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.log = Path(tmp.name) / "log.jsonl"

    def test_add_is_all_or_nothing(self):
        with self.assertRaisesRegex(ValueError, "line 2"):
            fl.add(self.log, [finding(), finding(summary="other", decision="maybe")], "2026-11-02")
        self.assertEqual(fl.read_rows(self.log), [])

    def test_rejection_needs_a_reason(self):
        with self.assertRaisesRegex(ValueError, "reason"):
            fl.add(self.log, [finding(decision="rejected")], "2026-11-02")

    def test_decide_moves_listed_to_rejected_and_counts_once(self):
        [fid] = fl.add(self.log, [finding(decision="listed")], "2026-11-02")
        fl.decide(self.log, fid, "rejected", "the drill is right", "2026-11-03")
        state = fl.current(fl.read_rows(self.log))
        self.assertEqual(len(state), 1)
        self.assertEqual(state[fid]["decision"], "rejected")
        self.assertEqual(fl.precision(list(state.values()))["drill-reviewer"], {"rejected": 1})

    def test_decide_unknown_id_fails(self):
        with self.assertRaisesRegex(ValueError, "no finding"):
            fl.decide(self.log, "nope", "applied", "", "2026-11-02")

    def test_candidate_needs_three_applied_across_two_files(self):
        one_file = [finding(summary=f"s{i}", pattern="p") for i in range(3)]
        fl.add(self.log, one_file, "2026-11-02")
        self.assertEqual(fl.candidates(fl.read_rows(self.log)), [])
        fl.add(self.log, [finding(summary="s9", target="b.md", pattern="p")], "2026-11-02")
        self.assertEqual(fl.candidates(fl.read_rows(self.log)), [("p", 4, 2)])

    def test_promoted_pattern_stops_being_a_candidate(self):
        rows = [finding(summary=f"s{i}", target=f"{i}.md", pattern="p") for i in range(3)]
        fl.add(self.log, rows, "2026-11-02")
        fl.append(self.log, [{"ts": "x", "type": "promotion", "pattern": "p", "to": "check.py"}])
        self.assertEqual(fl.candidates(fl.read_rows(self.log)), [])

    def test_report_flags_small_samples(self):
        fl.add(self.log, [finding()], "2026-11-02")
        self.assertIn("not a rate yet", "\n".join(fl.report_lines(fl.read_rows(self.log))))


DRILL = """---
title: T
track: sql
topic: t
difficulty: medium
timebox_min: 20
concepts: [a]
source: original
---

## Prompt

x

## Starter

x

## Tests

x

<details>
<summary>Solution</summary>

x

</details>
"""


class DrillChecks(unittest.TestCase):
    def test_valid_drill_passes(self):
        self.assertEqual(cd.check_drill(DRILL), [])

    def test_file_without_track_is_not_a_drill(self):
        self.assertEqual(cd.check_drill("# Track notes\n"), [])

    def test_bad_values_and_missing_section(self):
        text = DRILL.replace("difficulty: medium", "difficulty: brutal").replace("## Tests\n", "")
        problems = cd.check_drill(text)
        self.assertTrue(any("difficulty" in p for p in problems))
        self.assertTrue(any("Tests" in p for p in problems))

    def test_visible_solution_fails(self):
        text = DRILL.replace("<summary>Solution</summary>", "")
        self.assertTrue(any("details" in p for p in cd.check_drill(text)))

    def test_h1_in_a_code_fence_is_fine(self):
        self.assertEqual(cd.check_drill(DRILL + "\n```\n# comment\n```\n"), [])

    def test_python_and_sql(self):
        self.assertEqual(cd.check_python("raise NotImplementedError\n"), [])
        self.assertTrue(cd.check_python("def (:\n"))
        self.assertEqual(cd.check_sql("CREATE TABLE t (a); INSERT INTO t VALUES (1);"), [])
        self.assertTrue(cd.check_sql("CREATE TABEL t (a);"))


class EvalScoring(unittest.TestCase):
    CASE = {"id": "c", "planted": [{"id": "venue", "any": ["ICML"]}, {"id": "term", "any": ["HNSW"]}]}

    def test_only_findings_count(self):
        report = "NOTE: ICML mentioned above the findings\nFINDINGS (most costly)\n- line: 3\n  problem: wrong icml venue\n"
        result = se.score_case(self.CASE, report)
        self.assertEqual((result["caught"], result["missed"], result["findings"]), (["venue"], ["term"], 1))

    def test_no_findings_section(self):
        self.assertEqual(se.score_case(self.CASE, "VERDICT: ready")["caught"], [])

    def test_split_counts_each_finding(self):
        report = "FINDINGS\n- file: a\n  line: 1\n- file: b\n  line: 2\n"
        self.assertEqual(len(se.split_findings(report)), 2)


class Signals(unittest.TestCase):
    def test_drill_log_never_keeps_the_note(self):
        log = "| Date | QID | Aid | Score | Note |\n|---|---|---|---|---|\n| 2026-08-13 | a | 3 | D✓ T✗ | private words |\n"
        rows = sg.parse_drill_log(log)
        self.assertEqual(rows, [{"date": "2026-08-13", "qid": "a", "aid": "3", "score": "D✓ T✗"}])

    def test_drill_flagged_on_latest_attempt_only(self):
        rows = [{"date": "1", "qid": "a", "aid": "3", "score": "T✗"}, {"date": "2", "qid": "a", "aid": "0", "score": "T✓"},
                {"date": "1", "qid": "b", "aid": "—", "score": "T✗ S✗ D✓"}]
        lines = sg.drill_section(rows, {"b": "programming/drills/b.md"})
        self.assertEqual(len(lines), 2)
        self.assertIn("b:", lines[1])
        self.assertIn("programming/drills/b.md", lines[1])

    def test_card_needs_enough_attempts(self):
        def grade(front, result):
            return {"deck": "d", "front": front, "source": "", "result": result}
        rows = [grade("few", "missed")] * 2 + [grade("many", "missed")] * 2 + [grade("many", "knew")]
        lines = sg.flashcard_section(rows, Path("/nonexistent"))
        self.assertEqual(len(lines), 2)
        self.assertIn('"many"', lines[1])

    def test_deck_location_finds_the_slide(self):
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp) / "gen" / "01-a" / "slides" / "deck.yaml"
            deck.parent.mkdir(parents=True)
            deck.write_text("slides:\n  - layout: bullets\n    title: Why rerank?\n")
            where = sg.deck_location(Path(tmp), "learn-ai-engineering/gen/01-a/notes/x.md", "", "Why rerank?")
            self.assertEqual(where, "gen/01-a/slides/deck.yaml:3")

    def test_only_real_searches_count(self):
        rows = [{"tool": "eval", "query": "x", "n_results": 0}, {"tool": "search_wiki", "query": "gap", "n_results": 0},
                {"tool": "search_wiki", "query": "ok", "n_results": 3}, {"tool": "sweep"}]
        lines = sg.search_section(rows)
        self.assertIn("2 real wiki searches, 1 found nothing", lines[0])
        self.assertEqual(lines[1:], ['- 1x "gap"'])


if __name__ == "__main__":
    unittest.main()
