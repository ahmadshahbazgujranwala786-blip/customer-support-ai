from datetime import datetime
from decimal import Decimal
from app.models.order import Order
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrderItem(Base):

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        default=1
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    created_at: Mapped[datetime]

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )

    product = relationship(
        "Product",
        back_populates="order_items"
    )