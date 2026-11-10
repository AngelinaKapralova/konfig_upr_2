"""Чтение индекса Packages (формат apt) без внешних библиотек."""
import gzip
import http.client
import re
import urllib.request

from errors import RepoError

TIMEOUT_SEC = 30
GZIP_MAGIC = b"\x1f\x8b"
DEPENDS_FIELDS = ("Depends", "Pre-Depends")
VERSION_PART_RE = re.compile(r"\(.*?\)")
ARCH_PART_RE = re.compile(r"\[.*?\]")


def download_index(url):
    """Скачать индекс Packages (можно .gz) и вернуть его текст."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SEC) as response:
            raw = response.read()
        if raw.startswith(GZIP_MAGIC):
            raw = gzip.decompress(raw)
    except (OSError, EOFError, http.client.HTTPException) as err:
        raise RepoError(f"не удалось получить {url}: {err}") from err
    return raw.decode("utf-8", errors="replace")


def parse_stanza(block):
    """Разобрать блок «Поле: значение» в словарь."""
    fields = {}
    key = ""
    for line in block.splitlines():
        if line.startswith((" ", "\t")):
            if key:
                fields[key] += "\n" + line.strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            fields[key] = value.strip()
    return fields


def clean_name(item):
    """Оставить в элементе зависимости только имя пакета."""
    item = VERSION_PART_RE.sub("", item)
    item = ARCH_PART_RE.sub("", item)
    return item.strip().split(":")[0]


def parse_depends(value):
    """Вернуть имена пакетов из строки Depends без повторов.

    Для альтернатив «a | b» берётся первый вариант.
    """
    names = []
    for group in value.split(","):
        name = clean_name(group.split("|")[0])
        if name and name not in names:
            names.append(name)
    return names


def depends_of(fields):
    """Собрать зависимости из полей Depends и Pre-Depends."""
    names = []
    for key in DEPENDS_FIELDS:
        for name in parse_depends(fields.get(key, "")):
            if name not in names:
                names.append(name)
    return names


class AptRepository:
    """Индекс Packages.

    graph[имя] — зависимости первой найденной версии пакета,
    versions[имя][версия] — зависимости конкретной версии.
    """

    def __init__(self, text):
        """Построить индекс по тексту файла Packages."""
        self.graph = {}
        self.versions = {}
        for block in text.split("\n\n"):
            self.add(parse_stanza(block))

    def add(self, fields):
        """Добавить описание одного пакета в индекс."""
        name = fields.get("Package")
        version = fields.get("Version")
        if not name or not version:
            return
        deps = depends_of(fields)
        self.versions.setdefault(name, {})[version] = deps
        self.graph.setdefault(name, deps)

    def direct(self, name, version=None):
        """Вернуть прямые зависимости пакета заданной версии."""
        versions = self.versions.get(name)
        if not versions:
            raise RepoError(f"пакет {name} не найден в репозитории")
        if version not in versions:
            known = ", ".join(versions)
            raise RepoError(
                f"версия {version} пакета {name} не найдена (есть: {known})"
            )
        return versions[version]