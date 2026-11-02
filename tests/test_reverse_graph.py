import unittest

from src.dependency_graph import build_graph, reverse_graph


class ReverseGraphTests(unittest.TestCase):
    def test_chain(self):
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        expected = {"A": set(), "B": {"A"}, "C": {"B"}}
        self.assertEqual(reverse_graph(graph), expected)

    def test_shared_dependency(self):
        graph = {"A": {"C"}, "B": {"C"}, "C": set()}
        self.assertEqual(reverse_graph(graph)["C"], {"A", "B"})

    def test_cycle(self):
        graph = {"A": {"B"}, "B": {"A"}}
        self.assertEqual(
            reverse_graph(graph), {"A": {"B"}, "B": {"A"}}
        )

    def test_isolated_package(self):
        self.assertEqual(reverse_graph({"F": set()}), {"F": set()})

    def test_self_cycle(self):
        self.assertEqual(reverse_graph({"A": {"A"}}), {"A": {"A"}})

    def test_empty_graph(self):
        self.assertEqual(reverse_graph({}), {})

    def test_depth_limit(self):
        repository = {"A": ["B"], "B": ["C"], "C": []}
        graph = build_graph("A", repository.__getitem__, 1)
        self.assertEqual(
            reverse_graph(graph), {"A": set(), "B": {"A"}}
        )


if __name__ == "__main__":
    unittest.main()