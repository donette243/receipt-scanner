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
            "Langue(s) Tesseract manquante(s) : "
            f"{missing_text}. "
            "Installe les fichiers traineddata "
            "correspondants ou modifie OCR_LANG."
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
            "Tesseract OCR n'est pas installé "
            "ou son chemin n'est pas configuré."
        ) from exc

    except pytesseract.TesseractError as exc:
        raise RuntimeError(
            "Erreur pendant l'exécution de "
            "Tesseract OCR."
        ) from exc

    return text.strip()