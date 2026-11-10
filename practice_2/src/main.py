"""Точка входа: CLI-инструмент графа зависимостей пакетов apt."""
import sys
from apt_repo import AptRepository, download_index
from config import parse_config
from errors import AppError, ConfigError

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_CONFIG_ERROR = 2

def run(config):
    """Вывести прямые зависимости пакета из репозитория по URL."""
    repo = AptRepository(download_index(config.repo))
    deps = repo.direct(config.package, config.version)
    print(f"Прямые зависимости {config.package} {config.version}:")
    for name in deps:
        print(f"  {name}")
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