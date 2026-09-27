from .receipt_parsing.items import (
    clean_item_name,
    extract_items,
    is_ignored_item,
)
from .receipt_parsing.numbers import normalize_number
from .receipt_parsing.receipt_info import (
    extract_date,
    extract_store,
    extract_total,
)


def extract_receipt_data(text: str) -> dict:
    return {
        "store": extract_store(text),
        "receipt_date": extract_date(text),
        "total": extract_total(text),
        "items": extract_items(text),
    }