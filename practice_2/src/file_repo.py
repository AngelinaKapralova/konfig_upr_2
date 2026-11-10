"""Тестовый репозиторий: граф зависимостей из текстового файла."""
import re
from pathlib import Path

from errors import RepoError

NAME_RE = re.compile(r"[A-Z]+")
COMMENT_MARK = "#"


def parse_graph_text(text):
    """Разобрать строки вида «A: B C» в словарь {пакет: [зависимости]}."""
    graph = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split(COMMENT_MARK)[0].strip()
        if not line:
            continue
        name, sep, rest = line.partition(":")
        names = [name.strip()] + rest.split()
        if not sep or not all(NAME_RE.fullmatch(n) for n in names):
            raise RepoError(
                f"строка {number}: ожидалось «ИМЯ: ЗАВИСИМОСТИ», "
                "имена — большие латинские буквы через пробел"
            )
        graph[names[0]] = list(dict.fromkeys(names[1:]))
    return graph


class FileRepository:
    """Тестовый репозиторий с тем же интерфейсом, что у AptRepository."""

    def __init__(self, text):
        """Разобрать текст описания графа."""
        self.graph = parse_graph_text(text)

    @classmethod
    def from_file(cls, path):
        """Прочитать описание графа из файла."""
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as err:
            raise RepoError(f"не удалось прочитать {path}: {err}") from err
        return cls(text)

    def direct(self, name, version=None):
        """Вернуть прямые зависимости пакета (версия игнорируется)."""
        if name not in self.graph:
            raise RepoError(f"пакет {name} не описан в файле")
        return self.graph[name]