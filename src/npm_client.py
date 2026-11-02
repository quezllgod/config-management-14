import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


def get_dependencies(repository, package, version):
    base = repository.rstrip("/")
    name = quote(package, safe="")
    release = quote(version, safe="")
    url = f"{base}/{name}/{release}"

    try:
        with urlopen(url, timeout=20) as response:
            data = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            raise ValueError("Пакет или указанная версия не найдены") from error
        raise ValueError(
            f"Ошибка репозитория: HTTP {error.code}"
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        raise ValueError(
            "Не удалось подключиться к репозиторию"
        ) from error
    except (ValueError, UnicodeError) as error:
        raise ValueError(
            "Репозиторий вернул некорректный JSON"
        ) from error

    if not isinstance(data, dict):
        raise ValueError("Описание пакета должно быть объектом JSON")

    dependencies = data.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise ValueError("Некорректный список зависимостей")
    if not all(
        isinstance(name, str) and isinstance(value, str)
        for name, value in dependencies.items()
    ):
        raise ValueError("Имена и версии зависимостей должны быть строками")

    return dependencies