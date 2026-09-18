import re


DATE_PATTERNS = [
    r"\b(\d{2}[./-]\d{2}[./-]\d{4})\b",
    r"\b(\d{4}[./-]\d{2}[./-]\d{2})\b",
    r"\b(\d{2}[./-]\d{2}[./-]\d{2})\b",
]

TOTAL_KEYWORDS = [
    r"total",
    r"totale",
    r"grand\s+total",
    r"amount",
    r"montant",
    r"sum",

    r"итого",
    r"итог",
    r"к\s+оплате",
    r"сумма",

    # OCR variants
    r"ator",
    r"atог",
    r"wvol",
    r"wtot",
    r"htomo",
    r"ior",
]


NUMBER_PATTERN = r"[+\-]?\s*\d[\d\s.,]*"


def normalize_number(value: str) -> float:
    if not value:
        raise ValueError("Valeur numérique vide.")

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
        value = "".join(parts[:-1]) + "." + parts[-1]

    return float(value)

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


IGNORED_ITEM_PATTERNS = [
    # Totals
    r"^total\b",
    r"^totale\b",
    r"^subtotal\b",
    r"^grand\s+total\b",
    r"^amount\b",
    r"^montant\b",
    r"^sum\b",

    r"^итого\b",
    r"^итог\b",
    r"^сумма\b",
    r"^к\s+оплате\b",

    # OCR totals
    r"^ator\b",
    r"^atог\b",
    r"^wvol\b",
    r"^wtot\b",
    r"^htomo\b",
    r"^ior\b",

    # Taxes
    r"^tax\b",
    r"^vat\b",
    r"^tva\b",
    r"^ндс\b",
    r"^hac\b",
    r"^hас\b",

    # Payment
    r"^cash\b",
    r"^card\b",
    r"^carte\b",
    r"^payment\b",
    r"^paiement\b",
    r"^change\b",

    r"^карта\b",
    r"^наличн",
    r"^сдача\b",
    r"^оплата\b",

    # OCR payment variants
    r"^karta(?:\s*[-_:]?\s*\d*)?\b",
    r"^kapta(?:\s*[-_:]?\s*\d*)?\b",
    r"^kар[тt]а\b",

    r"^caaya\b",
    r"^cdaya\b",

    r"^haamuh",
    r"^haauy",
    r"^haay",
    r"^haa",

    r"^hanbu",
    r"^py6nb\b",
    r"^coama\b",
    r"^orniata\b",
    r"^opniata\b",

    r"^bce[o0]\b",
    r"^hash\b",
    r"^hanh\b",

    # Fiscal metadata
    r"^ккт\b",
    r"^kkt\b",
    r"^инн\b",
    r"^inn\b",
    r"^касса\b",
    r"^kassa\b",
    r"^кассир\b",

    r"^siret\b",
    r"^table\b",
    r"^caisse\b",
    r"^document\b",

    # Dates
    r"^дата\b",
    r"^date\b",
    r"^aata\b",

    # Quantity summaries
    r"^количество\s+товар",
    r"^koamyec",
]


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
            r"""\.[0Oo][\sA-Za-zА-Яа-яЁёÀ-ÿ°."'“”‘’\-]*""",
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
            r"""[\sA-Za-zА-Яа-яЁёÀ-ÿ°."'“”‘’\-]*""",
            after_price,
        )

        zero_ocr_tail = re.fullmatch(
            r"""\.[0Oo][\sA-Za-zА-Яа-яЁёÀ-ÿ°."'“”‘’\-]*""",
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


def extract_receipt_data(
    text: str,
) -> dict:
    return {
        "store": extract_store(text),
        "receipt_date": extract_date(text),
        "total": extract_total(text),
        "items": extract_items(text),
    }