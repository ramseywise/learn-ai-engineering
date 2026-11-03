import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from smoke_labs import run_lab  # noqa: E402


class RunLabTest(unittest.TestCase):
    def run_code(self, code, timeout=30):
        with tempfile.TemporaryDirectory() as tmp:
            return run_lab("lab", [sys.executable, "-c", code], Path(tmp), timeout)

    def test_clean_exit_is_ok(self):
        self.assertEqual(self.run_code("print('hi')").status, "ok")

    def test_failure_keeps_the_end_of_the_output(self):
        result = self.run_code("raise ValueError('boom')")
        self.assertEqual(result.status, "FAILED")
        self.assertIn("boom", result.tail)

    def test_hanging_lab_is_stopped_at_the_limit(self):
        result = self.run_code("import time; time.sleep(30)", timeout=0.5)
        self.assertEqual(result.status, "TIMEOUT")
        self.assertLess(result.seconds, 10)

    def test_headless_backend_is_set(self):
        self.assertEqual(self.run_code("import os; assert os.environ['MPLBACKEND'] == 'Agg'").status, "ok")


if __name__ == "__main__":
    unittest.main()
