"""Генерация описания графа на языке D2 и рендер в SVG."""
import subprocess
from pathlib import Path

from errors import RenderError

D2_COMMAND = "d2"
D2_SUFFIX = ".d2"


def quote(name):
    """Заключить имя в кавычки: точки и дефисы не ломают разбор D2."""
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def to_d2(graph, reverse=False):
    """Построить текст D2: узлы и стрелки «зависит от».

    В режиме reverse стрелки разворачиваются обратно, чтобы
    стрелка всегда шла от зависящего пакета к тому, от кого он зависит.
    """
    lines = ["direction: right"]
    for name, deps in graph.items():
        lines.append(quote(name))
        for dep in deps:
            source, target = (dep, name) if reverse else (name, dep)
            lines.append(f"{quote(source)} -> {quote(target)}")
    return "\n".join(lines) + "\n"


def render_svg(d2_text, svg_path):
    """Сохранить D2-описание рядом с SVG и вызвать d2 для рендера."""
    d2_path = Path(svg_path).with_suffix(D2_SUFFIX)
    try:
        d2_path.write_text(d2_text, encoding="utf-8")
        subprocess.run(
            [D2_COMMAND, str(d2_path), str(svg_path)],
            check=True, capture_output=True, text=True,
        )
    except FileNotFoundError as err:
        raise RenderError("программа d2 не найдена, см. d2lang.com") from err
    except subprocess.CalledProcessError as err:
        raise RenderError(f"d2 завершился с ошибкой: {err.stderr}") from err
    except OSError as err:
        raise RenderError(f"не удалось записать файл: {err}") from err