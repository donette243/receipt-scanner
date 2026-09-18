from datetime import UTC, datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=True,
    )

    store = Column(
        String(255),
        nullable=True,
    )

    receipt_date = Column(
        String(50),
        nullable=True,
    )

    total = Column(
        Numeric(10, 2),
        nullable=True,
    )

    raw_text = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    items = relationship(
        "ReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    receipt_id = Column(
        Integer,
        ForeignKey(
            "receipts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    quantity = Column(
        Numeric(10, 3),
        default=Decimal("1.000"),
        nullable=False,
    )

    price = Column(
        Numeric(10, 2),
        nullable=True,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    receipt = relationship(
        "Receipt",
        back_populates="items",
    )