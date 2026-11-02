import unittest

from src.dependency_graph import build_graph


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.repository = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": ["A"],
            "E": [],
            "F": [],
        }

    def build(self, root, depth):
        return build_graph(
            root, self.repository.__getitem__, depth
        )

    def test_cycle(self):
        graph = self.build("A", 10)
        self.assertEqual(set(graph), {"A", "B", "C", "D", "E"})
        self.assertEqual(graph["D"], {"A"})

    def test_depth_one(self):
        self.assertEqual(
            self.build("A", 1),
            {"A": {"B", "C"}, "B": set(), "C": set()},
        )

    def test_depth_zero(self):
        self.assertEqual(self.build("A", 0), {"A": set()})

    def test_isolated_package(self):
        self.assertEqual(self.build("F", 3), {"F": set()})

    def test_self_cycle(self):
        self.repository = {"A": ["A"]}
        self.assertEqual(self.build("A", 10), {"A": {"A"}})

    def test_shorter_path(self):
        self.repository = {
            "A": ["B", "D"],
            "B": ["C"],
            "C": ["D"],
            "D": ["E"],
            "E": [],
        }
        graph = self.build("A", 3)
        self.assertEqual(graph["D"], {"E"})

    def test_negative_depth(self):
        with self.assertRaises(ValueError):
            self.build("A", -1)


if __name__ == "__main__":
    unittest.main()