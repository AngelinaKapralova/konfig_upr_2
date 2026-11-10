"""Построение графа зависимостей обходом в ширину (BFS)."""
from collections import deque


def is_skipped(name, substr):
    """Проверить, нужно ли пропустить пакет по подстроке в имени."""
    return bool(substr) and substr in name


def visible(names, current, substr):
    """Убрать повторы, петли и пакеты, имя которых содержит подстроку."""
    result = []
    for name in names:
        if name == current or is_skipped(name, substr):
            continue
        if name not in result:
            result.append(name)
    return result


def build_graph(root, neighbors, max_depth, substr=""):
    """Построить граф {пакет: [зависимости]} обходом BFS без рекурсии.

    Пакеты на глубине max_depth попадают в граф, но не раскрываются.
    Повторно найденный пакет не добавляется в очередь, поэтому циклы
    не приводят к зацикливанию (ребро в него при этом сохраняется).
    """
    graph = {root: []}
    depth = {root: 0}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        if depth[current] >= max_depth:
            continue
        for name in visible(neighbors(current), current, substr):
            graph[current].append(name)
            if name not in depth:
                depth[name] = depth[current] + 1
                graph[name] = []
                queue.append(name)
    return graph


def format_graph(graph):
    """Вернуть текст графа: по строке «пакет -> зависимости»."""
    lines = []
    for name, deps in graph.items():
        targets = ", ".join(deps) if deps else "—"
        lines.append(f"{name} -> {targets}")
    return "\n".join(lines)