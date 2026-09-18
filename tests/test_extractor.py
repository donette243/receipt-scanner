from app.services.extractor import (
    clean_item_name,
    extract_date,
    extract_items,
    extract_receipt_data,
    extract_store,
    extract_total,
    is_ignored_item,
    normalize_number,
)


# =========================================================
# NUMBER NORMALIZATION
# =========================================================

def test_normalize_number_comma():
    assert normalize_number("88,80") == 88.80


def test_normalize_number_with_spaces():
    assert normalize_number("1 234,50") == 1234.50


# =========================================================
# DATE
# =========================================================

def test_extract_date():
    text = """
    Carrefour
    29/08/2026
    TOTAL 25,50
    """

    assert extract_date(text) == "29/08/2026"


def test_extract_date_iso():
    assert extract_date(
        "Date: 2026-08-29"
    ) == "2026-08-29"


def test_extract_date_not_found():
    assert extract_date(
        "Carrefour\nTOTAL 25,50"
    ) is None


def test_extract_short_year_date():
    assert extract_date(
        "Date 20-04-17 15:49"
    ) == "20-04-17"


# =========================================================
# TOTAL
# =========================================================

def test_extract_total():
    text = """
    Milk 2,50
    Bread 1,80
    TOTAL 4,30
    """

    assert extract_total(text) == 4.30


def test_extract_total_alternative_format():
    assert extract_total(
        "Montant: 12,50"
    ) == 12.50


def test_extract_total_not_found():
    assert extract_total(
        "Milk 2,50\nBread 1,80"
    ) is None


def test_extract_total_invalid_number():
    assert extract_total(
        "TOTAL abc"
    ) is None


def test_extract_total_wtot_ocr():
    text = """
    CUNKA «5500.00
    WTOT — =6900.00
    HANH =5900.00
    """

    assert extract_total(text) == 6900.00


def test_extract_total_degraded_russian_fallback():
    text = """
    KOAM4eCTBO TOBAPHbIX NO3HLVH 3
    i * 260.00
    """

    assert extract_total(text) == 260.00


# =========================================================
# STORE
# =========================================================

def test_extract_store():
    text = """
    Carrefour
    29/08/2026
    Milk 2,50
    TOTAL 2,50
    """

    assert extract_store(text) == "Carrefour"


def test_extract_store_empty():
    assert extract_store("") is None


def test_extract_store_ignores_numeric_line():
    text = """
    Receipt
    123456
    Carrefour
    TOTAL 10,00
    """

    assert extract_store(text) == "Carrefour"


def test_extract_store_ignored_headers():
    text = """
    receipt
    ticket
    facture
    Carrefour
    """

    assert extract_store(text) == "Carrefour"


def test_extract_store_ignores_ocr_noise():
    text = """
    ï ; : —"
    CAFE ODESSA '
    * 128 RUE ODESSA.
    75014 PARIS FRANCE
    """

    store = extract_store(text)

    assert store is not None
    assert clean_item_name(store) == "CAFE ODESSA"


def test_extract_store_ignores_degraded_cash_receipt_header():
    text = """
    | KACOOBU VEK KOPPEKUMA
    | AutmActpator
    """

    store = extract_store(text)

    assert store != "| KACOOBU VEK KOPPEKUMA"


# =========================================================
# ITEM NAME
# =========================================================

def test_clean_item_name():
    assert clean_item_name(
        '  "Milk"  '
    ) == "Milk"


def test_clean_item_name_removes_tax():
    assert clean_item_name(
        "Milk HAC 18/118"
    ) == "Milk"


def test_clean_item_name_removes_ocr_prefix_suffix():
    assert clean_item_name(
        "{CHOCOLAT LIEGEOIS."
    ) == "CHOCOLAT LIEGEOIS"


def test_clean_item_name_removes_dash_prefix():
    assert clean_item_name(
        "- À ENTRECOTE GRILLEE"
    ) == "À ENTRECOTE GRILLEE"


# =========================================================
# IGNORED ITEMS
# =========================================================

def test_ignored_item():
    assert is_ignored_item("TOTAL") is True
    assert is_ignored_item("tax") is True
    assert is_ignored_item("Milk") is False
    assert is_ignored_item("A") is True


def test_ignored_wtot():
    assert is_ignored_item(
        "WTOT — =6900.00"
    ) is True


def test_ignored_payment_ocr():
    assert is_ignored_item(
        "HAAUYHbIE PYb. *60.00"
    ) is True


# =========================================================
# BASIC ITEM EXTRACTION
# =========================================================

def test_extract_items():
    text = """
    Carrefour
    Milk 2,50
    Bread 1,80
    TOTAL 4,30
    """

    items = extract_items(text)

    assert len(items) == 2

    assert items[0]["name"] == "Milk"
    assert items[0]["price"] == 2.50
    assert items[0]["quantity"] == 1

    assert items[1]["name"] == "Bread"
    assert items[1]["price"] == 1.80
    assert items[1]["quantity"] == 1


def test_extract_items_with_quantity():
    text = """
    4 APEROL SPRITZ 44.50 B
    2 BADOIT ROUGE 5.80 11.60C
    4 ENTRECOTE GRILLEE 24.50 C
    """

    items = extract_items(text)

    assert len(items) == 3

    assert items[0]["quantity"] == 4
    assert items[0]["price"] == 44.50

    assert items[1]["quantity"] == 2
    assert items[1]["price"] == 5.80

    assert items[2]["quantity"] == 4
    assert items[2]["price"] == 24.50


