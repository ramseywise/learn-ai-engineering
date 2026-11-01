"""Tests the agent never sees. They are copied in only after it has finished."""
import unittest

from tipkit.stats import median


class HeldOutTest(unittest.TestCase):
    def test_median_even_other_values(self):
        self.assertEqual(median([10, 40, 20, 30]), 25)

    def test_median_six_items(self):
        self.assertEqual(median([6, 1, 5, 2, 4, 3]), 3.5)

    def test_median_odd_still_works(self):
        self.assertEqual(median([7]), 7)


if __name__ == "__main__":
    unittest.main()
