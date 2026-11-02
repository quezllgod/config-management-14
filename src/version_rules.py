import re


def version_tuple(value):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Неподдерживаемый формат версии: {value}")
    return tuple(map(int, value.split(".")))


def matches_rule(version, rule):
    current = version_tuple(version)
    rule = rule.strip()

    if rule in ("", "*", "x", "X"):
        return True

    if rule.startswith(("~", "^")):
        symbol = rule[0]
        base = version_tuple(rule[1:])
        if symbol == "~":
            upper = (base[0], base[1] + 1, 0)
        elif base[0] > 0:
            upper = (base[0] + 1, 0, 0)
        elif base[1] > 0:
            upper = (0, base[1] + 1, 0)
        else:
            upper = (0, 0, base[2] + 1)
        return base <= current < upper

    match = re.fullmatch(r"(>=|<=|>|<|=)?(\d+\.\d+\.\d+)", rule)
    if match:
        operator = match[1] or "="
        target = version_tuple(match[2])
        return {
            "=": current == target,
            ">": current > target,
            "<": current < target,
            ">=": current >= target,
            "<=": current <= target,
        }[operator]

    raise ValueError(f"Неподдерживаемое условие версии: {rule}")


def matches_range(version, requirement):
    requirement = re.sub(r"([<>]=?|=|\^|~)\s+", r"\1", requirement)
    requirement = re.sub(
        r"(?<![<>=])<(\d+)(?![\d.])",
        r"<\1.0.0",
        requirement
    )
    for alternative in requirement.split("||"):
        rules = alternative.strip().split()
        if all(matches_rule(version, rule) for rule in rules):
            return True
    return False


def choose_version(versions, requirement):
    suitable = []
    for version in versions:
        if re.fullmatch(r"\d+\.\d+\.\d+", version):
            if matches_range(version, requirement):
                suitable.append(version)

    if not suitable:
        raise ValueError(f"Нет подходящей версии для {requirement}")

    return max(suitable, key=version_tuple)