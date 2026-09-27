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
    r"ator",
    r"atог",
    r"wvol",
    r"wtot",
    r"htomo",
    r"ior",
]


NUMBER_PATTERN = r"[+\-]?\s*\d[\d\s.,]*"


IGNORED_ITEM_PATTERNS = [
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
    r"^ator\b",
    r"^atог\b",
    r"^wvol\b",
    r"^wtot\b",
    r"^htomo\b",
    r"^ior\b",
    r"^tax\b",
    r"^vat\b",
    r"^tva\b",
    r"^ндс\b",
    r"^hac\b",
    r"^hас\b",
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
    r"^дата\b",
    r"^date\b",
    r"^aata\b",
    r"^количество\s+товар",
    r"^koamyec",
]


OCR_TRAILING_NOISE = (
    r"""[\sA-Za-zА-Яа-яЁёÀ-ÿ°."'“”‘’\-]*"""
)

OCR_ZERO_SUFFIX = (
    rf"""\.[0Oo]{OCR_TRAILING_NOISE}"""
)