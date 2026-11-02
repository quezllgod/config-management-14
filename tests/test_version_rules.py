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


    def test_partial_major(self):
        self.assertTrue(matches_range("2.5.0", "2"))
        self.assertFalse(matches_range("3.0.0", "2"))

    def test_partial_minor(self):
        self.assertTrue(matches_range("2.1.9", "2.1"))
        self.assertFalse(matches_range("2.2.0", "2.1"))

    def test_wildcard(self):
        self.assertTrue(matches_range("2.5.0", "2.x"))
        self.assertFalse(matches_range("3.0.0", "2.x"))

    def test_partial_comparisons(self):
        cases = [
            ("2.0.0", ">=2", True),
            ("1.9.9", ">=2", False),
            ("2.0.9", "<2.1", True),
            ("2.1.0", "<2.1", False),
            ("2.9.9", "<=2", True),
            ("3.0.0", "<=2", False),
            ("2.9.9", ">2", False),
            ("3.0.0", ">2", True),
        ]
        for version, rule, expected in cases:
            with self.subTest(version=version, rule=rule):
                self.assertEqual(
                    matches_range(version, rule), expected
                )

    def test_short_compatible_ranges(self):
        cases = [
            ("1.2.9", "~1.2", True),
            ("1.3.0", "~1.2", False),
            ("1.9.0", "^1", True),
            ("2.0.0", "^1", False),
            ("0.2.9", "^0.2", True),
            ("0.3.0", "^0.2", False),
            ("0.9.0", "^0", True),
            ("1.0.0", "^0", False),
            ("0.0.9", "^0.0", True),
            ("0.1.0", "^0.0", False),
        ]
        for version, rule, expected in cases:
            with self.subTest(version=version, rule=rule):
                self.assertEqual(
                    matches_range(version, rule), expected
                )

    def test_hyphen_ranges(self):
        cases = [
            ("1.0.0", "1.0.0 - 2.0.0", True),
            ("2.0.0", "1.0.0 - 2.0.0", True),
            ("2.0.1", "1.0.0 - 2.0.0", False),
            ("2.9.0", "1 - 2", True),
            ("3.0.0", "1 - 2", False),
            ("2.3.9", "1.2 - 2.3", True),
            ("2.4.0", "1.2 - 2.3", False),
        ]
        for version, rule, expected in cases:
            with self.subTest(version=version, rule=rule):
                self.assertEqual(
                    matches_range(version, rule), expected
                )

if __name__ == "__main__":
    unittest.main()