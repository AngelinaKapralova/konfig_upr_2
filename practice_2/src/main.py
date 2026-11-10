import sys

from apt_repo import AptRepository, download_index
from config import parse_config
from errors import AppError, ConfigError
from file_repo import FileRepository
from graph import build_graph, format_graph

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_CONFIG_ERROR = 2


def load_repository(config):
    """Создать репозиторий: тестовый файл или индекс Packages по URL."""
    if config.test_mode:
        return FileRepository.from_file(config.repo)
    return AptRepository(download_index(config.repo))


def run(config):
    """Построить граф зависимостей и вывести его в виде текста."""
    repo = load_repository(config)
    repo.direct(config.package, config.version)
    graph = build_graph(
        config.package,
        lambda name: repo.graph.get(name, []),
        config.max_depth,
        config.filter_substr,
    )
    print(format_graph(graph))
    return EXIT_OK



def main(argv=None):
    """Разобрать параметры, запустить работу, обработать ошибки."""
    try:
        return run(parse_config(argv))
    except ConfigError as err:
        print(f"Ошибка параметров: {err}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except AppError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())