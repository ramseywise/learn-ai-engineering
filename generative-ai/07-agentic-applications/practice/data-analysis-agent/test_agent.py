"""python -m unittest test_agent (with pandas and matplotlib available)"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

from agent import Analyst, ToolError, bootstrap_difference, run_agent, traced, validate  # noqa: E402
from datasets import load  # noqa: E402
from run import METRICS  # noqa: E402
from scripted import ANALYSES, ScriptedModel  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.analyst = Analyst({"tips": load("tips"), "titanic": load("titanic")}, METRICS, Path(self.tmp.name))

    def tearDown(self):
        self.analyst.conn.close()
        self.tmp.cleanup()

    def play(self, name):
        question, script = ANALYSES[name]
        return run_agent(ScriptedModel(script), self.analyst, question, trace=lambda _line: None)


class Analyses(Base):
    def test_tip_share_needs_three_tries(self):
        result = self.play("tip_share")
        self.assertEqual((result.status, result.rejected), ("answered", 2))
        rejected = [entry["output"] for entry in result.log if entry["is_error"]]
        self.assertIn("not an agreed metric", rejected[0])
        self.assertIn("State that sample size", rejected[1])
        self.assertIn("not distinguishable", rejected[1])
        self.assertIn("did not come from any tool result", rejected[1])

    def test_titanic_age_reports_coverage(self):
        result = self.play("titanic_age")
        self.assertEqual(result.status, "answered")
        text = result.log[2]["output"]
        self.assertIn("null in 177 of 891", text)
        self.assertIn("observational", text)

    def test_titanic_sex(self):
        self.assertEqual(self.play("titanic_sex").status, "answered")

    def test_guards_leave_the_data_intact(self):
        result = self.play("guards")
        self.assertEqual(result.rejected, 10)
        self.assertEqual(self.analyst.conn.execute("SELECT COUNT(*) FROM tips").fetchone()[0], 244)
        self.assertEqual(result.status, "stopped_without_answer:end_turn")


class Validator(Base):
    def check(self, **overrides):
        args = dict(text="Friday, n=19, not distinguishable from Sunday.", metric="tip_share", group_by="day",
                    group="Fri", value=0.1699, is_largest=True)
        args.update(overrides)
        return validate(self.analyst, **args)

    def test_accepts_a_correct_claim(self):
        self.assertEqual(self.check(), [])

    def test_rejects_a_wrong_value(self):
        self.assertIn("Recomputed", self.check(value=0.25)[0])

    def test_rejects_a_wrong_group_as_largest(self):
        self.assertTrue(any("not the largest" in p for p in self.check(group="Sun", value=0.1669)))

    def test_rejects_an_unknown_group(self):
        self.assertIn("does not exist", self.check(group="Mon")[0])

    def test_traced_respects_precision(self):
        self.assertTrue(traced("17.0", True, {0.1699}))
        self.assertFalse(traced("20", True, {0.1699}))
        self.assertTrue(traced("3.26", False, {3.2551}))

    def test_bootstrap_is_reproducible(self):
        frame = load("tips")
        a, b = frame.tip[frame.day == "Fri"], frame.tip[frame.day == "Sun"]
        self.assertEqual(bootstrap_difference(a, b), bootstrap_difference(a, b))


class Sql(Base):
    def test_no_write_gets_through(self):
        for query in ["DROP TABLE tips", "UPDATE tips SET tip = 0", "INSERT INTO tips (tip) VALUES (1)",
                      "CREATE TABLE t (a)", "ATTACH DATABASE ':memory:' AS x", "PRAGMA query_only = 0"]:
            with self.assertRaises(ToolError, msg=query):
                self.analyst.run_sql(query)

    def test_runaway_query_is_stopped(self):
        with self.assertRaises(ToolError):
            self.analyst.run_sql("SELECT COUNT(*) FROM tips a, tips b, tips c, tips d, tips e")

    def test_row_cap(self):
        self.assertIn("only the first 25 rows", self.analyst.run_sql("SELECT * FROM tips"))

    def test_chart_written(self):
        self.analyst.make_chart("SELECT day, AVG(tip) AS t FROM tips GROUP BY day", "Tip by day", "Sun")
        self.assertTrue(Path(self.analyst.charts[0]).stat().st_size > 1000)

    def test_chart_rejects_too_many_bars(self):
        with self.assertRaises(ToolError):
            self.analyst.make_chart("SELECT total_bill, tip FROM tips", "x", "y")


if __name__ == "__main__":
    unittest.main()
