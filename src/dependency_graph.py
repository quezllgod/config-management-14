import json
import re
from pathlib import Path


def load_test_repository(filename):
    try:
        text = Path(filename).read_text(encoding="utf-8-sig")
        data = json.loads(text)
    except (OSError, ValueError) as error:
        raise ValueError("Не удалось прочитать тестовый JSON") from error

    if not isinstance(data, dict):
        raise ValueError("Тестовый репозиторий должен быть словарём")

    for name, dependencies in data.items():
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError("Имена пакетов должны быть большими буквами")
        if not isinstance(dependencies, list):
            raise ValueError("Зависимости должны быть списком")
        for dependency in dependencies:
            if not isinstance(dependency, str) or dependency not in data:
                raise ValueError(
                    f"Неизвестная зависимость пакета {name}"
                )

    return data


def build_graph(root, get_children, max_depth):
    if max_depth < 0:
        raise ValueError("Глубина не может быть отрицательной")

    graph = {}
    best_depth = {}
    cache = {}
    stack = [(root, 0)]

    while stack:
        node, depth = stack.pop()
        graph.setdefault(node, set())

        if node in best_depth and best_depth[node] <= depth:
            continue
        best_depth[node] = depth

        if depth >= max_depth:
            continue

        if node not in cache:
            cache[node] = list(get_children(node))

        for child in reversed(cache[node]):
            graph[node].add(child)
            graph.setdefault(child, set())
            stack.append((child, depth + 1))

    return graph


def print_graph(graph):
    for node, dependencies in sorted(graph.items()):
        if dependencies:
            print(f"{node} -> {', '.join(sorted(dependencies))}")
        else:
            print(f"{node} -> нет раскрытых зависимостей")

def reverse_graph(graph):
    result = {node: set() for node in graph}

    for parent, dependencies in graph.items():
        for dependency in dependencies:
            result.setdefault(dependency, set()).add(parent)

    return result