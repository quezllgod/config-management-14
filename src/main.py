import argparse
import re
from pathlib import Path
from urllib.parse import urlparse


def package_name(value):
    pattern = r"(?:@[a-z0-9_-]+/)?[a-z0-9_-][a-z0-9._-]*"
    if not re.fullmatch(pattern, value) and not re.fullmatch(
        r"[A-Z]+", value
    ):
        raise argparse.ArgumentTypeError("Некорректное имя пакета")
    return value


def package_version(value):
    pattern = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    pattern += r"(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?"
    if not re.fullmatch(pattern, value):
        raise argparse.ArgumentTypeError(
            "Версия должна иметь вид 1.0.0"
        )
    return value


def depth_value(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Глубина должна быть целым числом")
    if number < 0:
        raise argparse.ArgumentTypeError("Глубина не может быть отрицательной")
    return number


def output_file(value):
    path = Path(value)
    if path.suffix.lower() != ".png":
        raise argparse.ArgumentTypeError("Укажите имя файла с расширением .png")
    if not path.parent.is_dir():
        raise argparse.ArgumentTypeError("Папка для сохранения не существует")
    if path.is_dir():
        raise argparse.ArgumentTypeError("Вместо файла указана папка")
    return value


def check_repository(args, parser):
    if args.test:
        if not Path(args.repository).is_file():
            parser.error("Файл тестового репозитория не найден")
    else:
        try:
            address = urlparse(args.repository)
            valid = (
                address.scheme in ("http", "https")
                and address.hostname
                and not any(c.isspace() for c in args.repository)
            )
            address.port
        except ValueError:
            valid = False
        if not valid:
            parser.error("Укажите корректный URL с http:// или https://")


def get_settings():
    parser = argparse.ArgumentParser(
        description="Анализ зависимостей npm. Вариант 14"
    )
    parser.add_argument("--package", required=True, type=package_name)
    parser.add_argument("--repository", required=True)
    parser.add_argument(
        "--test", action="store_true", help="Использовать тестовый файл"
    )
    parser.add_argument("--version", required=True, type=package_version)
    parser.add_argument("--output", required=True, type=output_file)
    parser.add_argument("--max-depth", required=True, type=depth_value)
    args = parser.parse_args()
    check_repository(args, parser)
    return args


def main():
    args = get_settings()
    print(f"package = {args.package}")
    print(f"repository = {args.repository}")
    print(f"test = {args.test}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")
    print(f"max_depth = {args.max_depth}")


if __name__ == "__main__":
    main()