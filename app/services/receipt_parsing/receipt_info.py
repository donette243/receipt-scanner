import re
from .numbers import normalize_number
from .patterns import (
    DATE_PATTERNS,
    NUMBER_PATTERN,
    TOTAL_KEYWORDS,
)


def extract_date(text: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

    return None


def extract_total(text: str) -> float | None:
    explicit_candidates: list[float] = []
    fallback_candidates: list[float] = []

    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):
        has_total_keyword = any(
            re.search(
                rf"\b{keyword}\b",
                line,
                re.IGNORECASE,
            )
            for keyword in TOTAL_KEYWORDS
        )

        if has_total_keyword:
            numbers = re.findall(
                NUMBER_PATTERN,
                line,
            )

            for number in numbers:
                try:
                    value = normalize_number(number)
                except ValueError:
                    continue

                if value >= 0:
                    explicit_candidates.append(value)

        star_match = re.fullmatch(
            r"""
            [A-Za-zА-Яа-яЁё]?
            \s*
            \*
            \s*
            (\d[\d\s]*[,.]\d{2})
            """,
            line,
            re.VERBOSE,
        )

        if star_match and index > 0:
            previous_window = " ".join(
                lines[max(0, index - 3):index]
            ).lower()

            quantity_summary = re.search(
                r"""
                (?:
                    количество\s+товар
                    |
                    koam
                    |
                    tovar
                    |
                    tobap
                    |
                    no3h
                )
                """,
                previous_window,
                re.IGNORECASE | re.VERBOSE,
            )

            if quantity_summary:
                try:
                    value = normalize_number(
                        star_match.group(1)
                    )
                except ValueError:
                    continue

                if value >= 0:
                    fallback_candidates.append(value)

    if explicit_candidates:
        return max(explicit_candidates)

    if fallback_candidates:
        return max(fallback_candidates)

    return None
def extract_store(text: str) -> str | None:
    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    ignored_exact = {
        "receipt",
        "ticket",
        "reçu",
        "facture",
        "invoice",
        "чек",
        "кассовый чек",
        "касса",
    }

    ignored_patterns = [
        r"^\d+$",
        r"^kkt\b",
        r"^ккт\b",
        r"^inn\b",
        r"^инн\b",
        r"^касса\b",
        r"^kassa\b",
        r"^кассир\b",
        r"^receipt\b",
        r"^ticket\b",
        r"^invoice\b",
        r"^дата\b",
        r"^date\b",
        r"^счет\b",
        r"^сч[еe]т\b",
        r"^оператор\b",
        r"^kacc",
        r"^kac[o0]",
        r"^\|?\s*kaco",
    ]

    for line in lines[:15]:
        normalized = line.lower()

        if normalized in ignored_exact:
            continue

        if len(line) < 3 or len(line) > 255:
            continue

        letters = re.findall(
            r"[A-Za-zА-Яа-яЁёÀ-ÿ]",
            line,
        )

        if len(letters) < 3:
            continue

        if re.fullmatch(
            r"""[\d\s./:,*+\-=|_'";—–ï]+""",
            line,
        ):
            continue

        if any(
            re.search(
                pattern,
                normalized,
                re.IGNORECASE,
            )
            for pattern in ignored_patterns
        ):
            continue

        if re.search(
            r"\b(?:inn|инн|kkt|ккт|siret)\b",
            normalized,
            re.IGNORECASE,
        ):
            continue

        if re.search(
            r"\b(?:"
            r"rue|street|avenue|av\.?|boulevard|"
            r"france|россия|москва|mockea"
            r")\b",
            normalized,
            re.IGNORECASE,
        ):
            continue

        store = re.sub(
            r"""^[\s"'“”‘’«»|~_=+*°—–.,;:{}\-]+""",
            "",
            line,
        )

        store = re.sub(
            r"""[\s"'“”‘’«»|~_=+*°—–.,;:{}\-]+$""",
            "",
            store,
        )

        store = re.sub(
            r"\s+",
            " ",
            store,
        ).strip()

        if store:
            return store[:255]

    return None