from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReceiptItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    price: float | None = None
    category: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ReceiptResponse(BaseModel):
    id: int
    filename: str
    original_filename: str | None = None
    store: str | None = None
    receipt_date: str | None = None
    total: float | None = None
    raw_text: str | None = None
    created_at: datetime
    items: list[ReceiptItemResponse] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class CategoryStatistic(BaseModel):
    category: str
    total: float


class StatisticsResponse(BaseModel):
    total_spent: float
    receipts_count: int
    categories: list[CategoryStatistic]