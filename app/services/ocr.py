import pytesseract

from ..config import settings


if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def _get_available_languages() -> set[str]:
    try:
        return set(
            pytesseract.get_languages(
                config=""
            )
        )
    except (
        pytesseract.TesseractNotFoundError,
        pytesseract.TesseractError,
    ):
        return set()


def _validate_ocr_languages() -> None:
    requested = {
        language.strip()
        for language in settings.OCR_LANG.split("+")
        if language.strip()
    }

    available = _get_available_languages()

    if not available:
        return

    missing = requested - available

    if missing:
        missing_text = ", ".join(
            sorted(missing)
        )

        raise RuntimeError(
            "Отсутствуют языковые данные Tesseract: "
            f"{missing_text}. "
            "Установите соответствующие файлы traineddata "
            "или измените OCR_LANG."
        )


def extract_text(image_path: str) -> str:
    _validate_ocr_languages()

    try:
        text = pytesseract.image_to_string(
            image_path,
            lang=settings.OCR_LANG,
            config="--oem 3 --psm 6",
        )

    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR не установлен "
            "или путь к нему не настроен."
        ) from exc

    except pytesseract.TesseractError as exc:
        raise RuntimeError(
            "Ошибка при выполнении Tesseract OCR."
        ) from exc

    return text.strip()