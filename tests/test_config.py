import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from src.main import get_settings


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.args = [
            "--package", "express",
            "--repository", "https://registry.npmjs.org",
            "--version", "4.18.2",
            "--output", "graph.png",
            "--max-depth", "3",
        ]

    def read_settings(self):
        with patch.object(sys, "argv", ["main.py"] + self.args):
            return get_settings()

    def check_error(self, option, value):
        index = self.args.index(option) + 1
        self.args[index] = value
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                self.read_settings()
        self.assertEqual(error.exception.code, 2)

    def test_valid_settings(self):
        args = self.read_settings()
        self.assertEqual(args.package, "express")
        self.assertEqual(args.repository, "https://registry.npmjs.org")
        self.assertEqual(args.version, "4.18.2")
        self.assertEqual(args.output, "graph.png")
        self.assertEqual(args.max_depth, 3)
        self.assertFalse(args.test)

    def test_bad_package(self):
        self.check_error("--package", "bad name!")

    def test_bad_repository(self):
        self.check_error("--repository", "wrong-address")

    def test_bad_version(self):
        self.check_error("--version", "hello")

    def test_bad_output(self):
        self.check_error("--output", "graph.jpg")

    def test_negative_depth(self):
        self.check_error("--max-depth", "-1")

    def test_text_depth(self):
        self.check_error("--max-depth", "three")

    def test_zero_depth(self):
        self.args[-1] = "0"
        self.assertEqual(self.read_settings().max_depth, 0)

    def test_missing_test_file(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = str(Path(folder) / "missing.json")
            self.args.append("--test")
            self.check_error("--repository", missing)

    def test_valid_test_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "repo.json"
            file.write_text('{"A": []}', encoding="utf-8")
            self.args[1] = "A"
            self.args[3] = str(file)
            self.args.append("--test")
            args = self.read_settings()
            self.assertTrue(args.test)
            self.assertEqual(args.repository, str(file))

    def test_bad_test_flag(self):
        self.args.append("--test=hello")
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                self.read_settings()
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()