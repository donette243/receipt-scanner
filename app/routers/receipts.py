from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Receipt, ReceiptItem
from ..schemas import ReceiptResponse
from ..services.categorizer import categorize_items
from ..services.extractor import extract_receipt_data
from ..services.image_processor import preprocess_image
from ..services.llm import categorize_with_llm
from ..services.ocr import extract_text


router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"],
)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def _to_decimal(
    value,
    decimals: int = 2,
) -> Decimal | None:
    if value is None:
        return None

    try:
        decimal_value = Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None

    if decimals == 3:
        return decimal_value.quantize(
            Decimal("0.001")
        )

    return decimal_value.quantize(
        Decimal("0.01")
    )


def _validate_image(
    file_path: Path,
) -> None:
    image = cv2.imread(str(file_path))

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Загруженный файл не является корректным изображением.",
        )


@router.post(
    "/scan",
    response_model=ReceiptResponse,
)
async def scan_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    original_filename = file.filename or "receipt"

    extension = (
        Path(original_filename)
        .suffix
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат. Используйте JPG, JPEG, PNG или WEBP.",
        )

    content = await file.read()

    max_size = (
        settings.MAX_FILE_SIZE_MB
        * 1024
        * 1024
    )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Файл пуст.",
        )

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                "Размер файла превышает допустимый. "
                f"Максимальный размер: {settings.MAX_FILE_SIZE_MB} МБ."
            ),
        )

    filename = f"{uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename

    processed_path: str | None = None
    scan_successful = False

    try:
        file_path.write_bytes(content)

        _validate_image(file_path)

        processed_path = preprocess_image(
            str(file_path)
        )

        raw_text = extract_text(
            processed_path
        )

        if not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Не удалось распознать текст на чеке.",
            )

        data = extract_receipt_data(
            raw_text
        )

        items = data.get(
            "items",
            [],
        )

        items = categorize_items(
            items
        )

        items = categorize_with_llm(
            items
        )

        receipt = Receipt(
            filename=filename,
            original_filename=original_filename[:255],
            store=data.get("store"),
            receipt_date=data.get(
                "receipt_date"
            ),
            total=_to_decimal(
                data.get("total")
            ),
            raw_text=raw_text,
        )

        db.add(receipt)
        db.flush()

        for item in items:
            name = str(
                item.get(
                    "name",
                    "",
                )
            ).strip()

            if not name:
                continue

            quantity = _to_decimal(
                item.get(
                    "quantity",
                    1,
                ),
                decimals=3,
            )

            if quantity is None:
                quantity = Decimal(
                    "1.000"
                )

            price = _to_decimal(
                item.get("price")
            )

            category = (
                item.get("category")
                or "other"
            )

            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                name=name[:255],
                quantity=quantity,
                price=price,
                category=str(category)[:100],
            )

            db.add(receipt_item)

        db.commit()
        db.refresh(receipt)

        scan_successful = True

        return receipt

    except HTTPException:
        db.rollback()
        raise

    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Во время обработки чека произошла внутренняя ошибка.",
        ) from exc

    finally:
        if processed_path:
            processed_file = Path(
                processed_path
            )

            if processed_file.exists():
                processed_file.unlink(
                    missing_ok=True
                )

        if (
            not scan_successful
            and file_path.exists()
        ):
            file_path.unlink(
                missing_ok=True
            )


@router.get(
    "",
    response_model=list[ReceiptResponse],
)
def get_receipts(
    db: Session = Depends(get_db),
):
    return (
        db.query(Receipt)
        .order_by(
            Receipt.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{receipt_id}",
    response_model=ReceiptResponse,
)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Чек не найден.",
        )

    return receipt


@router.delete(
    "/{receipt_id}",
)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Чек не найден.",
        )

    stored_file = (
        UPLOAD_DIR
        / receipt.filename
    )

    try:
        db.delete(receipt)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Не удалось удалить чек.",
        ) from exc

    if stored_file.exists():
        stored_file.unlink(
            missing_ok=True
        )

    return {
        "message": "Чек удалён.",
        "id": receipt_id,
    }