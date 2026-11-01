"""Checks each limit against the scripted scenarios: python -m unittest test_agent"""
import sys
import unittest

sys.dont_write_bytecode = True

from agent import Limits, ToolError, Workspace, head_tail, run_agent  # noqa: E402
from scripted import SCENARIOS, ScriptedModel  # noqa: E402

TASK = "Fix median."


def play(name, limits=None):
    workspace = Workspace(limits or Limits())
    model = ScriptedModel(SCENARIOS[name](workspace.root))
    return workspace, run_agent(model, workspace, TASK, trace=lambda _line: None)


class Scenarios(unittest.TestCase):
    def test_fix_finishes_and_passes_heldout(self):
        workspace, result = play("fix")
        self.assertEqual(result.status, "finished")
        self.assertTrue(workspace.score_heldout()[0])
        workspace.close()

    def test_overfit_finishes_but_fails_heldout(self):
        workspace, result = play("overfit")
        self.assertEqual(result.status, "finished")
        self.assertFalse(workspace.score_heldout()[0])
        workspace.close()

    def test_guards_refuse_then_recover(self):
        workspace, result = play("guards")
        self.assertEqual(result.status, "finished")
        refused = [entry["output"] for entry in result.log if entry["is_error"]]
        self.assertEqual(len(refused), 9)
        for fragment in ["outside the workspace", "no tool called shell", "Read tipkit/stats.py", "read-only",
                         "matches 2 places", "would not parse", "Not finished", "changed since you read it"]:
            self.assertTrue(any(fragment in text for text in refused), fragment)
        self.assertTrue(workspace.score_heldout()[0])
        workspace.close()

    def test_stale_read_is_refused(self):
        workspace = Workspace(Limits())
        workspace.read_file("tipkit/stats.py")
        target = workspace.root / "tipkit" / "stats.py"
        target.write_text(target.read_text() + "\n# changed\n")
        with self.assertRaisesRegex(ToolError, "changed since you read it"):
            workspace.edit_file("tipkit/stats.py", "return ordered[mid]", "return 0")
        workspace.close()

    def test_timeout_kills_a_hanging_patch(self):
        workspace, result = play("timeout", Limits(test_timeout_s=1.0))
        self.assertEqual(result.status, "finished")
        self.assertTrue(any("Tests killed" in entry["output"] for entry in result.log))
        workspace.close()

    def test_repeat_halts(self):
        workspace, result = play("loop")
        self.assertEqual(result.status, "halted_repeat")
        workspace.close()

    def test_step_cap(self):
        workspace, result = play("budget", Limits(max_steps=4))
        self.assertEqual((result.status, result.steps), ("step_limit", 4))
        workspace.close()

    def test_end_turn_is_not_finish(self):
        workspace, result = play("giveup")
        self.assertEqual(result.status, "stopped_without_finish:end_turn")
        workspace.close()

    def test_process_escape_is_a_documented_limit(self):
        workspace, _result = play("escape")
        self.assertTrue((workspace.outside / "escaped.txt").exists())
        workspace.close()

    def test_head_tail_keeps_both_ends(self):
        text = "A" * 100 + "B" * 100
        short = head_tail(text, 20)
        self.assertTrue(short.startswith("A") and short.endswith("B") and "omitted" in short)


if __name__ == "__main__":
    unittest.main()
