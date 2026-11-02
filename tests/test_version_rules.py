import unittest

from src.version_rules import choose_version, matches_range


class VersionRulesTests(unittest.TestCase):
    def test_exact_version(self):
        self.assertTrue(matches_range("1.2.3", "1.2.3"))
        self.assertFalse(matches_range("1.2.4", "1.2.3"))

    def test_tilde(self):
        self.assertTrue(matches_range("1.2.9", "~1.2.3"))
        self.assertFalse(matches_range("1.3.0", "~1.2.3"))

    def test_caret(self):
        self.assertTrue(matches_range("1.9.0", "^1.2.3"))
        self.assertFalse(matches_range("2.0.0", "^1.2.3"))

    def test_zero_major(self):
        self.assertTrue(matches_range("0.2.9", "^0.2.3"))
        self.assertFalse(matches_range("0.3.0", "^0.2.3"))

    def test_spaces_and_short_bound(self):
        self.assertTrue(matches_range("2.5.0", ">= 2.1.2 <3"))
        self.assertFalse(matches_range("3.0.0", ">= 2.1.2 <3"))

    def test_alternatives(self):
        self.assertTrue(matches_range("2.1.0", "^1.0.0 || ^2.0.0"))
        self.assertFalse(matches_range("3.0.0", "^1.0.0 || ^2.0.0"))

    def test_choose_highest(self):
        versions = ["1.2.0", "1.10.0", "1.9.0", "2.0.0"]
        self.assertEqual(choose_version(versions, "^1.0.0"), "1.10.0")

    def test_no_matching_version(self):
        with self.assertRaises(ValueError):
            choose_version(["1.0.0"], "^2.0.0")


if __name__ == "__main__":
    unittest.main()