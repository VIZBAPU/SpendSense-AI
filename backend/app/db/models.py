from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True)}


class Upload(Base):
    __tablename__ = "uploads"
    __table_args__ = (
        CheckConstraint("status IN ('categorizing', 'done', 'failed')", name="ck_uploads_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    status: Mapped[str]
    row_count: Mapped[int] = mapped_column(default=0)
    inserted_count: Mapped[int] = mapped_column(default=0)
    duplicate_count: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None]


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint("direction IN ('debit', 'credit')", name="ck_transactions_direction"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id", ondelete="CASCADE"), index=True)
    txn_date: Mapped[date] = mapped_column(index=True)
    description_raw: Mapped[str]
    merchant_normalized: Mapped[str]
    direction: Mapped[str]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str | None]
    category_source: Mapped[str | None]
    needs_review: Mapped[bool] = mapped_column(default=False)
    row_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