def test_extract_items_comma_price():
    items = extract_items(
        "Milk 2,50"
    )

    assert len(items) == 1
    assert items[0]["price"] == 2.50


def test_extract_items_without_price():
    assert extract_items(
        "Milk"
    ) == []


def test_extract_items_invalid_price():
    assert extract_items(
        "Milk abc"
    ) == []


def test_extract_items_ignores_invalid_lines():
    text = """
    TOTAL 20,00
    TAX 2,00
    PAYMENT CARD
    12345
    A
    """

    assert extract_items(text) == []


# =========================================================
# COMPLETE BASIC RECEIPT
# =========================================================

def test_extract_receipt_data():
    text = """
    Carrefour
    29/08/2026
    Milk 2,50
    TOTAL 2,50
    """

    data = extract_receipt_data(text)

    assert data["store"] == "Carrefour"
    assert data["receipt_date"] == "29/08/2026"
    assert data["total"] == 2.50
    assert len(data["items"]) == 1


# =========================================================
# REAL RECEIPT 1 — RUSSIAN
# =========================================================

def test_extract_real_russian_ocr_receipt():
    text = """
    000 “MepBbiñ BUT”
    KodeHHsa “Adpoanta”
    r. Mockea, BopoHuoBcxas, 35 À
    KKT Ne 009011123 WHH: 7700077301
    Cron Ne 1
    Opuuvant CrenaHos Barepuñ
    * KACCOBbIH YEK *
    * TIPUXOA *
    Canar Llesapb (A) HAC 18/118 *200.00
    CpexezaBapeHHbIk Kode (AT)
    HAC 18/118 *50.00
    CaWBKH 50 MA HAC 10/110 *10.00
    KOAMYECTBO TOBApHbIX NO3HLHH 3
    ATOr * 260.00
    Br. 4. HAC:
    HAC 18/118 *38.14
    HAC 10/110 *0.91
    KAPTA-2 *200.00
    HAAMUHBIE PYb. *60.00
    CAAYA *00.00
    """

    data = extract_receipt_data(text)

    assert data["total"] == 260.00
    assert len(data["items"]) == 2

    assert data["items"][0]["price"] == 200.00
    assert data["items"][1]["price"] == 10.00


def test_extract_real_russian_ocr_receipt_item_names():
    text = """
    Canar Llesapb (A) HAC 18/118 *200.00
    CpexezaBapeHHbIk Kode (AT)
    HAC 18/118 *50.00
    CaWBKH 50 MA HAC 10/110 *10.00
    KOAMYECTBO TOBApHbIX NO3HLHH 3
    ATOr * 260.00
    """

    items = extract_items(text)

    assert len(items) == 2

    assert items[0]["name"] == "Canar Llesapb (A)"
    assert items[0]["quantity"] == 1
    assert items[0]["price"] == 200.00

    assert items[1]["name"] == "CaWBKH 50 MA"
    assert items[1]["quantity"] == 1
    assert items[1]["price"] == 10.00


def test_extract_real_russian_ocr_receipt_date():
    text = """
    KACCHP Akumuyk tana
    AATA 23.08.2017 BPEMA 14:13
    """

    assert extract_date(text) == "23.08.2017"


def test_extract_real_russian_ocr_receipt_total():
    assert extract_total(
        "ATOr * 260.00"
    ) == 260.00


# =========================================================
# REAL RECEIPT 2 — CAFE ODESSA
# =========================================================

def test_extract_real_french_receipt_header():
    text = """
    ï ; : —"
    CAFE ODESSA '
    * 128 RUE ODESSA.
    75014 PARIS FRANCE =
    TOTAL -” 88.80
    DIMANCHE 07-05-2020 22:42:54
    """

    data = extract_receipt_data(text)

    assert clean_item_name(data["store"]) == "CAFE ODESSA"
    assert data["receipt_date"] == "07-05-2020"
    assert data["total"] == 88.80


def test_extract_real_french_receipt_items():
    text = """
    4 SUPP COUID RESTO. “4.50 C-
    - À ENTRECOTE GRILLEE | 24.50.C.
    4 CROQUE, JEUNE FEMME’ 43.90. C”
    4 ASS. .FRITES * ° “6.50.0
    ‘A SALADE DE-FRUITS — 7,50 C”
    """

    items = extract_items(text)

    names = [item["name"] for item in items]

    assert any(
        "SUPP COUID RESTO" in name
        for name in names
    )

    assert any(
        "ENTRECOTE GRILLEE" in name
        for name in names
    )

    assert any(
        "CROQUE" in name
        for name in names
    )

    assert any(
        "FRITES" in name
        for name in names
    )

    assert any(
        "SALADE DE-FRUITS" in name
        for name in names
    )


# =========================================================
# REAL RECEIPT 3 — DEGRADED RUSSIAN OCR
# =========================================================

def test_extract_real_degraded_russian_receipt():
    text = """
    | KACOOBU VEK KOPPEKUMA
    ts … !
    | AutmActpator
    q fposaxa Kt rena K1 v
    CUNKA «5500.00
    WTOT — =6900.00
    OUATA !
    HANH =§900.00 |
    BCEO OMNAYEHO
    HASH =6500.00
    SMEKTPOTEOU 80.00
    hava Brena 20-04-17 15:49
    """

    data = extract_receipt_data(text)

    assert data["receipt_date"] == "20-04-17"
    assert data["total"] == 6900.00