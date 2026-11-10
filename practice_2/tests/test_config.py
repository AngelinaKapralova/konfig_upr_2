"""Тесты разбора параметров командной строки."""
import unittest
from pathlib import Path

from config import parse_config
from errors import ConfigError

DATA = Path(__file__).parent / "data" / "simple.txt"


class ConfigTest(unittest.TestCase):
    """Проверки параметров."""

    def test_valid_test_mode(self):
        """Корректные параметры тестового режима принимаются."""
        argv = ["-p", "A", "-r", str(DATA), "-t", "-d", "2"]
        config = parse_config(argv)
        self.assertEqual(config.package, "A")
        self.assertEqual(config.max_depth, 2)

    def test_bad_values(self):
        """Некорректные значения вызывают ConfigError."""
        bad = [
            ["-p", "a", "-r", str(DATA), "-t"],
            ["-p", "A", "-r", "missing.txt", "-t"],
            ["-p", "curl", "-r", "ftp://x/Packages", "-v", "1"],
            ["-p", "curl", "-r", "http://x/Packages"],
            ["-p", "A", "-r", str(DATA), "-t", "-o", "g.png"],
            ["-p", "A", "-r", str(DATA), "-t", "-d", "0"],
            ["-p", "A", "-r", str(DATA), "-t", "-d", "abc"],
            ["-p", "AB", "-r", str(DATA), "-t", "-f", "B"],
            ["-r", str(DATA), "-t"],
        ]
        for argv in bad:
            with self.subTest(argv=argv):
                with self.assertRaises(ConfigError):
                    parse_config(argv)