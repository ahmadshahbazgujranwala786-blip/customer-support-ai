from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    category: Mapped[str | None] = mapped_column(String)

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    product_metadata = mapped_column(
        "metadata",
        JSON
    )


    status: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime]

    updated_at: Mapped[datetime]

    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )