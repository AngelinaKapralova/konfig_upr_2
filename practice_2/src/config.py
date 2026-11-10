"""Разбор и проверка параметров командной строки."""
import argparse
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

from errors import ConfigError

DEFAULT_DEPTH = 3
MIN_DEPTH = 1
URL_SCHEMES = ("http", "https")
OUTPUT_SUFFIX = ".svg"
APT_NAME_RE = re.compile(r"[a-z0-9][a-z0-9+.\-]+")
TEST_NAME_RE = re.compile(r"[A-Z]+")
VERSION_RE = re.compile(r"[0-9A-Za-z.+:~\-]+")


class ArgParser(argparse.ArgumentParser):
    """Парсер, который сообщает об ошибках через ConfigError."""

    def error(self, message):
        """Бросить ConfigError вместо завершения процесса."""
        raise ConfigError(message)


def check_package(name, test_mode):
    """Проверить имя пакета."""
    pattern = TEST_NAME_RE if test_mode else APT_NAME_RE
    if not pattern.fullmatch(name):
        raise ConfigError(f"некорректное имя пакета: {name!r}")
    return name


def check_repo(repo, test_mode):
    """Проверить путь к тестовому файлу или URL репозитория."""
    if test_mode:
        if not Path(repo).is_file():
            raise ConfigError(f"файл репозитория не найден: {repo}")
        return repo
    parsed = urlparse(repo)
    if parsed.scheme not in URL_SCHEMES or not parsed.netloc:
        raise ConfigError(f"некорректный URL репозитория: {repo!r}")
    return repo


def check_version(version, test_mode):
    """Проверить версию (в тестовом режиме она не нужна)."""
    if test_mode:
        return version
    if not VERSION_RE.fullmatch(version):
        raise ConfigError(f"некорректная версия пакета: {version!r}")
    return version


def check_output(output):
    """Проверить имя выходного SVG-файла."""
    path = Path(output)
    if path.suffix.lower() != OUTPUT_SUFFIX:
        raise ConfigError("имя файла должно оканчиваться на .svg")
    if not path.parent.is_dir():
        raise ConfigError(f"каталог не существует: {path.parent}")
    return output


def check_depth(depth):
    """Проверить максимальную глубину."""
    if depth < MIN_DEPTH:
        raise ConfigError(f"глубина должна быть не меньше {MIN_DEPTH}")
    return depth


def check_filter(substr, package):
    """Проверить, что фильтр не исключает сам анализируемый пакет."""
    if substr and substr in package:
        raise ConfigError("имя пакета содержит подстроку фильтра")
    return substr


@dataclass(frozen=True)
class Config:
    """Параметры, заданные пользователем."""

    package: str
    repo: str
    test_mode: bool
    version: str
    output: str
    max_depth: int
    filter_substr: str
    reverse: bool

    @classmethod
    def from_args(cls, args):
        """Проверить значения argparse и собрать конфигурацию."""
        test_mode = args.test_mode
        return cls(
            package=check_package(args.package, test_mode),
            repo=check_repo(args.repo, test_mode),
            test_mode=test_mode,
            version=check_version(args.version, test_mode),
            output=check_output(args.output),
            max_depth=check_depth(args.depth),
            filter_substr=check_filter(args.filter, args.package),
            reverse=args.reverse,
        )


def build_parser():
    """Создать парсер опций командной строки."""
    parser = ArgParser(
        prog="depgraph",
        description="Граф зависимостей пакетов apt (Ubuntu).",
    )
    parser.add_argument("-p", "--package", required=True,
                        help="имя анализируемого пакета")
    parser.add_argument("-r", "--repo", required=True,
                        help="URL файла Packages(.gz) или путь к файлу "
                             "тестового репозитория")
    parser.add_argument("-t", "--test-mode", action="store_true",
                        help="читать тестовый репозиторий из файла")
    parser.add_argument("-v", "--version", default="",
                        help="версия пакета (в тестовом режиме не нужна)")
    parser.add_argument("-o", "--output", default="graph.svg",
                        help="имя выходного SVG-файла")
    parser.add_argument("-d", "--depth", type=int, default=DEFAULT_DEPTH,
                        help="максимальная глубина анализа")
    parser.add_argument("-f", "--filter", default="",
                        help="не учитывать пакеты с этой подстрокой в имени")
    parser.add_argument("-R", "--reverse", action="store_true",
                        help="вывести обратные зависимости пакета")
    return parser


def parse_config(argv=None):
    """Разобрать аргументы и вернуть проверенную конфигурацию."""
    return Config.from_args(build_parser().parse_args(argv))


def format_params(config):
    """Вернуть параметры в формате «ключ: значение» по строке."""
    pairs = asdict(config).items()
    return "\n".join(f"{key}: {value}" for key, value in pairs)