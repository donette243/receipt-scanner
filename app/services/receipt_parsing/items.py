import re

from .numbers import normalize_number
from .patterns import (
    IGNORED_ITEM_PATTERNS,
    OCR_TRAILING_NOISE,
    OCR_ZERO_SUFFIX,
)


def clean_item_name(name: str) -> str:
    name = name.strip()

    name = re.sub(
        r"""^[\s"'“”‘’«»|~_=+*°—–.,;:{}\-]+""",
        "",
        name,
    )

    name = re.sub(
        r"""[\s"'“”‘’«»|~_=+*°—–.,;:{}\-]+$""",
        "",
        name,
    )

    name = re.sub(
        r"""
        \s+
        (?:
            НДС|
            HAC|
            HАС|
            VAT|
            TVA
        )
        \s*
        \d+
        (?:
            \s*/\s*\d+
        )?
        .*
        $
        """,
        "",
        name,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    )

    return name.strip()


def is_ignored_item(name: str) -> bool:
    normalized = name.lower().strip()

    if not normalized:
        return True

    if len(normalized) < 2:
        return True

    return any(
        re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )
        for pattern in IGNORED_ITEM_PATTERNS
    )


def _looks_like_metadata(name: str) -> bool:
    normalized = name.lower().strip()

    metadata_patterns = [
        r"\b(?:ндс|hac|hас|vat|tva)"
        r"\s*\d+\s*/?\s*\d*",
        r"\b(?:inn|инн)\b",
        r"\b(?:kkt|ккт)\b",
        r"\b(?:касса|кассир)\b",
        r"\bsiret\b",
        r"\b\d{2}[./-]\d{2}[./-]\d{4}\b",
        r"\b\d{4}[./-]\d{2}[./-]\d{2}\b",
        r"\b\d{2}[./-]\d{2}[./-]\d{2}\b",
        r"\b\d{1,2}:\d{2}\b",
    ]

    return any(
        re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )
        for pattern in metadata_patterns
    )


def _normalize_ocr_price_text(
    value: str,
) -> str | None:
    if not value:
        return None

    value = value.strip()

    value = re.sub(
        r"""^[\s=|_'\"«»~*°—–]+""",
        "",
        value,
    )

    value = re.sub(
        r"""[\s=|_'\"«»~*°—–]+$""",
        "",
        value,
    )

    value = re.sub(
        r"[.,]?[A-Za-zА-Яа-яЁё]$",
        "",
        value,
    )

    if not re.fullmatch(
        r"\d[\d\s]*[,.]\d{1,3}",
        value,
    ):
        return None

    return value


def _parse_quantity_format(
    line: str,
) -> tuple[float, str, str] | None:
    match = re.match(
        r"""
        ^
        [~"'«»|—–]*
        (\d+(?:[.,]\d+)?)
        \s+
        (.+?)
        \s+
        [=|_'"]*
        (\d[\d\s]*[,.]\d{1,3})
        (?:
            \s+
            [=|_'"]*
            \d[\d\s]*[,.]\d{1,3}
        )?
        (?:
            \s*
            [°"'.,]*
            [A-Za-zА-Яа-яЁё]?
            [°"'.,]*
        )?
        \s*
        $
        """,
        line,
        re.VERBOSE,
    )

    if not match:
        return None

    try:
        quantity = normalize_number(
            match.group(1)
        )
    except ValueError:
        return None

    price_text = _normalize_ocr_price_text(
        match.group(3)
    )

    if price_text is None:
        return None

    return (
        quantity,
        match.group(2),
        price_text,
    )


def _parse_star_format(
    line: str,
) -> tuple[float, str, str] | None:
    match = re.match(
        r"""
        ^
        (.+?)
        \s*
        \*
        \s*
        (\d[\d\s]*[,.]\d{2})
        \s*
        $
        """,
        line,
        re.VERBOSE,
    )

    if not match:
        return None

    return (
        1.0,
        match.group(1),
        match.group(2),
    )


