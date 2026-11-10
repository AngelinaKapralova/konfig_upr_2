"""Тесты разбора индекса Packages."""
import unittest

from apt_repo import AptRepository
from errors import RepoError

SAMPLE = """Package: foo
Version: 1.0
Depends: libc6 (>= 2.34), bar | baz, qux:any
Pre-Depends: dpkg

Package: bar
Version: 2.0
"""


class AptRepoTest(unittest.TestCase):
    """Проверки разбора зависимостей."""

    def test_direct(self):
        """Версии, альтернативы и архитектуры отбрасываются."""
        repo = AptRepository(SAMPLE)
        deps = repo.direct("foo", "1.0")
        self.assertEqual(deps, ["libc6", "bar", "qux", "dpkg"])

    def test_unknown(self):
        """Неизвестный пакет или версия дают RepoError."""
        repo = AptRepository(SAMPLE)
        with self.assertRaises(RepoError):
            repo.direct("nope", "1.0")
        with self.assertRaises(RepoError):
            repo.direct("foo", "9.9")