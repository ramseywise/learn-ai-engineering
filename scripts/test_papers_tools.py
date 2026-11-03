#!/usr/bin/env python3
"""Tests for citegraph's reading lists, the figure-yield report and the nightly run's limit check."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent / "papers"))
import citegraph
import figures
import potw

LIB = Path(__file__).parent / "papers" / "nightly-lib.sh"


def run_lib(call, *args):
    return subprocess.run(["bash", "-c", f'source "{LIB}"; {call} "$@"', "bash", *args], capture_output=True, text=True)


class ReadingList(unittest.TestCase):
    def test_a_listed_work_is_not_a_seed(self):
        text = f"cited 2301.11111\n{citegraph.ORIGINS_START}\n| 2301.22222 |\n{citegraph.ORIGINS_END}\nafter\n"
        stripped = citegraph.strip_origins(text)
        self.assertIn("2301.11111", stripped)
        self.assertNotIn("2301.22222", stripped)
        self.assertIn("after", stripped)

    def test_only_an_integrated_row_reads_as_read(self):
        work = {"in_repo": "a/sources/x.pdf"}
        self.assertTrue(citegraph.read_state(work, {"a/sources/x.pdf": "integrated"}, "a").startswith("read "))
        self.assertTrue(citegraph.read_state(work, {"a/sources/x.pdf": "filed"}, "a").startswith("held, unread"))
        self.assertTrue(citegraph.read_state(work, {}, "a").startswith("held, unread"))

    def test_a_work_we_lack_says_not_held(self):
        with mock.patch.object(citegraph, "availability", return_value=("→ arXiv", "https://arxiv.org/abs/1")):
            self.assertTrue(citegraph.read_state({"in_repo": None}, {}, "a").startswith("not held"))


class FigureYield(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        for p in (mock.patch.object(potw, "REPO", self.repo),
                  mock.patch.object(potw, "PILLARS", {"rag": "gen/rag", "ml-systems": "de", "data-systems": "de"})):
            p.start()
            self.addCleanup(p.stop)

    def write(self, path, text=""):
        full = self.repo / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(text, encoding="utf-8")

    def rows(self, home, n):
        return [{"key": f"{home}{i}", "status": "integrated", "pillar": home, "local_pdf": "x.pdf"} for i in range(n)]

    def test_counts_kept_and_embedded_per_home(self):
        self.write("gen/rag/sources/images/a.png")
        self.write("gen/rag/sources/images/b.png")
        self.write("gen/rag/sources/images/notes.txt")
        self.write("gen/rag/notes/01.md", "![a](../sources/images/a.png)\n![web](https://x/y.png)\n")
        got = figures.figure_yield(self.rows("rag", 4), home="rag")[0]
        self.assertEqual((got["readings"], got["kept"], got["embedded"], got["per_100"]), (4, 2, 1, 25.0))

    def test_flags_a_big_home_with_almost_no_figures(self):
        low = figures.figure_yield(self.rows("rag", figures.LOW_YIELD_MIN_READINGS), home="rag")[0]
        self.assertTrue(low["low"])
        small = figures.figure_yield(self.rows("rag", figures.LOW_YIELD_MIN_READINGS - 1), home="rag")[0]
        self.assertFalse(small["low"])

    def test_homes_sharing_a_folder_share_a_line(self):
        rows = self.rows("ml-systems", 1) + self.rows("data-systems", 2) + [
            {"key": "q", "status": "queued", "pillar": "ml-systems", "local_pdf": "x.pdf"}]
        got = figures.figure_yield(rows, home="data-systems")
        self.assertEqual([(y["folder"], y["readings"]) for y in got], [("de", 3)])


class NightlyLimit(unittest.TestCase):
    def hit(self, status, out):
        return run_lib("limit_hit", str(status), out).returncode == 0

    def test_real_limit_line_counts_whatever_the_exit(self):
        line = "You've hit your session limit · resets 11:10am (Europe/Berlin)"
        self.assertTrue(self.hit(1, line))
        self.assertTrue(self.hit(0, f"partial work\n{line}"))

    def test_a_summary_that_mentions_limits_is_not_one(self):
        self.assertFalse(self.hit(0, "Integrated a paper on rate limit handling; usage limit tiers explained."))

    def test_other_failures_are_not_a_limit(self):
        self.assertFalse(self.hit(1, "Not logged in"))
        self.assertTrue(self.hit(1, "API Error: rate limit"))

    def test_stop_hour(self):
        self.assertEqual(run_lib("past_stop", "08", "8").returncode, 0)
        self.assertEqual(run_lib("past_stop", "07", "8").returncode, 1)
        self.assertEqual(run_lib("past_stop", "23", "8").returncode, 1)  # started before midnight
        self.assertEqual(run_lib("past_stop", "10", "24").returncode, 1)

    def test_scripts_parse(self):
        for name in ("papers-nightly.sh", "nightly-lib.sh"):
            result = subprocess.run(["bash", "-n", str(LIB.parent / name)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
