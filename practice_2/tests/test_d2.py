"""Тесты генерации D2."""
import unittest

from d2_export import to_d2


class D2Test(unittest.TestCase):
    """Проверки текста D2."""

    def test_edges(self):
        """Имена квотируются, стрелки соответствуют графу."""
        text = to_d2({"a.b": ["c-d"], "c-d": []})
        self.assertIn('"a.b" -> "c-d"', text)

    def test_reverse(self):
        """В обратном режиме стрелка разворачивается."""
        text = to_d2({"D": ["B"], "B": []}, reverse=True)
        self.assertIn('"B" -> "D"', text)