from app.services.categorizer import (
    categorize_item,
    categorize_items,
)


def test_food_category():
    assert categorize_item("Milk") == "food"


def test_hygiene_category():
    assert categorize_item("Shampoo") == "hygiene"


def test_electronics_category():
    assert categorize_item("Phone charger") == "electronics"


def test_transport_category():
    assert categorize_item("Metro") == "transport"


def test_unknown_category():
    assert categorize_item("Something Unknown") == "other"


def test_categorize_items():
    items = [
        {
            "name": "Milk",
            "quantity": 1,
            "price": 2.50,
        },
        {
            "name": "Shampoo",
            "quantity": 1,
            "price": 4.90,
        },
    ]

    result = categorize_items(items)

    assert result[0]["category"] == "food"
    assert result[1]["category"] == "hygiene"