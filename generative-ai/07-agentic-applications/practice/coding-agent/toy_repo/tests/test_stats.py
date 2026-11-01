import unittest

from tipkit.stats import median, tip_rate, top_value


class StatsTest(unittest.TestCase):
    def test_tip_rate(self):
        self.assertAlmostEqual(tip_rate(20.0, 3.0), 0.15)

    def test_median_odd(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_median_even(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_top_value(self):
        self.assertEqual(top_value([3, 9, 2]), 9)


if __name__ == "__main__":
    unittest.main()
