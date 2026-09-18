import pytest
import pytesseract

from app.services.ocr import extract_text


def test_extract_text():
    original = pytesseract.image_to_string

    try:
        pytesseract.image_to_string = (
            lambda *args, **kwargs: "  Carrefour\nTOTAL 25,50  "
        )

        result = extract_text("fake_image.jpg")

        assert result == "Carrefour\nTOTAL 25,50"

    finally:
        pytesseract.image_to_string = original


def test_extract_text_tesseract_not_found():
    original = pytesseract.image_to_string

    try:
        def fake_ocr(*args, **kwargs):
            raise pytesseract.TesseractNotFoundError()

        pytesseract.image_to_string = fake_ocr

        with pytest.raises(
            RuntimeError,
            match="Tesseract OCR",
        ):
            extract_text("fake_image.jpg")

    finally:
        pytesseract.image_to_string = original