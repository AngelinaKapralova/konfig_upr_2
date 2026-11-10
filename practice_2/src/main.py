import sys
import subprocess
from apt_repo import AptRepository, download_index
from config import parse_config
from errors import AppError, ConfigError
from file_repo import FileRepository
from graph import build_graph, format_graph, invert

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_CONFIG_ERROR = 2


def load_repository(config):
    """Создать репозиторий: тестовый файл или индекс Packages по URL."""
    if config.test_mode:
        return FileRepository.from_file(config.repo)
    return AptRepository(download_index(config.repo))


def neighbors_func(repo, reverse):
    """Вернуть функцию «пакет -> соседи» для прямого или обратного обхода."""
    table = invert(repo.graph) if reverse else repo.graph
    return lambda name: table.get(name, [])


def run(config):
    """Построить граф прямых или обратных зависимостей и вывести его."""
    repo = load_repository(config)
    repo.direct(config.package, config.version)
    graph = build_graph(
        config.package,
        neighbors_func(repo, config.reverse),
        config.max_depth,
        config.filter_substr,
    )
    title = "Обратные зависимости" if config.reverse else "Зависимости"
    print(f"{title} пакета {config.package}:")

    graph_str = format_graph(graph)
    print(graph_str)

    if config.output:
        d2_filepath = config.output.replace('.svg', '.d2')

        with open(d2_filepath, 'w', encoding='utf-8') as f:
            f.write(graph_str)
        print(f"Сохранен исходный файл: {d2_filepath}")

        try:
            subprocess.run(['d2', d2_filepath, config.output], check=True)
            print(f"Сгенерирована картинка: {config.output}")
        except FileNotFoundError:
            print("Ошибка: утилита 'd2' не найдена в системе!", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при работе утилиты d2: {e}", file=sys.stderr)

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