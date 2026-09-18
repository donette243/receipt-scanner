from fastapi.testclient import TestClient

from app.main import app
from app.routers import receipts


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_receipts():
    response = client.get("/receipts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_receipt_not_found():
    response = client.get("/receipts/999999")

    assert response.status_code == 404


def test_delete_receipt_not_found():
    response = client.delete("/receipts/999999")

    assert response.status_code == 404


def test_get_statistics():
    response = client.get("/statistics")

    assert response.status_code == 200

    data = response.json()

    assert "total_spent" in data
    assert "receipts_count" in data
    assert "categories" in data
    assert isinstance(data["categories"], list)


def test_scan_receipt_success(monkeypatch):
    monkeypatch.setattr(
        receipts,
        "_validate_image",
        lambda path: None,
    )

    monkeypatch.setattr(
        receipts,
        "preprocess_image",
        lambda path: path,
    )

    monkeypatch.setattr(
        receipts,
        "extract_text",
        lambda path: (
            "Carrefour\n"
            "Milk 2,50\n"
            "TOTAL 2,50"
        ),
    )

    monkeypatch.setattr(
        receipts,
        "categorize_items",
        lambda items: [
            {
                **item,
                "category": "food",
            }
            for item in items
        ],
    )

    monkeypatch.setattr(
        receipts,
        "categorize_with_llm",
        lambda items: items,
    )

    response = client.post(
        "/receipts/scan",
        files={
            "file": (
                "receipt.jpg",
                b"fake image content",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["original_filename"] == "receipt.jpg"
    assert data["store"] == "Carrefour"
    assert data["total"] == 2.50
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Milk"
    assert data["items"][0]["category"] == "food"


def test_scan_receipt_invalid_extension():
    response = client.post(
        "/receipts/scan",
        files={
            "file": (
                "receipt.txt",
                b"fake content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_scan_receipt_empty_file():
    response = client.post(
        "/receipts/scan",
        files={
            "file": (
                "receipt.jpg",
                b"",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400


def test_scan_receipt_no_text(monkeypatch):
    monkeypatch.setattr(
        receipts,
        "_validate_image",
        lambda path: None,
    )

    monkeypatch.setattr(
        receipts,
        "preprocess_image",
        lambda path: path,
    )

    monkeypatch.setattr(
        receipts,
        "extract_text",
        lambda path: "",
    )

    response = client.post(
        "/receipts/scan",
        files={
            "file": (
                "receipt.jpg",
                b"fake image",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 422