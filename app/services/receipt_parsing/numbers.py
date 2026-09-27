def normalize_number(value: str) -> float:
    if not value:
        raise ValueError(
            "Пустое числовое значение."
        )

    value = (
        value.strip()
        .replace("\u00a0", "")
        .replace(" ", "")
        .replace("*", "")
        .replace("+", "")
    )

    if "," in value and "." in value:
        last_comma = value.rfind(",")
        last_dot = value.rfind(".")

        if last_comma > last_dot:
            value = value.replace(".", "")
            value = value.replace(",", ".")
        else:
            value = value.replace(",", "")

    elif "," in value:
        value = value.replace(",", ".")

    if value.count(".") > 1:
        parts = value.split(".")
        value = (
            "".join(parts[:-1])
            + "."
            + parts[-1]
        )

    return float(value)