def _parse_noisy_ocr_format(
    line: str,
) -> tuple[float, str, str] | None:
    working = line.strip()

    working = re.sub(
        r"""[“”‘’]""",
        " ",
        working,
    )

    working = re.sub(
        r"\s*[|=—–]\s*",
        " ",
        working,
    )

    working = re.sub(
        r"\s+",
        " ",
        working,
    ).strip()

    working = re.sub(
        r"""^[~"'«»|{}\-]+\s*""",
        "",
        working,
    )

    money_matches = list(
        re.finditer(
            r"\d[\d\s]*[,.]\d{2}(?!\d)",
            working,
        )
    )

    if not money_matches:
        return None

    price_match = money_matches[-1]

    before_price = working[
        :price_match.start()
    ].strip()

    after_price = working[
        price_match.end():
    ].strip()

    if (
        after_price
        and not re.fullmatch(
            OCR_ZERO_SUFFIX,
            after_price,
        )
        and re.search(
            r"\d+\s*[:.,]\s*\d+",
            after_price,
        )
    ):
        return None

    if after_price:
        safe_tail = re.fullmatch(
            OCR_TRAILING_NOISE,
            after_price,
        )

        zero_ocr_tail = re.fullmatch(
            OCR_ZERO_SUFFIX,
            after_price,
        )

        if not safe_tail and not zero_ocr_tail:
            return None

    quantity = 1.0
    raw_name = before_price

    quantity_match = re.match(
        r"^(\d+(?:[.,]\d+)?)\s+(.+)$",
        before_price,
    )

    if quantity_match:
        try:
            quantity = normalize_number(
                quantity_match.group(1)
            )
        except ValueError:
            return None

        raw_name = quantity_match.group(2)

    raw_name = re.sub(
        r"""[\s*°"'“”‘’|=—–]+$""",
        "",
        raw_name,
    ).strip()

    if not raw_name:
        return None

    return (
        quantity,
        raw_name,
        price_match.group(0),
    )


def _parse_standard_format(
    line: str,
) -> tuple[float, str, str] | None:
    match = re.match(
        r"""
        ^
        [~"'«»|—–À]*
        \s*
        (.+?)
        \s+
        [=|_'"]*
        (\d[\d\s]*[,.]\d{1,3})
        (?:
            [.,]?
            \s*
            [°"'.,]*
            [A-Za-zА-Яа-яЁё]?
            [°"'.,]*
        )?
        \s*
        $
        """,
        line,
        re.VERBOSE,
    )

    if not match:
        return None

    price_text = _normalize_ocr_price_text(
        match.group(2)
    )

    if price_text is None:
        return None

    return (
        1.0,
        match.group(1),
        price_text,
    )


def extract_items(text: str) -> list[dict]:
    items: list[dict] = []

    for raw_line in text.splitlines():
        line = re.sub(
            r"\s+",
            " ",
            raw_line.strip(),
        )

        if not line:
            continue

        if is_ignored_item(line):
            continue

        parsed = (
            _parse_quantity_format(line)
            or _parse_star_format(line)
            or _parse_noisy_ocr_format(line)
            or _parse_standard_format(line)
        )

        if parsed is None:
            continue

        quantity, raw_name, price_text = parsed

        if quantity <= 0:
            continue

        name = clean_item_name(raw_name)

        if not name:
            continue

        if is_ignored_item(name):
            continue

        if _looks_like_metadata(name):
            continue

        if not re.search(
            r"[A-Za-zА-Яа-яЁёÀ-ÿ]",
            name,
        ):
            continue

        if re.fullmatch(
            r"[\d\s.,:/\-*()+]+",
            name,
        ):
            continue

        try:
            price = normalize_number(
                price_text
            )
        except (ValueError, TypeError):
            continue

        if price < 0:
            continue

        items.append(
            {
                "name": name[:255],
                "quantity": quantity,
                "price": price,
            }
        )

    return items