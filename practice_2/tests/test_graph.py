"""Тесты построения графа."""
import unittest
from pathlib import Path

from file_repo import FileRepository
from graph import build_graph

DATA = Path(__file__).parent / "data"


def graph_of(file_name, root, depth, substr=""):
    """Построить граф для тестового файла."""
    repo = FileRepository.from_file(DATA / file_name)
    return build_graph(root, lambda n: repo.graph.get(n, []), depth, substr)


class GraphTest(unittest.TestCase):
    """Проверки BFS."""

    def test_full(self):
        """Транзитивные зависимости собираются полностью."""
        graph = graph_of("simple.txt", "A", 10)
        self.assertEqual(graph["C"], ["D", "E"])
        self.assertEqual(len(graph), 5)

    def test_depth(self):
        """Глубина 1 не раскрывает зависимости соседей."""
        graph = graph_of("simple.txt", "A", 1)
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_filter(self):
        """Пакеты с подстрокой в имени пропускаются."""
        graph = graph_of("simple.txt", "A", 10, "E")
        self.assertNotIn("E", graph)

    def test_cycle(self):
        """Цикл не приводит к зацикливанию."""
        graph = graph_of("cycle.txt", "A", 10)
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": ["A"]})