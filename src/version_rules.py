import re


def version_tuple(value):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Неподдерживаемый формат версии: {value}")
    return tuple(map(int, value.split(".")))


def matches_partial(current, rule):
    match = re.fullmatch(
        r"(>=|<=|>|<|=)?(\d+)(?:\.(\d+|[xX*]))?"
        r"(?:\.(\d+|[xX*]))?",
        rule,
    )
    if not match:
        return None

    operator = match[1] or "="
    parts = [match[2], match[3], match[4]]
    numbers = []
    wildcard = False

    for part in parts:
        if part is None or part in ("x", "X", "*"):
            wildcard = True
        elif wildcard:
            raise ValueError(f"Некорректное условие: {rule}")
        else:
            numbers.append(int(part))

    if len(numbers) == 3:
        return None

    lower = tuple(numbers + [0] * (3 - len(numbers)))
    upper = list(lower)
    upper[len(numbers) - 1] += 1
    upper = tuple(upper)

    return {
        "=": lower <= current < upper,
        ">=": current >= lower,
        ">": current >= upper,
        "<": current < lower,
        "<=": current < upper,
    }[operator]

def matches_compatible(current, rule):
    match = re.fullmatch(
        r"([~^])(\d+)(?:\.(\d+))?(?:\.(\d+))?",
        rule,
    )
    if not match:
        raise ValueError(f"Неподдерживаемое условие версии: {rule}")

    numbers = [
        int(part) for part in match.groups()[1:]
        if part is not None
    ]
    lower = tuple(numbers + [0] * (3 - len(numbers)))

    if match[1] == "~":
        position = 0 if len(numbers) == 1 else 1
    else:
        position = len(numbers) - 1
        for index, number in enumerate(numbers):
            if number != 0:
                position = index
                break

    upper = list(lower)
    upper[position] += 1
    for index in range(position + 1, 3):
        upper[index] = 0

    return lower <= current < tuple(upper)

def matches_rule(version, rule):
    current = version_tuple(version)
    rule = rule.strip()

    if rule in ("", "*", "x", "X"):
        return True

    partial = matches_partial(current, rule)
    if partial is not None:
        return partial

    if rule.startswith(("~", "^")):
        return matches_compatible(current, rule)

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
    requirement = re.sub(
        r"(\d+(?:\.\d+){0,2})\s+-\s+"
        r"(\d+(?:\.\d+){0,2})",
        r">=\1 <=\2",
        requirement,
    )
    requirement = re.sub(
        r"([<>]=?|=|\^|~)\s+", r"\1", requirement
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