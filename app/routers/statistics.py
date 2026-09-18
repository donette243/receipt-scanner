from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Receipt
from ..schemas import (
    CategoryStatistic,
    StatisticsResponse,
)


router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
)


@router.get(
    "",
    response_model=StatisticsResponse,
)
def get_statistics(
    db: Session = Depends(get_db),
):
    receipts = (
        db.query(Receipt)
        .all()
    )
    total_spent = Decimal("0.00")

    category_totals = defaultdict(
        lambda: Decimal("0.00")
    )

    for receipt in receipts:
        if receipt.total is not None:
            total_spent += Decimal(
                str(receipt.total)
            )

        for item in receipt.items:
            if item.price is None:
                continue

            price = Decimal(
                str(item.price)
            )

            quantity = Decimal(
                str(
                    item.quantity
                    if item.quantity is not None
                    else 1
                )
            )

            category = (
                item.category
                or "other"
            )

            category_totals[
                category
            ] += (
                price * quantity
            )

    categories = [
        CategoryStatistic(
            category=category,
            total=float(
                total.quantize(
                    Decimal("0.01")
                )
            ),
        )
        for category, total
        in sorted(
            category_totals.items()
        )
    ]

    return StatisticsResponse(
        total_spent=float(
            total_spent.quantize(
                Decimal("0.01")
            )
        ),
        receipts_count=len(
            receipts
        ),
        categories=categories,
    )