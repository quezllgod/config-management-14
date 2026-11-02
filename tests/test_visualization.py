import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.visualization import to_mermaid, save_mermaid, render_png


class VisualizationTests(unittest.TestCase):
    def test_edge(self):
        text = to_mermaid({"A": {"B"}, "B": set()})
        self.assertIn('n0["A"]', text)
        self.assertIn('n1["B"]', text)
        self.assertIn("n0 --> n1", text)

    def test_isolated_node(self):
        text = to_mermaid({"F": set()})
        self.assertIn('n0["F"]', text)
        self.assertNotIn("-->", text)

    def test_cycle(self):
        text = to_mermaid({"A": {"B"}, "B": {"A"}})
        self.assertIn("n0 --> n1", text)
        self.assertIn("n1 --> n0", text)

    def test_save_file(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "graph.png"
            source = save_mermaid({"A": set()}, output)
            self.assertEqual(source.suffix, ".mmd")
            self.assertEqual(
                source.read_text(encoding="utf-8"),
                to_mermaid({"A": set()}),
            )

    def test_missing_renderer(self):
        with patch("src.visualization.shutil.which", return_value=None):
            with self.assertRaises(ValueError):
                render_png("graph.mmd", "graph.png")


if __name__ == "__main__":
    unittest.main()